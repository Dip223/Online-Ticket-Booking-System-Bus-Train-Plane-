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
from models.observer import booking_subject  # ← IMPORT THE OBSERVER

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


# ================= BOOK TICKET WITH OBSERVER PATTERN =================

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
        departure_time = data.get("departure_time", "Selected schedule")
        arrival_time = data.get("arrival_time", "")

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

        # Get user details for notification
        user_doc = DB.users().find_one({"_id": ObjectId(user_id)}) or {}
        user_name = user_doc.get("name", "User")
        user_email = user_doc.get("email", "")

        # Save to database
        booking_doc = {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "journey_date": journey_date,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "seat_no": seat_no,
            "seat_class": seat_class,
            "seat_layout": seat_layout,
            "schedule_key": schedule_key,
            "payment": receipt.to_dict(),
            "payment_status": receipt.status,
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat(),
            "decorators": [],  # ← ADDED: initialize empty decorators list
        }

        result = DB.bookings().insert_one(booking_doc)
        booking_id = str(result.inserted_id)

        # ============================================================
        # OBSERVER PATTERN - Send notifications to all observers
        # ============================================================
        notification_data = {
            "booking_id": booking_id,
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "payment": receipt.method,
            "seat_no": seat_no,
            "journey_date": journey_date,
            "departure_time": departure_time
        }
        
        # This will trigger ALL attached observers (WebsiteNotificationObserver)
        booking_subject.notify(notification_data)
        
        print(f"✅ Booking {booking_id} completed. Observer notified.")

        return jsonify({
            "message": "Booking Successful ✅",
            "booking_id": booking_id,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
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

        result = DB.notifications().update_one(
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

        if result.modified_count > 0:
            return jsonify({
                "message": "Marked as read ✅"
            })
        else:
            return jsonify({
                "message": "Notification not found or already read"
            }), 404

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


# ================= MARK ALL NOTIFICATIONS AS READ =================

@booking.route("/notifications/mark-all-read", methods=["POST"])
@jwt_required()
def mark_all_notifications_read():
    try:
        user_id = get_jwt_identity()
        
        result = DB.notifications().update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
        
        return jsonify({
            "message": f"{result.modified_count} notifications marked as read ✅",
            "count": result.modified_count
        })
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ================= DECORATOR PATTERN ENDPOINTS =================

@booking.route("/decorator/addons", methods=["POST"])
@jwt_required()
def add_decorators_to_ticket():
    """
    Demonstrate Decorator Pattern with transport-specific features
    Like adding condiments and sides to a sandwich
    
    Features:
    - Plane: Insurance (300), Priority Boarding (300), Lounge Access (400)
    - Train: Insurance (50)
    - Bus: Insurance (50), Hanif Voucher (10% off)
    - Common: Extra Luggage (200), Meal (150)
    - Base: Basic or Premium ticket
    """
    try:
        from models.base_ticket import BaseTicket, PremiumTicket
        from models.transport_decorator import (
            ExtraLuggageDecorator, MealDecorator, InsuranceDecorator,
            PriorityBoardingDecorator, LoungeAccessDecorator, HanifVoucherDecorator
        )
        
        data = request.json
        booking_id = data.get("booking_id")
        addons = data.get("addons", [])  # ['luggage', 'meal', 'insurance', 'priority', 'lounge', 'voucher']
        premium = data.get("premium", False)
        voucher_code = data.get("voucher_code", "HANIF10")
        
        user_id = get_jwt_identity()
        
        # Get booking from database
        booking = DB.bookings().find_one({
            "_id": ObjectId(booking_id),
            "user_id": user_id
        })
        
        if not booking:
            return jsonify({"message": "Booking not found ❌"}), 404
        
        # Create Ticket object from booking data
        ticket_data = booking.get("ticket", {})
        operator = booking.get("operator", "")
        
        ticket = TicketFactory.create_ticket(
            transport_type=ticket_data.get("type", ""),
            source=ticket_data.get("source", ""),
            destination=ticket_data.get("destination", ""),
            price=ticket_data.get("price", 0)
        )
        
        # Attach operator to ticket for decorator access
        ticket.operator = operator
        
        transport = ticket.type.lower()
        
        # ============= DECORATOR PATTERN IN ACTION =============
        # Like in main.cpp:
        # SandwichOrder *sandwich1 = new DeluxeSandwich;
        # SandwichOrder *decorated1 = new CondimentDecorator("mayo", sandwich1);
        
        # Step 1: Choose base component (Basic or Premium)
        if premium:
            ticket_component = PremiumTicket(ticket)
        else:
            ticket_component = BaseTicket(ticket)
        
        original_cost = ticket_component.get_cost()
        applied_addons = []
        errors = []
        
        # Step 2: Apply decorators (like adding condiments and sides)
        for addon in addons:
            addon = addon.lower()
            
            try:
                if addon == "luggage":
                    ticket_component = ExtraLuggageDecorator(ticket_component)
                    applied_addons.append("Extra Luggage (+200 BDT)")
                
                elif addon == "meal":
                    ticket_component = MealDecorator(ticket_component)
                    applied_addons.append("Meal (+150 BDT)")
                
                elif addon == "insurance":
                    ticket_component = InsuranceDecorator(ticket_component)
                    applied_addons.append("Travel Insurance")
                
                elif addon == "priority" and transport == "plane":
                    ticket_component = PriorityBoardingDecorator(ticket_component)
                    applied_addons.append("Priority Boarding (+300 BDT)")
                
                elif addon == "lounge" and transport == "plane":
                    ticket_component = LoungeAccessDecorator(ticket_component)
                    applied_addons.append("VIP Lounge Access (+400 BDT)")
                
                elif addon == "voucher" and transport == "bus":
                    ticket_component = HanifVoucherDecorator(ticket_component, voucher_code)
                    applied_addons.append(f"Hanif Voucher ({voucher_code}) - 10% off")
                
                elif addon == "voucher" and transport != "bus":
                    errors.append(f"Voucher is only available for BUS, not for {transport.upper()}")
                
                elif addon == "priority" and transport != "plane":
                    errors.append(f"Priority Boarding is only available for PLANE, not for {transport.upper()}")
                
                elif addon == "lounge" and transport != "plane":
                    errors.append(f"Lounge Access is only available for PLANE, not for {transport.upper()}")
                
                else:
                    errors.append(f"'{addon}' is not available for {transport.upper()}")
                    
            except ValueError as e:
                errors.append(str(e))
        
        # ============= SAVE DECORATORS TO DATABASE =============
        # Save decorators to booking document for ticket view
        decorator_features = ticket_component.get_features()
        
        DB.bookings().update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "decorators": decorator_features,
                "decorator_total": ticket_component.get_cost(),
                "decorator_description": ticket_component.get_description(),
                "premium_applied": premium,
                "addons_applied": addons
            }}
        )
        
        # Step 3: Get final result
        return jsonify({
            "message": "Decorator Pattern Demo ✅",
            "transport_type": transport.upper(),
            "operator": operator,
            "base_type": "PREMIUM" if premium else "BASIC",
            "original_cost": original_cost,
            "total_addon_cost": ticket_component.get_cost() - original_cost,
            "total_cost": ticket_component.get_cost(),
            "applied_addons": applied_addons,
            "errors": errors if errors else None,
            "description": ticket_component.get_description(),
            "features": ticket_component.get_features()
        })
        
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@booking.route("/decorator/available-addons", methods=["GET"])
def get_available_addons():
    """Returns available add-ons for each transport type"""
    return jsonify({
        "common_addons": [
            {"id": "luggage", "name": "Extra Luggage", "price": 200, "description": "+10kg luggage allowance"},
            {"id": "meal", "name": "Complimentary Meal", "price": 150, "description": "Hot meal included"}
        ],
        "plane_addons": [
            {"id": "insurance", "name": "Travel Insurance", "price": 300, "description": "Flight cancellation + medical"},
            {"id": "priority", "name": "Priority Boarding", "price": 300, "description": "Skip the queue"},
            {"id": "lounge", "name": "VIP Lounge Access", "price": 400, "description": "Airport lounge access"}
        ],
        "train_addons": [
            {"id": "insurance", "name": "Travel Insurance", "price": 50, "description": "Journey protection"}
        ],
        "bus_addons": [
            {"id": "insurance", "name": "Travel Insurance", "price": 50, "description": "Trip protection"},
            {"id": "voucher", "name": "Hanif Voucher", "price": "10% off", "description": "10% discount for Hanif Transport only", "voucher_code": "HANIF10"}
        ],
        "ticket_types": [
            {"id": "basic", "name": "Basic Ticket", "extra_cost": 0, "description": "Standard ticket"},
            {"id": "premium", "name": "Premium Ticket", "extra_cost": "Bus:300, Train:400, Plane:800", "description": "Premium seat + Extra legroom"}
        ]
    })