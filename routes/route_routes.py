from flask import Blueprint, jsonify

route_bp = Blueprint("routes", __name__)

# ================= PLANE =================
@route_bp.route('/plane-routes')
def plane_routes():
    return jsonify({
        "routes": [
            {"from": "Dhaka", "to": "Chattogram", "price": 3000},
            {"from": "Dhaka", "to": "Cox's Bazar", "price": 3500},
            {"from": "Dhaka", "to": "Sylhet", "price": 2800}
        ],
        "operators": [
            "Biman Bangladesh Airlines",
            "US-Bangla Airlines"
        ]
    })


# ================= BUS =================
@route_bp.route('/bus-routes')
def bus_routes():
    return jsonify({
        "routes": [
            {"from": "Dhaka", "to": "Chattogram", "price": 800},
            {"from": "Dhaka", "to": "Sylhet", "price": 700},
            {"from": "Dhaka", "to": "Rajshahi", "price": 600}
        ],
        "operators": [
            "Ena Transport",
            "Green Line Transport",
            "Hanif Transport",
            "Shyamoli Transport"
        ]
    })


# ================= TRAIN =================
@route_bp.route('/train-routes')
def train_routes():
    return jsonify({
        "routes": [
            {"from": "Dhaka", "to": "Chattogram", "price": 900},
            {"from": "Dhaka", "to": "Sylhet", "price": 850},
            {"from": "Dhaka", "to": "Rajshahi", "price": 800}
        ],
        "operators": [
            "Upokul Express",
            "Shundorbon Express",
            "Joyentika Express"
        ]
    })