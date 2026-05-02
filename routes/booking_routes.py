from flask import Blueprint, request, jsonify, render_template
from config import DB

from models.ticket_factory import TicketFactory
from models.routes_data import (
    get_price,
    get_all_operators_with_schedules,
    get_all_schedules_as_list
)
from models.ticket_builder import TicketDirector, get_ticket_builder
from models.payment_strategy import PaymentContext, PaymentStrategyFactory

from routes.seat_routes import make_schedule_key, get_booked_seat_numbers

from datetime import datetime
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity


booking = Blueprint("booking", __name__)


# ================= OPERATOR SCHEDULES API =================

@booking.route("/operators/<transport>/schedules", methods=["GET"])
def get_operator_schedules(transport):
    operators = get_all_operators_with_schedules(transport)
    return jsonify(operators)


# ================= ALL SCHEDULES API =================

@booking.route("/schedules/<transport>", methods=["GET"])
def get_all_schedules(transport):
    schedules = get_all_schedules_as_list(transport)
    return jsonify(schedules)


# ================= FINAL TICKET VIEW PAGE =================

@booking.route("/ticket-view", methods=["GET"])
def ticket_view_page():
    return render_template("ticket_view.html")


# ================= BOOK TICKET WITH PAYMENT =================

@booking.route("/book", methods=["POST"])
@jwt_required()
def book_ticket():
    try:
        data = request.json or {}
        user_id = get_jwt_identity()

        required = [
            "type",
            "source",
            "destination",
            "operator",
            "journey_date",
            "seat_no",
            "seat_class"
        ]

        missing = [field for field in required if not data.get(field)]

        if missing:
            return jsonify({
                "message": f"Missing fields: {missing} ❌"
            }), 400

        payment_method = data.get("payment_method") or data.get("payment")

        if not payment_method:
            return jsonify({
                "message": "Missing payment method ❌"
            }), 400

        transport_type = data["type"]
        source = data["source"]
        destination = data["destination"]
        operator = data["operator"]
        journey_date = data["journey_date"]
        seat_no = data["seat_no"]
        seat_class = data["seat_class"]

        # Get price from master route data
        price = get_price(transport_type, source, destination)

        if price is None:
            try:
                price = int(data.get("price", 0))
            except Exception:
                price = 0

        if price <= 0:
            return jsonify({
                "message": "Invalid route or price selected ❌"
            }), 400

        # Check if seat is already booked
        booked_seats = get_booked_seat_numbers(
            transport_type,
            source,
            destination,
            operator,
            journey_date
        )

        if seat_no in booked_seats:
            return jsonify({
                "message": f"Seat {seat_no} is already booked ❌"
            }), 409

        # Factory Pattern: Create ticket object
        ticket = TicketFactory.create_ticket(
            transport_type=transport_type,
            source=source,
            destination=destination,
            price=price
        )

        # Strategy Pattern: Payment processing
        payer_info = {
            "phone": data.get("phone", ""),
            "pin": data.get("pin", ""),
            "card_number": data.get("card_number", ""),
            "card_holder": data.get("card_holder", ""),
            "expiry": data.get("expiry", ""),
            "cvv": data.get("cvv", ""),
        }

        try:
            payment_strategy = PaymentStrategyFactory.get_strategy(payment_method)
            payment_context = PaymentContext(payment_strategy)
            receipt = payment_context.execute_payment(price, payer_info)

        except ValueError as payment_error:
            return jsonify({
                "message": f"Payment failed: {str(payment_error)} ❌"
            }), 400

        schedule_key = make_schedule_key(
            transport_type,
            source,
            destination,
            operator,
            journey_date
        )

        seat_layout = {
            "bus": "36 seats bus layout",
            "train": "6 bogies train layout",
            "plane": "Business + Economy class layout",
        }.get(str(transport_type).lower(), "Seat layout")

        booking_doc = {
            "user_id": user_id,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "journey_date": journey_date,
            "departure_time": data.get("departure_time", "Selected schedule"),
            "arrival_time": data.get("arrival_time", ""),
            "seat_no": seat_no,
            "seat_class": seat_class,
            "seat_layout": seat_layout,
            "schedule_key": schedule_key,
            "payment": receipt.to_dict(),
            "payment_status": receipt.status,
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat(),
        }

        result = DB.bookings().insert_one(booking_doc)
        booking_id = str(result.inserted_id)

        DB.notifications().insert_one({
            "user_id": user_id,
            "message": (
                f"Booking confirmed! {ticket.type} ticket: "
                f"{ticket.source} → {ticket.destination}, "
                f"Seat {seat_no}, Payment: {receipt.method}"
            ),
            "type": "booking",
            "read": False,
            "created_at": datetime.utcnow().isoformat(),
        })

        return jsonify({
            "message": "Booking Successful ✅",
            "booking_id": booking_id,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "departure_time": data.get("departure_time", ""),
            "arrival_time": data.get("arrival_time", ""),
            "seat_no": seat_no,
            "seat_class": seat_class,
            "payment": receipt.to_dict(),
            "redirect_url": f"/ticket-view?id={booking_id}",
        })

    except KeyError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "message": f"Error: {str(e)}"
        }), 500


