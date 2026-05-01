"""
setup_ticket_seat_builder_no_payment.py

Run this file inside your Flask project root folder:

    python setup_ticket_seat_builder_no_payment.py

It creates/updates:
- models/ticket_builder.py
- routes/seat_routes.py
- routes/booking_routes.py
- templates/seat_selection.html
- templates/ticket_view.html
- static/seat_ticket.css
- app_with_seat_example.py

Payment is not included.
Ticket part uses Builder Design Pattern.
Seat part uses UI only.
Bus = 36 seats.
Train = one bogie.
Plane = economy class.
"""

from pathlib import Path

FILES = {}

FILES["models/ticket_builder.py"] = r'''
from abc import ABC, abstractmethod
from datetime import datetime


class TicketView:
    def __init__(self):
        self.ticket_id = ""
        self.title = ""
        self.subtitle = ""
        self.transport_type = ""
        self.theme = ""
        self.icon = ""
        self.route_line = ""
        self.status = "CONFIRMED"
        self.issue_time = ""
        self.footer_note = ""
        self.ticket_code = ""
        self.sections = []

    def add_section(self, title: str, rows: dict):
        self.sections.append({"title": title, "rows": rows})

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "transport_type": self.transport_type,
            "theme": self.theme,
            "icon": self.icon,
            "route_line": self.route_line,
            "status": self.status,
            "issue_time": self.issue_time,
            "footer_note": self.footer_note,
            "ticket_code": self.ticket_code,
            "sections": self.sections,
        }


class TicketBuilder(ABC):
    def __init__(self):
        self.product = TicketView()

    def reset(self):
        self.product = TicketView()

    @abstractmethod
    def add_header(self, booking_doc: dict, user_doc: dict):
        pass

    def add_passenger_info(self, booking_doc: dict, user_doc: dict):
        self.product.add_section("Passenger Information", {
            "Passenger Name": user_doc.get("name", "Passenger"),
            "Email": user_doc.get("email", "N/A"),
            "User ID": str(booking_doc.get("user_id", "N/A")),
        })

    def add_journey_info(self, booking_doc: dict, user_doc: dict):
        ticket = booking_doc.get("ticket", {})
        source = ticket.get("source", "N/A")
        destination = ticket.get("destination", "N/A")
        self.product.route_line = f"{source} → {destination}"
        self.product.add_section("Journey Information", {
            "From": source,
            "To": destination,
            "Journey Date": booking_doc.get("journey_date", "N/A"),
            "Departure Time": booking_doc.get("departure_time", "N/A"),
            "Operator": booking_doc.get("operator", "N/A"),
        })

    def add_seat_info(self, booking_doc: dict, user_doc: dict):
        self.product.add_section("Seat Information", {
            "Selected Seat": booking_doc.get("seat_no", "N/A"),
            "Seat Class": booking_doc.get("seat_class", "N/A"),
            "Layout": booking_doc.get("seat_layout", "N/A"),
        })

    def add_fare_info(self, booking_doc: dict, user_doc: dict):
        ticket = booking_doc.get("ticket", {})
        self.product.add_section("Fare Information", {
            "Ticket Fare": f"৳{ticket.get('price', 0)}",
            "Payment": "Not included in this module",
        })

    @abstractmethod
    def add_transport_specific_info(self, booking_doc: dict, user_doc: dict):
        pass

    @abstractmethod
    def add_ticket_style(self):
        pass

    def add_footer(self, booking_doc: dict, user_doc: dict):
        self.product.issue_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.product.ticket_code = self.product.ticket_id

    def return_product(self):
        final_ticket = self.product
        self.reset()
        return final_ticket


class BusTicketBuilder(TicketBuilder):
    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()
        self.product.ticket_id = f"BUS-{booking_id}"
        self.product.title = "BUS E-TICKET"
        self.product.subtitle = "36 Seat Bus Ticket Confirmation"
        self.product.transport_type = "Bus"
        self.product.icon = "fa-bus"

    def add_transport_specific_info(self, booking_doc, user_doc):
        self.product.add_section("Bus Details", {
            "Bus Operator": booking_doc.get("operator", "N/A"),
            "Seat Layout": "36 seats, 2 × 2 layout",
            "Boarding Point": booking_doc.get("boarding_point", "Main Counter"),
            "Reporting Time": "30 minutes before departure",
        })

    def add_ticket_style(self):
        self.product.theme = "bus"
        self.product.footer_note = "Please arrive at the bus counter at least 30 minutes before departure."


class TrainTicketBuilder(TicketBuilder):
    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()
        self.product.ticket_id = f"TRN-{booking_id}"
        self.product.title = "TRAIN E-TICKET"
        self.product.subtitle = "One Bogie Train Ticket Confirmation"
        self.product.transport_type = "Train"
        self.product.icon = "fa-train"

    def add_transport_specific_info(self, booking_doc, user_doc):
        self.product.add_section("Train Details", {
            "Train Name": booking_doc.get("operator", "N/A"),
            "Bogie": "Bogie 1",
            "Coach Type": booking_doc.get("seat_class", "Bogie-1"),
            "ID Requirement": "Carry a valid ID card",
        })

    def add_ticket_style(self):
        self.product.theme = "train"
        self.product.footer_note = "Carry a valid ID card during the train journey."


class PlaneTicketBuilder(TicketBuilder):
    def add_header(self, booking_doc, user_doc):
        booking_id = str(booking_doc.get("_id", ""))[-8:].upper()
        self.product.ticket_id = f"AIR-{booking_id}"
        self.product.title = "PLANE E-TICKET"
        self.product.subtitle = "Economy Class Flight Ticket Confirmation"
        self.product.transport_type = "Plane"
        self.product.icon = "fa-plane"

    def add_transport_specific_info(self, booking_doc, user_doc):
        self.product.add_section("Flight Details", {
            "Airline": booking_doc.get("operator", "N/A"),
            "Class": "Economy",
            "Gate": booking_doc.get("gate_no", "Gate 1"),
            "Check-in": "Closes 45 minutes before departure",
        })

    def add_ticket_style(self):
        self.product.theme = "plane"
        self.product.footer_note = "Check-in closes 45 minutes before flight departure."


class TicketDirector:
    def __init__(self):
        self.builder = None

    def set_builder_type(self, builder):
        self.builder = builder

    def construct_ticket(self, booking_doc, user_doc):
        if self.builder is None:
            raise ValueError("Ticket builder is not selected.")

        self.builder.reset()
        self.builder.add_header(booking_doc, user_doc)
        self.builder.add_passenger_info(booking_doc, user_doc)
        self.builder.add_journey_info(booking_doc, user_doc)
        self.builder.add_seat_info(booking_doc, user_doc)
        self.builder.add_fare_info(booking_doc, user_doc)
        self.builder.add_transport_specific_info(booking_doc, user_doc)
        self.builder.add_ticket_style()
        self.builder.add_footer(booking_doc, user_doc)
        return self.builder.return_product()


def get_ticket_builder(transport_type: str):
    builders = {
        "bus": BusTicketBuilder,
        "train": TrainTicketBuilder,
        "plane": PlaneTicketBuilder,
    }
    builder_class = builders.get(str(transport_type).lower().strip())
    if builder_class is None:
        raise KeyError(f"No ticket builder found for type: {transport_type}")
    return builder_class()
'''

