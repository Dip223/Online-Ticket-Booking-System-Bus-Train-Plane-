from flask import Blueprint, request, jsonify
from config import DB
from models.ticket_factory import TicketFactory
from models.payment_strategy import PaymentContext, PaymentStrategyFactory
from models.routes_data import get_price, get_all_operators_with_schedules
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity

booking = Blueprint("booking", __name__)


# ================= OPERATOR SCHEDULES API =================

@booking.route('/operators/<transport>/schedules', methods=['GET'])
def get_operator_schedules(transport):
    """Get all operators with schedules for a transport type"""
    operators = get_all_operators_with_schedules(transport)
    return jsonify(operators)


# ================= BOOK TICKET =================
@booking.route("/book", methods=["POST"])
@jwt_required()
def book_ticket():
    try:
        data = request.json
        user_id = get_jwt_identity()

        # Validate required fields
        required = ["type", "source", "destination", "operator", "payment"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"message": f"Missing fields: {missing} ❌"}), 400

        # Get price from master data (single source of truth)
        price = get_price(data["type"], data["source"], data["destination"])
        
        if price is None:
            return jsonify({"message": "Invalid route selected ❌"}), 400

        # ── FACTORY PATTERN ──────────────────────────────────────────────────
        ticket = TicketFactory.create_ticket(
            transport_type=data["type"],
            source=data["source"],
            destination=data["destination"],
            price=price
        )

        # ── STRATEGY PATTERN ─────────────────────────────────────────────────
        payer_info = {
            "phone": data.get("phone", ""),
            "card_number": data.get("card_number", ""),
        }
        strategy = PaymentStrategyFactory.get_strategy(data["payment"])
        context = PaymentContext(strategy)
        receipt = context.execute_payment(ticket.price, payer_info)

        # ── Save to DB ────────────────────────────────────────────────────────
        booking_doc = {
            "user_id": user_id,
            "ticket": ticket.to_dict(),
            "operator": data["operator"],
            "payment": receipt.to_dict(),
            "journey_date": data.get("journey_date", datetime.now().isoformat()),
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat(),
        }
        DB.bookings().insert_one(booking_doc)

        # ── Save notification for user ────────────────────────────────────────
        DB.notifications().insert_one({
            "user_id": user_id,
            "message": f"Booking confirmed! {ticket.type} ticket: {ticket.source} → {ticket.destination} (৳{ticket.price})",
            "type": "booking",
            "read": False,
            "created_at": datetime.utcnow().isoformat(),
        })

        return jsonify({
            "message": "Booking Successful ✅",
            "ticket": ticket.to_dict(),
            "payment": receipt.to_dict(),
            "operator": data["operator"],
        })

    except KeyError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# ================= GET USER BOOKINGS =================
@booking.route("/my-bookings", methods=["GET"])
@jwt_required()
def my_bookings():
    try:
        user_id = get_jwt_identity()
        bookings = list(DB.bookings().find({"user_id": user_id}).sort("booked_at", -1))

        for b in bookings:
            b["_id"] = str(b["_id"])

        return jsonify(bookings)

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ================= GET NOTIFICATIONS =================
@booking.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        notifications = list(DB.notifications().find({"user_id": user_id}).sort("created_at", -1))

        for n in notifications:
            n["_id"] = str(n["_id"])

        return jsonify({
            "notifications": notifications,
            "unread_count": sum(1 for n in notifications if not n.get("read", False))
        })

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ================= MARK NOTIFICATION AS READ =================
@booking.route("/notifications/mark-read", methods=["POST"])
@jwt_required()
def mark_notification_read():
    try:
        user_id = get_jwt_identity()
        data = request.json
        notification_id = data.get("notification_id")

        from bson import ObjectId
        DB.notifications().update_one(
            {"_id": ObjectId(notification_id), "user_id": user_id},
            {"$set": {"read": True}}
        )

        return jsonify({"message": "Marked as read ✅"})

    except Exception as e:
        return jsonify({"message": str(e)}), 500