# ================= BUILDER PATTERN: FINAL TICKET DATA =================

@booking.route("/ticket-data/<booking_id>", methods=["GET"])
@jwt_required()
def get_ticket_data(booking_id):
    try:
        user_id = get_jwt_identity()

        booking_doc = DB.bookings().find_one({
            "_id": ObjectId(booking_id),
            "user_id": user_id
        })

        if not booking_doc:
            return jsonify({
                "message": "Ticket not found or access denied ❌"
            }), 404

        booking_doc["_id"] = str(booking_doc["_id"])

        try:
            user_doc = DB.users().find_one({
                "_id": ObjectId(user_id)
            }) or {}
        except Exception:
            user_doc = {}

        transport_type = booking_doc.get("ticket", {}).get("type", "")

        builder = get_ticket_builder(transport_type)

        director = TicketDirector()
        director.set_builder_type(builder)

        final_ticket = director.construct_ticket(booking_doc, user_doc)

        return jsonify({
            "message": "Ticket generated using Builder Pattern ✅",
            "ticket_view": final_ticket.to_dict()
        })

    except Exception as e:
        return jsonify({
            "message": f"Error generating ticket: {str(e)}"
        }), 500


# ================= GET USER BOOKINGS =================

@booking.route("/my-bookings", methods=["GET"])
@jwt_required()
def my_bookings():
    try:
        user_id = get_jwt_identity()

        bookings = list(
            DB.bookings()
            .find({"user_id": user_id})
            .sort("booked_at", -1)
        )

        for item in bookings:
            item["_id"] = str(item["_id"])

        return jsonify(bookings)

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


# ================= GET NOTIFICATIONS =================

@booking.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()

        notifications = list(
            DB.notifications()
            .find({"user_id": user_id})
            .sort("created_at", -1)
        )

        for item in notifications:
            item["_id"] = str(item["_id"])

        unread_count = sum(
            1 for item in notifications
            if not item.get("read", False)
        )

        return jsonify({
            "notifications": notifications,
            "unread_count": unread_count
        })

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


# ================= MARK NOTIFICATION AS READ =================

@booking.route("/notifications/mark-read", methods=["POST"])
@jwt_required()
def mark_notification_read():
    try:
        user_id = get_jwt_identity()
        data = request.json or {}

        notification_id = data.get("notification_id")

        if not notification_id:
            return jsonify({
                "message": "Notification ID is required ❌"
            }), 400

        DB.notifications().update_one(
            {
                "_id": ObjectId(notification_id),
                "user_id": user_id
            },
            {
                "$set": {
                    "read": True
                }
            }
        )

        return jsonify({
            "message": "Marked as read ✅"
        })

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500