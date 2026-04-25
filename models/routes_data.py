
def get_routes(type):
    type = type.lower()

    routes = {
        "bus": [
            {"from": "Dhaka", "to": "Chattogram", "price": 800},
            {"from": "Chattogram", "to": "Dhaka", "price": 800},

            {"from": "Dhaka", "to": "Sylhet", "price": 700},
            {"from": "Sylhet", "to": "Dhaka", "price": 700},

            {"from": "Dhaka", "to": "Rajshahi", "price": 650},
            {"from": "Rajshahi", "to": "Dhaka", "price": 650}
        ],

        "train": [
            {"from": "Dhaka", "to": "Chattogram", "price": 500},
            {"from": "Chattogram", "to": "Dhaka", "price": 500},

            {"from": "Dhaka", "to": "Sylhet", "price": 450},
            {"from": "Sylhet", "to": "Dhaka", "price": 450}
        ],

        "plane": [
            {"from": "Dhaka", "to": "Cox's Bazar", "price": 5000},
            {"from": "Cox's Bazar", "to": "Dhaka", "price": 5000},

            {"from": "Dhaka", "to": "Sylhet", "price": 3500},
            {"from": "Sylhet", "to": "Dhaka", "price": 3500}
        ]
    }

    operators = {
        "bus": ["Ena Transport", "Green Line", "Hanif", "Shyamoli"],
        "train": ["Upokul Express", "Shundorbon Express", "Joyentika Express"],
        "plane": ["Biman Bangladesh Airlines", "US-Bangla Airlines"]
    }

    return {
        "routes": routes[type],
        "operators": operators[type]
    }