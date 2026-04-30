from flask import Blueprint, jsonify

route_bp = Blueprint("routes", __name__)


def _bidir(routes):
    """Add reverse direction for every route."""
    result = list(routes)
    for r in routes:
        result.append({"from": r["to"], "to": r["from"], "price": r["price"]})
    return result


# ── Data ──────────────────────────────────────────────────────────────────────

BUS_ROUTES = _bidir([
    {"from": "Dhaka", "to": "Chattogram",  "price": 800},
    {"from": "Dhaka", "to": "Sylhet",      "price": 700},
    {"from": "Dhaka", "to": "Rajshahi",    "price": 650},
    {"from": "Dhaka", "to": "Khulna",      "price": 750},
    {"from": "Dhaka", "to": "Barishal",    "price": 600},
    {"from": "Dhaka", "to": "Rangpur",     "price": 800},
    {"from": "Dhaka", "to": "Mymensingh",  "price": 350},
    {"from": "Dhaka", "to": "Cox's Bazar", "price": 900},
])

TRAIN_ROUTES = _bidir([
    {"from": "Dhaka", "to": "Chattogram",  "price": 500},
    {"from": "Dhaka", "to": "Sylhet",      "price": 450},
    {"from": "Dhaka", "to": "Rajshahi",    "price": 400},
    {"from": "Dhaka", "to": "Khulna",      "price": 480},
    {"from": "Dhaka", "to": "Rangpur",     "price": 520},
    {"from": "Dhaka", "to": "Mymensingh",  "price": 200},
    {"from": "Dhaka", "to": "Jamalpur",    "price": 250},
])

PLANE_ROUTES = _bidir([
    {"from": "Dhaka", "to": "Chattogram",  "price": 3000},
    {"from": "Dhaka", "to": "Cox's Bazar", "price": 3500},
    {"from": "Dhaka", "to": "Sylhet",      "price": 2800},
    {"from": "Dhaka", "to": "Jashore",     "price": 2600},
    {"from": "Dhaka", "to": "Saidpur",     "price": 2700},
    {"from": "Dhaka", "to": "Rajshahi",    "price": 2500},
    {"from": "Dhaka", "to": "Barishal",    "price": 2300},
])

OPERATORS = {
    "bus":   ["Ena Transport", "Green Line", "Hanif Transport", "Shyamoli Transport"],
    "train": ["Upokul Express", "Shundorbon Express", "Joyentika Express"],
    "plane": ["Biman Bangladesh Airlines", "US-Bangla Airlines"],
}

PAYMENT_METHODS = [
    {"key": "bkash",      "label": "bKash",      "icon": "📱"},
    {"key": "nagad",      "label": "Nagad",       "icon": "💚"},
    {"key": "visa",       "label": "Visa Card",   "icon": "💳"},
    {"key": "mastercard", "label": "MasterCard",  "icon": "💳"},
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@route_bp.route("/bus-routes")
def bus_routes():
    return jsonify({"routes": BUS_ROUTES, "operators": OPERATORS["bus"]})

@route_bp.route("/train-routes")
def train_routes():
    return jsonify({"routes": TRAIN_ROUTES, "operators": OPERATORS["train"]})

@route_bp.route("/plane-routes")
def plane_routes():
    return jsonify({"routes": PLANE_ROUTES, "operators": OPERATORS["plane"]})

@route_bp.route("/payment-methods")
def payment_methods():
    return jsonify(PAYMENT_METHODS)