from flask import Blueprint, request, jsonify
from config import DB
from models.ticket_factory import TicketFactory
from models.payment_strategy import BkashPayment, CardPayment, PaymentContext

# 🔐 JWT
from flask_jwt_extended import jwt_required, get_jwt_identity

booking = Blueprint("booking", __name__)


# ================= BOOK TICKET =================
@booking.route('/book', methods=['POST'])
@jwt_required()  # ✅ secure endpoint
def book_ticket():
    try:
        data = request.json

        # ===== GET USER FROM JWT =====
        user_id = get_jwt_identity()

        # ===== VALIDATION =====
        required_fields = ["type", "source", "destination", "price", "payment", "operator"]
        for field in required_fields:
            if field not in data or not data[field]:
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
            "user_id": user_id,  # ✅ from JWT (secure)
            "ticket": ticket.to_dict(),
            "operator": data.get("operator"),
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
@jwt_required()  # ✅ secure endpoint
def my_bookings():
    try:
        db = DB.get_db()

        # ===== GET USER FROM JWT =====
        user_id = get_jwt_identity()

        bookings = list(db.bookings.find({"user_id": user_id}))

        # Convert ObjectId → string
        for b in bookings:
            b['_id'] = str(b['_id'])

        return jsonify(bookings)

    except Exception as e:
        return jsonify({"message": str(e)}), 500