FILES["routes/seat_routes.py"] = r'''
from flask import Blueprint, request, jsonify, render_template
from config import DB

seat_bp = Blueprint("seat", __name__)


def make_schedule_key(transport_type: str, source: str, destination: str, operator: str, journey_date: str) -> str:
    return "|".join([
        transport_type.lower().strip(),
        source.strip(),
        destination.strip(),
        operator.strip(),
        journey_date.strip(),
    ])


def get_booked_seat_numbers(transport_type: str, source: str, destination: str, operator: str, journey_date: str) -> set:
    schedule_key = make_schedule_key(transport_type, source, destination, operator, journey_date)
    bookings = DB.bookings().find({"schedule_key": schedule_key, "status": {"$ne": "CANCELLED"}})
    return {b.get("seat_no") for b in bookings if b.get("seat_no")}


def generate_bus_36_seats(booked: set):
    seats = []
    for row in range(1, 10):
        for col in ["A", "B", "C", "D"]:
            seat_no = f"{col}{row}"
            seats.append({
                "seat_no": seat_no,
                "class_type": "Business" if row <= 2 else "Economy",
                "status": "booked" if seat_no in booked else "available"
            })
    return seats


def generate_train_one_bogie(booked: set):
    seats = []
    for row in range(1, 11):
        for col in ["A", "B", "C", "D"]:
            seat_no = f"B1-{col}{row}"
            seats.append({
                "seat_no": seat_no,
                "class_type": "Bogie-1",
                "status": "booked" if seat_no in booked else "available"
            })
    return seats


def generate_plane_economy(booked: set):
    seats = []
    for row in range(1, 11):
        for col in ["A", "B", "C", "D", "E", "F"]:
            seat_no = f"{row}{col}"
            seats.append({
                "seat_no": seat_no,
                "class_type": "Economy",
                "status": "booked" if seat_no in booked else "available"
            })
    return seats


def generate_seats(transport_type: str, booked: set):
    t = transport_type.lower().strip()
    if t == "bus":
        return generate_bus_36_seats(booked)
    if t == "train":
        return generate_train_one_bogie(booked)
    if t == "plane":
        return generate_plane_economy(booked)
    return []


@seat_bp.route("/seat-select/<transport_type>")
def seat_select_page(transport_type):
    return render_template("seat_selection.html", transport_type=transport_type.lower())


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
        return jsonify({"message": "Missing source, destination, operator, or journey_date"}), 400

    booked = get_booked_seat_numbers(transport_type, source, destination, operator, journey_date)
    seats = generate_seats(transport_type, booked)
    return jsonify({"transport_type": transport_type, "booked_count": len(booked), "seats": seats})
'''

