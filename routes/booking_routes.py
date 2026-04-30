from flask import Blueprint, request, jsonify
from config import DB
from models.ticket_factory   import TicketFactory
from models.payment_strategy import PaymentContext, PaymentStrategyFactory
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity

booking = Blueprint("booking", __name__)


# ── Book ticket ───────────────────────────────────────────────────────────────

@booking.route("/book", methods=["POST"])
@jwt_required()
def book_ticket():
    try:
        data    = request.json
        user_id = get_jwt_identity()   # secure — from JWT, not frontend

        # Validate required fields
        required = ["type", "source", "destination", "price", "payment", "operator"]
        missing  = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"message": f"Missing fields: {missing} ❌"}), 400

        # ── FACTORY PATTERN ──────────────────────────────────────────────────
        # Delegates creation to TicketFactory registry — no if/else here
        ticket = TicketFactory.create_ticket(
            transport_type = data["type"],
            source         = data["source"],
            destination    = data["destination"],
            price          = int(float(data["price"])),
        )

        # ── STRATEGY PATTERN ─────────────────────────────────────────────────
        # PaymentStrategyFactory picks the right strategy from registry
        payer_info = {
            "phone":       data.get("phone", ""),
            "card_number": data.get("card_number", ""),
        }
        strategy = PaymentStrategyFactory.get_strategy(data["payment"])
        context  = PaymentContext(strategy)
        receipt  = context.execute_payment(ticket.price, payer_info)

        # ── Save to DB ────────────────────────────────────────────────────────
        booking_doc = {
            "user_id":    user_id,
            "ticket":     ticket.to_dict(),
            "operator":   data["operator"],
            "payment":    receipt.to_dict(),
            "status":     "CONFIRMED",
            "booked_at":  datetime.utcnow().isoformat(),
        }
        DB.bookings().insert_one(booking_doc)

        # Save notification for user
        DB.notifications().insert_one({
            "user_id":    user_id,
            "message":    f"Booking confirmed! {ticket.type} ticket: {ticket.source} → {ticket.destination} (৳{ticket.price})",
            "type":       "booking",
            "read":       False,
            "created_at": datetime.utcnow().isoformat(),
        })

        return jsonify({
            "message": "Booking Successful ✅",
            "ticket":  ticket.to_dict(),
            "payment": receipt.to_dict(),
            "operator": data["operator"],
        })

    except KeyError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# ── My bookings ───────────────────────────────────────────────────────────────

@booking.route("/my-bookings", methods=["GET"])
@jwt_required()
def my_bookings():
    try:
        user_id  = get_jwt_identity()
        all_docs = list(DB.bookings().find({"user_id": user_id}))
        for b in all_docs:
            b["_id"] = str(b["_id"])
        return jsonify(all_docs)
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ── My notifications ──────────────────────────────────────────────────────────

@booking.route("/my-notifications", methods=["GET"])
@jwt_required()
def my_notifications():
    try:
        user_id = get_jwt_identity()
        notes   = list(DB.notifications().find({"user_id": user_id}))
        for n in notes:
            n["_id"] = str(n["_id"])
        return jsonify(notes)
    except Exception as e:
        return jsonify({"message": str(e)}), 500