from flask import Blueprint, jsonify, request

route_bp = Blueprint("routes", __name__)

# ================= COMMON ROUTE BUILDER =================
def make_bidirectional(routes):
    result = []
    for r in routes:
        result.append(r)
        result.append({
            "from": r["to"],
            "to": r["from"],
            "price": r["price"]
        })
    return result


# ================= DATA =================

plane_data = make_bidirectional([
    {"from": "Dhaka", "to": "Chattogram", "price": 3000},
    {"from": "Dhaka", "to": "Cox's Bazar", "price": 3500},
    {"from": "Dhaka", "to": "Sylhet", "price": 2800},
    {"from": "Dhaka", "to": "Jashore", "price": 2600},
    {"from": "Dhaka", "to": "Saidpur", "price": 2700},
    {"from": "Dhaka", "to": "Rajshahi", "price": 2500},
    {"from": "Dhaka", "to": "Barishal", "price": 2300}
])

bus_data = make_bidirectional([
    {"from": "Dhaka", "to": "Chattogram", "price": 800},
    {"from": "Dhaka", "to": "Sylhet", "price": 700},
    {"from": "Dhaka", "to": "Rajshahi", "price": 650},
    {"from": "Dhaka", "to": "Khulna", "price": 750},
    {"from": "Dhaka", "to": "Barishal", "price": 600}
])

train_data = make_bidirectional([
    {"from": "Dhaka", "to": "Chattogram", "price": 900},
    {"from": "Dhaka", "to": "Sylhet", "price": 850},
    {"from": "Dhaka", "to": "Rajshahi", "price": 800},
    {"from": "Dhaka", "to": "Khulna", "price": 780}
])


operators = {
    "plane": [
        "Biman Bangladesh Airlines",
        "US-Bangla Airlines"
    ],
    "bus": [
        "Ena Transport",
        "Green Line Transport",
        "Hanif Transport",
        "Shyamoli Transport"
    ],
    "train": [
        "Upokul Express",
        "Shundorbon Express",
        "Joyentika Express"
    ]
}


# ================= NEW UNIFIED ROUTE =================
@route_bp.route('/routes', methods=['GET'])
def get_routes():
    type = request.args.get("type", "").lower()

    if type == "plane":
        return jsonify({
            "routes": plane_data,
            "operators": operators["plane"]
        })

    elif type == "bus":
        return jsonify({
            "routes": bus_data,
            "operators": operators["bus"]
        })

    elif type == "train":
        return jsonify({
            "routes": train_data,
            "operators": operators["train"]
        })

    return jsonify({"message": "Invalid type ❌"}), 400


# ================= OLD ROUTES (OPTIONAL KEEP) =================
# Keep these if your frontend still uses them

@route_bp.route('/plane-routes')
def plane_routes():
    return jsonify({
        "routes": plane_data,
        "operators": operators["plane"]
    })


@route_bp.route('/bus-routes')
def bus_routes():
    return jsonify({
        "routes": bus_data,
        "operators": operators["bus"]
    })


@route_bp.route('/train-routes')
def train_routes():
    return jsonify({
        "routes": train_data,
        "operators": operators["train"]
    })