FILES["routes/booking_routes.py"] = r'''
from flask import Blueprint, request, jsonify, render_template
from config import DB
from models.ticket_factory import TicketFactory
from models.routes_data import get_price, get_all_operators_with_schedules
from models.ticket_builder import TicketDirector, get_ticket_builder
from routes.seat_routes import make_schedule_key, get_booked_seat_numbers
from datetime import datetime
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity

booking = Blueprint("booking", __name__)


@booking.route('/operators/<transport>/schedules', methods=['GET'])
def get_operator_schedules(transport):
    operators = get_all_operators_with_schedules(transport)
    return jsonify(operators)


@booking.route("/ticket-view", methods=["GET"])
def ticket_view_page():
    return render_template("ticket_view.html")


@booking.route("/book", methods=["POST"])
@jwt_required()
def book_ticket():
    try:
        data = request.json or {}
        user_id = get_jwt_identity()

        required = ["type", "source", "destination", "operator", "journey_date", "seat_no", "seat_class"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({"message": f"Missing fields: {missing} ❌"}), 400

        transport_type = data["type"]
        source = data["source"]
        destination = data["destination"]
        operator = data["operator"]
        journey_date = data["journey_date"]
        seat_no = data["seat_no"]
        seat_class = data["seat_class"]

        price = get_price(transport_type, source, destination)
        if price is None:
            price = int(data.get("price", 0))
        if price <= 0:
            return jsonify({"message": "Invalid route or price selected ❌"}), 400

        booked_seats = get_booked_seat_numbers(transport_type, source, destination, operator, journey_date)
        if seat_no in booked_seats:
            return jsonify({"message": f"Seat {seat_no} is already booked ❌"}), 409

        ticket = TicketFactory.create_ticket(
            transport_type=transport_type,
            source=source,
            destination=destination,
            price=price
        )

        schedule_key = make_schedule_key(transport_type, source, destination, operator, journey_date)
        seat_layout = {
            "bus": "36 seats bus layout",
            "train": "One bogie layout",
            "plane": "Economy class layout",
        }.get(str(transport_type).lower(), "Seat layout")

        booking_doc = {
            "user_id": user_id,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "journey_date": journey_date,
            "departure_time": data.get("departure_time", "Selected schedule"),
            "seat_no": seat_no,
            "seat_class": seat_class,
            "seat_layout": seat_layout,
            "schedule_key": schedule_key,
            "status": "CONFIRMED",
            "payment_status": "NOT_INCLUDED",
            "booked_at": datetime.utcnow().isoformat(),
        }

        result = DB.bookings().insert_one(booking_doc)
        booking_id = str(result.inserted_id)

        DB.notifications().insert_one({
            "user_id": user_id,
            "message": f"Booking confirmed! {ticket.type} ticket: {ticket.source} → {ticket.destination}, Seat {seat_no}",
            "type": "booking",
            "read": False,
            "created_at": datetime.utcnow().isoformat(),
        })

        return jsonify({
            "message": "Booking Successful ✅",
            "booking_id": booking_id,
            "ticket": ticket.to_dict(),
            "operator": operator,
            "seat_no": seat_no,
            "seat_class": seat_class,
            "redirect_url": f"/ticket-view?id={booking_id}",
        })

    except KeyError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@booking.route("/ticket-data/<booking_id>", methods=["GET"])
@jwt_required()
def get_ticket_data(booking_id):
    try:
        user_id = get_jwt_identity()
        booking_doc = DB.bookings().find_one({"_id": ObjectId(booking_id), "user_id": user_id})
        if not booking_doc:
            return jsonify({"message": "Ticket not found or access denied ❌"}), 404

        booking_doc["_id"] = str(booking_doc["_id"])

        try:
            user_doc = DB.users().find_one({"_id": ObjectId(user_id)}) or {}
        except Exception:
            user_doc = {}

        transport_type = booking_doc.get("ticket", {}).get("type", "")
        builder = get_ticket_builder(transport_type)
        director = TicketDirector()
        director.set_builder_type(builder)
        final_ticket = director.construct_ticket(booking_doc, user_doc)

        return jsonify({"message": "Ticket generated using Builder Pattern ✅", "ticket_view": final_ticket.to_dict()})

    except Exception as e:
        return jsonify({"message": f"Error generating ticket: {str(e)}"}), 500


@booking.route("/my-bookings", methods=["GET"])
@jwt_required()
def my_bookings():
    try:
        user_id = get_jwt_identity()
        bookings = list(DB.bookings().find({"user_id": user_id}).sort("booked_at", -1))
        for booking in bookings:
            booking["_id"] = str(booking["_id"])
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@booking.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        notifications = list(DB.notifications().find({"user_id": user_id}).sort("created_at", -1))
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
        return jsonify({"notifications": notifications, "unread_count": sum(1 for n in notifications if not n.get("read", False))})
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@booking.route("/notifications/mark-read", methods=["POST"])
@jwt_required()
def mark_notification_read():
    try:
        user_id = get_jwt_identity()
        data = request.json or {}
        notification_id = data.get("notification_id")
        DB.notifications().update_one({"_id": ObjectId(notification_id), "user_id": user_id}, {"$set": {"read": True}})
        return jsonify({"message": "Marked as read ✅"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
'''

