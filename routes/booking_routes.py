from flask import Blueprint, request, jsonify
from config import DB
from models.ticket_factory import TicketFactory
from models.payment_strategy import BkashPayment, CardPayment, PaymentContext

booking = Blueprint("booking", __name__)

# ================= BOOK TICKET =================
@booking.route('/book', methods=['POST'])
def book_ticket():
    try:
        data = request.json

        # ===== VALIDATION =====
        required_fields = ["type", "source", "destination", "price", "payment"]
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"{field} is required ❌"}), 400

        # ===== 1. FACTORY PATTERN =====
        ticket = TicketFactory.create_ticket(
            data['type'],
            data['source'],
            data['destination'],
            int(data['price'])
        )

        # ===== 2. STRATEGY PATTERN =====
        if data['payment'].lower() == "bkash":
            payment = PaymentContext(BkashPayment())
        else:
            payment = PaymentContext(CardPayment())

        payment_result = payment.execute(ticket.price)

        # ===== 3. SAVE TO DATABASE =====
        db = DB.get_db()

        booking_data = {
            "user_id": data.get("user_id"),
            "ticket": ticket.to_dict(),
            "payment": payment_result
        }

        db.bookings.insert_one(booking_data)

        # ===== 4. RESPONSE =====
        return jsonify({
            "message": "Booking Successful ✅",
            "ticket": ticket.to_dict(),
            "operator": data.get("operator"),
            "payment": payment_result
        })

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ================= GET USER BOOKINGS =================
@booking.route('/my-bookings', methods=['GET'])
def my_bookings():
    try:
        db = DB.get_db()

        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"message": "user_id required ❌"}), 400

        bookings = list(db.bookings.find({"user_id": user_id}))

        # Convert ObjectId to string
        for b in bookings:
            b['_id'] = str(b['_id'])

        return jsonify(bookings)

    except Exception as e:
        return jsonify({"message": str(e)}), 500