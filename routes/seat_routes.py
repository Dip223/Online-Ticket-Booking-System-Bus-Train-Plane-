from flask import Blueprint, request, jsonify, render_template
from config import DB

seat_bp = Blueprint("seat", __name__)


def make_schedule_key(
    transport_type: str,
    source: str,
    destination: str,
    operator: str,
    journey_date: str
) -> str:
    return "|".join([
        transport_type.lower().strip(),
        source.strip(),
        destination.strip(),
        operator.strip(),
        journey_date.strip(),
    ])


def get_booked_seat_numbers(
    transport_type: str,
    source: str,
    destination: str,
    operator: str,
    journey_date: str
) -> set:
    schedule_key = make_schedule_key(
        transport_type,
        source,
        destination,
        operator,
        journey_date
    )

    bookings = DB.bookings().find({
        "schedule_key": schedule_key,
        "status": {"$ne": "CANCELLED"}
    })

    return {
        booking.get("seat_no")
        for booking in bookings
        if booking.get("seat_no")
    }


# ================= BUS: 36 SEATS =================

def generate_bus_36_seats(booked: set):
    seats = []

    # 36 seats = 9 rows × 4 seats
    # Layout: A B | aisle | C D
    for row in range(1, 10):
        for col in ["A", "B", "C", "D"]:
            seat_no = f"{col}{row}"

            seats.append({
                "seat_no": seat_no,
                "class_type": "Business" if row <= 2 else "Economy",
                "section": "Bus Cabin",
                "layout": "bus-2-2",
                "status": "booked" if seat_no in booked else "available"
            })

    return seats


# ================= TRAIN: 6 BOGIES =================

def generate_train_six_bogies(booked: set):
    seats = []

    # 6 bogies
    # Each bogie = 40 seats
    # Total train seats = 6 × 40 = 240 seats
    # Seat format: B1-A1, B1-B1, ..., B6-D10
    for bogie in range(1, 7):
        for row in range(1, 11):
            for col in ["A", "B", "C", "D"]:
                seat_no = f"B{bogie}-{col}{row}"

                seats.append({
                    "seat_no": seat_no,
                    "class_type": f"Bogie-{bogie}",
                    "section": f"Bogie {bogie}",
                    "layout": "train-2-2",
                    "status": "booked" if seat_no in booked else "available"
                })

    return seats


# ================= PLANE: BUSINESS + ECONOMY =================

def generate_plane_business_and_economy(booked: set):
    seats = []

    # Business Class
    # 4 rows × 4 seats = 16 seats
    # Layout: A B | aisle | C D
    for row in range(1, 5):
        for col in ["A", "B", "C", "D"]:
            seat_no = f"{row}{col}"

            seats.append({
                "seat_no": seat_no,
                "class_type": "Business",
                "section": "Business Class",
                "layout": "plane-business",
                "status": "booked" if seat_no in booked else "available"
            })

    # Economy Class
    # 10 rows × 6 seats = 60 seats
    # Layout: A B C | aisle | D E F
    for row in range(5, 15):
        for col in ["A", "B", "C", "D", "E", "F"]:
            seat_no = f"{row}{col}"

            seats.append({
                "seat_no": seat_no,
                "class_type": "Economy",
                "section": "Economy Class",
                "layout": "plane-economy",
                "status": "booked" if seat_no in booked else "available"
            })

    return seats


def generate_seats(transport_type: str, booked: set):
    transport_type = transport_type.lower().strip()

    if transport_type == "bus":
        return generate_bus_36_seats(booked)

    if transport_type == "train":
        return generate_train_six_bogies(booked)

    if transport_type == "plane":
        return generate_plane_business_and_economy(booked)

    return []


@seat_bp.route("/seat-select/<transport_type>")
def seat_select_page(transport_type):
    return render_template(
        "seat_selection.html",
        transport_type=transport_type.lower()
    )


@seat_bp.route("/bus-seat")
def bus_seat_page():
    return render_template("seat_selection.html", transport_type="bus")


@seat_bp.route("/train-seat")
def train_seat_page():
    return render_template("seat_selection.html", transport_type="train")


@seat_bp.route("/plane-seat")
def plane_seat_page():
    return render_template("seat_selection.html", transport_type="plane")


@seat_bp.route("/bus-payment")
def bus_payment_compat_page():
    return render_template("seat_selection.html", transport_type="bus")


@seat_bp.route("/train-payment")
def train_payment_compat_page():
    return render_template("seat_selection.html", transport_type="train")


@seat_bp.route("/plane-payment")
def plane_payment_compat_page():
    return render_template("seat_selection.html", transport_type="plane")


@seat_bp.route("/seats/<transport_type>")
def seats_api(transport_type):
    source = request.args.get("source", "")
    destination = request.args.get("destination", "")
    operator = request.args.get("operator", "")
    journey_date = request.args.get("journey_date", "")

    if not source or not destination or not operator or not journey_date:
        return jsonify({
            "message": "Missing source, destination, operator, or journey_date"
        }), 400

    booked = get_booked_seat_numbers(
        transport_type,
        source,
        destination,
        operator,
        journey_date
    )

    seats = generate_seats(transport_type, booked)

    return jsonify({
        "transport_type": transport_type,
        "booked_count": len(booked),
        "seats": seats
    })