FILES["templates/seat_selection.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BD Ticket — Seat Selection</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="/static/seat_ticket.css">
</head>
<body class="{{ transport_type }}">
<nav>
  <a href="/dashboard" class="logo">
    <div class="logo-box"><i class="fas fa-ticket-alt"></i></div>
    <div class="logo-name">BD<span>Ticket</span></div>
  </a>
  <button class="nav-btn" onclick="logout()">Logout</button>
</nav>

<div class="page">
  <section class="hero-card">
    <div>
      <span class="badge" id="transportBadge">Seat Selection</span>
      <h1 id="pageTitle">Select Your Seat</h1>
      <p id="journeyText">Loading journey details...</p>
    </div>
    <div class="summary-mini">
      <span>Selected Seat</span>
      <strong id="selectedSeatText">None</strong>
    </div>
  </section>

  <section class="main-grid">
    <div class="seat-card">
      <div class="seat-head">
        <h2 id="layoutTitle">Seat Layout</h2>
        <div class="legend">
          <span><i class="dot available"></i> Available</span>
          <span><i class="dot selected"></i> Selected</span>
          <span><i class="dot booked"></i> Booked</span>
        </div>
      </div>
      <div class="vehicle-shell">
        <div class="front-label" id="frontLabel">FRONT</div>
        <div id="seatGrid" class="seat-grid"></div>
      </div>
    </div>

    <aside class="booking-card">
      <h2>Booking Summary</h2>
      <div class="info-row"><span>Transport</span><strong id="sumType">-</strong></div>
      <div class="info-row"><span>Route</span><strong id="sumRoute">-</strong></div>
      <div class="info-row"><span>Operator</span><strong id="sumOperator">-</strong></div>
      <div class="info-row"><span>Date</span><strong id="sumDate">-</strong></div>
      <div class="info-row"><span>Fare</span><strong id="sumFare">-</strong></div>
      <div class="info-row"><span>Seat Class</span><strong id="sumClass">-</strong></div>
      <p class="note" id="messageBox">Choose an available seat to continue.</p>
      <button class="confirm-btn" id="confirmBtn" onclick="confirmBooking()" disabled>Confirm Booking & Generate Ticket</button>
      <button class="back-btn" onclick="history.back()">Back</button>
    </aside>
  </section>
</div>

<div class="toast" id="toast"></div>

<script>
const API = "http://127.0.0.1:5000";
const TRANSPORT_TYPE = "{{ transport_type }}";
const STORAGE_KEY = TRANSPORT_TYPE + "_selection";
let journey = {};
let selectedSeat = null;

function titleCase(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function getToken() {
  return localStorage.getItem("token") || "";
}

function logout() {
  localStorage.clear();
  window.location = "/";
}

function showToast(msg, type = "ok") {
  const el = document.getElementById("toast");
  el.innerHTML = msg;
  el.className = "toast " + type + " show";
  setTimeout(() => el.classList.remove("show"), 3500);
}

function loadJourneyFromStorage() {
  journey = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");

  if (!journey.source || !journey.destination || !journey.operator || !journey.journeyDate) {
    showToast("Journey data missing. Please select route and operator again.", "err");
    setTimeout(() => window.location = "/" + TRANSPORT_TYPE, 1200);
    return false;
  }

  document.getElementById("transportBadge").textContent = titleCase(TRANSPORT_TYPE);
  document.getElementById("pageTitle").textContent = `${titleCase(TRANSPORT_TYPE)} Seat Selection`;
  document.getElementById("journeyText").textContent = `${journey.source} → ${journey.destination}`;
  document.getElementById("sumType").textContent = titleCase(TRANSPORT_TYPE);
  document.getElementById("sumRoute").textContent = `${journey.source} → ${journey.destination}`;
  document.getElementById("sumOperator").textContent = journey.operator;
  document.getElementById("sumDate").textContent = journey.journeyDate;
  document.getElementById("sumFare").textContent = "৳" + journey.price;

  const layoutTitles = {
    bus: "Bus Layout — 36 Seats",
    train: "Train Layout — One Bogie",
    plane: "Plane Layout — Economy Class"
  };

  const frontLabels = {
    bus: "DRIVER",
    train: "BOGIE 1",
    plane: "COCKPIT"
  };

  document.getElementById("layoutTitle").textContent = layoutTitles[TRANSPORT_TYPE] || "Seat Layout";
  document.getElementById("frontLabel").textContent = frontLabels[TRANSPORT_TYPE] || "FRONT";

  return true;
}

async function loadSeats() {
  const url = `${API}/seats/${TRANSPORT_TYPE}?source=${encodeURIComponent(journey.source)}&destination=${encodeURIComponent(journey.destination)}&operator=${encodeURIComponent(journey.operator)}&journey_date=${encodeURIComponent(journey.journeyDate)}`;
  const res = await fetch(url);
  const data = await res.json();

  if (!res.ok) {
    showToast(data.message || "Could not load seats.", "err");
    return;
  }

  renderSeats(data.seats || []);
}

function renderSeats(seats) {
  const grid = document.getElementById("seatGrid");
  grid.className = "seat-grid " + TRANSPORT_TYPE;
  grid.innerHTML = "";

  seats.forEach((seat) => {
    const btn = document.createElement("button");
    btn.className = `seat ${seat.status}`;
    btn.textContent = seat.seat_no;
    btn.dataset.seatNo = seat.seat_no;
    btn.dataset.seatClass = seat.class_type;
    btn.disabled = seat.status === "booked";
    btn.onclick = () => selectSeat(btn, seat);
    grid.appendChild(btn);
  });
}

function selectSeat(button, seat) {
  document.querySelectorAll(".seat.selected").forEach(btn => {
    btn.classList.remove("selected");
    btn.classList.add("available");
  });

  button.classList.remove("available");
  button.classList.add("selected");

  selectedSeat = seat;
  document.getElementById("selectedSeatText").textContent = seat.seat_no;
  document.getElementById("sumClass").textContent = seat.class_type;
  document.getElementById("messageBox").textContent = `Seat ${seat.seat_no} selected successfully.`;
  document.getElementById("messageBox").className = "note success";
  document.getElementById("confirmBtn").disabled = false;
}

async function confirmBooking() {
  if (!selectedSeat) {
    showToast("Please select a seat first.", "err");
    return;
  }

  if (!getToken()) {
    window.location = "/";
    return;
  }

  const payload = {
    type: titleCase(TRANSPORT_TYPE),
    source: journey.source,
    destination: journey.destination,
    price: journey.price,
    operator: journey.operator,
    journey_date: journey.journeyDate,
    departure_time: journey.departure_time || "Selected schedule",
    seat_no: selectedSeat.seat_no,
    seat_class: selectedSeat.class_type
  };

  try {
    const res = await fetch(API + "/book", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      showToast(data.message || "Booking failed.", "err");
      await loadSeats();
      return;
    }

    showToast("Booking confirmed. Opening ticket...", "ok");
    setTimeout(() => {
      window.location = "/ticket-view?id=" + data.booking_id;
    }, 800);

  } catch (error) {
    showToast("Server error. Please check Flask server.", "err");
  }
}

window.onload = async function() {
  if (!getToken()) {
    window.location = "/";
    return;
  }

  if (loadJourneyFromStorage()) {
    await loadSeats();
  }
};
</script>
</body>
</html>
'''

FILES["templates/ticket_view.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BD Ticket — E-Ticket</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="/static/seat_ticket.css">
</head>
<body>
<nav>
  <a href="/dashboard" class="logo">
    <div class="logo-box"><i class="fas fa-ticket-alt"></i></div>
    <div class="logo-name">BD<span>Ticket</span></div>
  </a>
  <button class="nav-btn" onclick="logout()">Logout</button>
</nav>

<div class="page">
  <div id="ticketRoot" class="loading-card">
    <i class="fas fa-spinner fa-spin"></i>
    <h2>Loading ticket...</h2>
  </div>
</div>

<script>
const API = "http://127.0.0.1:5000";

function getToken() {
  return localStorage.getItem("token") || "";
}

function logout() {
  localStorage.clear();
  window.location = "/";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sectionHtml(section) {
  const rows = Object.entries(section.rows || {}).map(([key, value]) => `
    <div class="ticket-row">
      <span>${escapeHtml(key)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join("");

  return `
    <div class="ticket-section">
      <h2>${escapeHtml(section.title)}</h2>
      <div class="ticket-rows">${rows}</div>
    </div>
  `;
}

function renderTicket(ticket) {
  document.body.className = ticket.theme || "";

  document.getElementById("ticketRoot").className = "";
  document.getElementById("ticketRoot").innerHTML = `
    <div class="ticket-card">
      <div class="ticket-top">
        <div class="ticket-title-area">
          <div class="ticket-icon"><i class="fas ${escapeHtml(ticket.icon)}"></i></div>
          <div>
            <h1>${escapeHtml(ticket.title)}</h1>
            <p>${escapeHtml(ticket.subtitle)}</p>
          </div>
        </div>
        <div class="ticket-id-box">
          <span>Ticket ID</span>
          <strong>${escapeHtml(ticket.ticket_id)}</strong>
        </div>
      </div>

      <div class="route-band">
        <div class="route-text">${escapeHtml(ticket.route_line)}</div>
        <div class="status-pill">${escapeHtml(ticket.status)}</div>
      </div>

      <div class="ticket-body">
        <div class="ticket-info">
          ${(ticket.sections || []).map(sectionHtml).join("")}
        </div>

        <div class="ticket-code-side">
          <div class="fake-qr"></div>
          <span>Ticket Code</span>
          <strong>${escapeHtml(ticket.ticket_code)}</strong>
          <small>Issued: ${escapeHtml(ticket.issue_time)}</small>
        </div>
      </div>

      <div class="ticket-footer">
        <i class="fas fa-info-circle"></i> ${escapeHtml(ticket.footer_note)}
      </div>
    </div>

    <div class="ticket-actions">
      <button onclick="window.print()" class="primary-action">Print / Save as PDF</button>
      <button onclick="window.location='/dashboard'" class="secondary-action">Back to Dashboard</button>
    </div>
  `;
}

async function loadTicket() {
  if (!getToken()) {
    window.location = "/";
    return;
  }

  const bookingId = new URLSearchParams(window.location.search).get("id");

  if (!bookingId) {
    document.getElementById("ticketRoot").className = "error-card";
    document.getElementById("ticketRoot").innerHTML = "Missing booking ID.";
    return;
  }

  try {
    const response = await fetch(`${API}/ticket-data/${bookingId}`, {
      headers: {
        "Authorization": "Bearer " + getToken()
      }
    });

    const data = await response.json();

    if (!response.ok) {
      document.getElementById("ticketRoot").className = "error-card";
      document.getElementById("ticketRoot").innerHTML = data.message || "Could not load ticket.";
      return;
    }

    renderTicket(data.ticket_view);

  } catch (error) {
    document.getElementById("ticketRoot").className = "error-card";
    document.getElementById("ticketRoot").innerHTML = "Server error. Please check Flask server.";
  }
}

window.onload = loadTicket;
</script>
</body>
</html>
'''

FILES["static/seat_ticket.css"] = r'''
:root{--nav:#0f172a;--bg:#f0f4f8;--txt:#0f172a;--sub:#64748b;--bdr:#e2e8f0;--main:#16a34a;--light:#dcfce7;--dark:#14532d}
body.bus{--main:#16a34a;--light:#dcfce7;--dark:#14532d}
body.train{--main:#2563eb;--light:#dbeafe;--dark:#1e3a8a}
body.plane{--main:#f97316;--light:#ffedd5;--dark:#7c2d12}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--txt);min-height:100vh}
nav{background:var(--nav);height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 40px;position:sticky;top:0;z-index:10}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo-box{width:38px;height:38px;background:var(--main);border-radius:10px;display:flex;align-items:center;justify-content:center;color:white}
.logo-name{font-family:'Syne',sans-serif;color:white;font-size:21px;font-weight:900}
.logo-name span{color:var(--main)}
.nav-btn{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);color:white;padding:9px 14px;border-radius:10px;font-weight:800;cursor:pointer}
.page{max-width:1180px;margin:30px auto;padding:0 20px}
.hero-card{background:white;border-radius:22px;padding:26px;display:flex;justify-content:space-between;gap:20px;align-items:center;box-shadow:0 12px 35px rgba(15,23,42,.08)}
.badge{display:inline-block;background:var(--light);color:var(--dark);padding:7px 14px;border-radius:999px;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.7px}
.hero-card h1{margin-top:10px;font-family:'Syne',sans-serif;font-size:32px;font-weight:900}
.hero-card p{color:var(--sub);margin-top:8px}
.summary-mini{min-width:180px;background:var(--light);border:1px solid var(--main);border-radius:16px;padding:18px;text-align:right}
.summary-mini span{display:block;color:var(--dark);font-size:12px;font-weight:800;margin-bottom:6px}
.summary-mini strong{font-size:28px;font-family:'Syne',sans-serif}
.main-grid{margin-top:24px;display:grid;grid-template-columns:1fr 360px;gap:24px}
.seat-card,.booking-card,.loading-card,.error-card{background:white;border-radius:22px;padding:24px;box-shadow:0 12px 35px rgba(15,23,42,.08)}
.seat-head{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:22px}
.seat-head h2,.booking-card h2{font-family:'Syne',sans-serif;font-size:22px}
.legend{display:flex;gap:12px;flex-wrap:wrap;color:var(--sub);font-size:13px;font-weight:700}
.dot{width:13px;height:13px;display:inline-block;border-radius:4px;margin-right:5px;vertical-align:middle}
.dot.available{background:#dcfce7;border:1px solid #16a34a}.dot.selected{background:#2563eb}.dot.booked{background:#cbd5e1}
.vehicle-shell{max-width:600px;margin:0 auto;border:2px solid #cbd5e1;background:#f8fafc;border-radius:42px 42px 20px 20px;padding:24px 28px 30px}
.front-label{background:#e2e8f0;color:#334155;padding:12px;text-align:center;border-radius:14px;font-weight:900;margin-bottom:22px;letter-spacing:1px}
.seat-grid{display:grid;justify-content:center;gap:10px}
.seat-grid.bus,.seat-grid.train{grid-template-columns:55px 55px 34px 55px 55px}
.seat-grid.bus .seat:nth-child(4n+3),.seat-grid.train .seat:nth-child(4n+3){grid-column:4}
.seat-grid.plane{grid-template-columns:52px 52px 52px 34px 52px 52px 52px}
.seat-grid.plane .seat:nth-child(6n+4){grid-column:5}
.seat{height:48px;border-radius:13px 13px 7px 7px;border:2px solid #16a34a;background:#dcfce7;color:#166534;font-weight:900;cursor:pointer;transition:.16s}
.seat:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 18px rgba(15,23,42,.18)}
.seat.selected{background:#2563eb;border-color:#1d4ed8;color:white}
.seat.booked{background:#cbd5e1;border-color:#94a3b8;color:#64748b;text-decoration:line-through;cursor:not-allowed}
.info-row{display:flex;justify-content:space-between;gap:14px;padding:14px 0;border-bottom:1px solid var(--bdr)}
.info-row span{color:var(--sub);font-weight:700}.info-row strong{text-align:right}
.note{margin-top:18px;padding:13px;border-radius:13px;background:#f1f5f9;color:#475569;font-weight:700}.note.success{background:#dcfce7;color:#166534}
.confirm-btn,.back-btn,.primary-action,.secondary-action{width:100%;padding:14px;margin-top:14px;border:none;border-radius:13px;font-weight:900;cursor:pointer;font-size:15px}
.confirm-btn,.primary-action{background:var(--main);color:white}.confirm-btn:disabled{background:#94a3b8;cursor:not-allowed}
.back-btn,.secondary-action{background:#f1f5f9;color:var(--txt);border:1px solid var(--bdr)}
.toast{position:fixed;right:24px;bottom:24px;background:#0f172a;color:white;padding:14px 18px;border-radius:13px;font-weight:800;opacity:0;transform:translateY(70px);transition:.25s;z-index:100}
.toast.show{opacity:1;transform:translateY(0)}.toast.err{border-left:5px solid #dc2626}.toast.ok{border-left:5px solid #16a34a}
.ticket-card{background:white;border-radius:28px;overflow:hidden;border:1px solid var(--bdr);box-shadow:0 22px 60px rgba(15,23,42,.14)}
.ticket-top{background:linear-gradient(135deg,var(--nav),var(--dark));color:white;padding:28px 32px;display:flex;justify-content:space-between;gap:22px;align-items:center}
.ticket-title-area{display:flex;align-items:center;gap:18px}.ticket-icon{width:64px;height:64px;border-radius:18px;background:var(--main);display:flex;align-items:center;justify-content:center;font-size:28px}.ticket-title-area h1{font-family:'Syne',sans-serif;font-size:32px;font-weight:900}.ticket-title-area p{color:rgba(255,255,255,.7);margin-top:5px}
.ticket-id-box{text-align:right}.ticket-id-box span{display:block;font-size:12px;color:rgba(255,255,255,.65);font-weight:900;text-transform:uppercase;margin-bottom:6px}.ticket-id-box strong{font-size:20px}
.route-band{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:22px 32px;background:var(--light);border-bottom:1px dashed #cbd5e1}.route-text{font-family:'Syne',sans-serif;font-size:25px;font-weight:900;color:var(--dark)}.status-pill{background:white;color:var(--main);border:2px solid var(--main);padding:8px 14px;border-radius:999px;font-size:12px;font-weight:900}
.ticket-body{display:grid;grid-template-columns:1fr 240px}.ticket-info{padding:28px 32px}.ticket-section{margin-bottom:22px}.ticket-section h2{font-size:15px;text-transform:uppercase;letter-spacing:.8px;color:var(--main);margin-bottom:12px;font-weight:900}.ticket-rows{display:grid;grid-template-columns:1fr 1fr;gap:12px}.ticket-row{background:#f8fafc;border:1px solid var(--bdr);border-radius:14px;padding:13px}.ticket-row span{display:block;color:var(--sub);font-size:12px;font-weight:800;margin-bottom:5px}.ticket-row strong{font-size:14px}
.ticket-code-side{border-left:1px dashed #cbd5e1;padding:28px 24px;background:#fcfcfd;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.fake-qr{width:150px;height:150px;border-radius:18px;border:2px solid var(--txt);background:linear-gradient(45deg,#111 25%,transparent 25%),linear-gradient(-45deg,#111 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#111 75%),linear-gradient(-45deg,transparent 75%,#111 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0;margin-bottom:14px}.ticket-code-side span,.ticket-code-side small{color:var(--sub);font-weight:800}.ticket-code-side strong{margin-top:6px;font-size:13px}
.ticket-footer{padding:18px 32px;background:#fffbeb;border-top:1px solid #fde68a;color:#92400e;font-weight:900}.ticket-actions{display:flex;gap:12px;justify-content:center;margin-top:24px}.ticket-actions button{width:auto;min-width:190px}.loading-card,.error-card{text-align:center;padding:45px}.error-card{color:#dc2626;font-weight:900}
@media(max-width:900px){nav{padding:0 18px}.hero-card,.seat-head,.ticket-top,.route-band{flex-direction:column;align-items:flex-start}.main-grid,.ticket-body{grid-template-columns:1fr}.ticket-code-side{border-left:none;border-top:1px dashed #cbd5e1}.ticket-rows{grid-template-columns:1fr}.ticket-id-box{text-align:left}}
@media print{nav,.ticket-actions{display:none}body{background:white}.page{max-width:none;margin:0;padding:0}.ticket-card{box-shadow:none;border-radius:0}}
'''

FILES["app_with_seat_example.py"] = r'''
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.auth_routes    import auth
from routes.booking_routes import booking
from routes.route_routes   import route_bp
from routes.admin_routes   import admin_bp
from routes.seat_routes    import seat_bp
from config import JWT_SECRET

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)

app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(route_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(seat_bp)

if __name__ == "__main__":
    app.run(debug=True)
'''


def write_files():
    root = Path.cwd()
    for relative_path, content in FILES.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            backup = path.with_suffix(path.suffix + ".backup")
            backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Backup created: {backup}")

        path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Written: {path}")

    print("\nDone.")
    print("Now update your real app.py:")
    print("1. Add: from routes.seat_routes import seat_bp")
    print("2. Add: app.register_blueprint(seat_bp)")
    print("\nThen run: python app.py")


if __name__ == "__main__":
    write_files()
