"""
models/routes_data.py
Single source of truth for all routes, operators, and schedules
"""

from datetime import datetime, timedelta
import random

# ==================== MASTER ROUTES DATA ====================
ROUTES = {
    "bus": [
        {"from": "Dhaka", "to": "Chattogram", "price": 800},
        {"from": "Chattogram", "to": "Dhaka", "price": 800},
        {"from": "Dhaka", "to": "Sylhet", "price": 700},
        {"from": "Sylhet", "to": "Dhaka", "price": 700},
        {"from": "Dhaka", "to": "Rajshahi", "price": 650},
        {"from": "Rajshahi", "to": "Dhaka", "price": 650},
        {"from": "Dhaka", "to": "Khulna", "price": 750},
        {"from": "Khulna", "to": "Dhaka", "price": 750},
    ],
    "train": [
        {"from": "Dhaka", "to": "Chattogram", "price": 500},
        {"from": "Chattogram", "to": "Dhaka", "price": 500},
        {"from": "Dhaka", "to": "Sylhet", "price": 450},
        {"from": "Sylhet", "to": "Dhaka", "price": 450},
        {"from": "Dhaka", "to": "Rajshahi", "price": 400},
        {"from": "Rajshahi", "to": "Dhaka", "price": 400},
    ],
    "plane": [
        {"from": "Dhaka", "to": "Cox's Bazar", "price": 5000},
        {"from": "Cox's Bazar", "to": "Dhaka", "price": 5000},
        {"from": "Dhaka", "to": "Sylhet", "price": 3500},
        {"from": "Sylhet", "to": "Dhaka", "price": 3500},
        {"from": "Dhaka", "to": "Chattogram", "price": 3000},
        {"from": "Chattogram", "to": "Dhaka", "price": 3000},
    ]
}

# ==================== OPERATORS WITH SCHEDULES ====================
OPERATOR_SCHEDULES = {
    "bus": {
        "Ena Transport": {
            "departure_times": ["06:00 AM", "08:00 AM", "10:00 AM", "02:00 PM", "06:00 PM", "08:00 PM"],
            "duration": "6-7 hours",
            "facilities": ["AC", "WiFi", "Snacks", "Water bottle"],
            "vehicle_type": "Volvo AC",
            "total_seats": 40
        },
        "Green Line": {
            "departure_times": ["07:00 AM", "09:00 AM", "11:00 AM", "03:00 PM", "07:00 PM"],
            "duration": "5-6 hours",
            "facilities": ["AC", "TV", "Snacks", "Blanket"],
            "vehicle_type": "Scania AC",
            "total_seats": 38
        },
        "Hanif": {
            "departure_times": ["05:30 AM", "07:30 AM", "12:00 PM", "04:00 PM", "09:00 PM"],
            "duration": "7-8 hours",
            "facilities": ["AC", "Charging point"],
            "vehicle_type": "Hino AC",
            "total_seats": 42
        },
        "Shyamoli": {
            "departure_times": ["06:30 AM", "09:30 AM", "01:00 PM", "05:00 PM", "10:00 PM"],
            "duration": "6-7 hours",
            "facilities": ["Non-AC", "Economy"],
            "vehicle_type": "Standard",
            "total_seats": 45
        }
    },
    "train": {
        "Upokul Express": {
            "departure_times": ["07:00 AM", "03:00 PM"],
            "duration": "4-5 hours",
            "facilities": ["AC", "Non-AC", "Food available"],
            "vehicle_type": "Intercity",
            "total_seats": 600
        },
        "Shundorbon Express": {
            "departure_times": ["08:30 AM", "10:00 PM"],
            "duration": "4-5 hours",
            "facilities": ["AC", "Non-AC", "Snacks"],
            "vehicle_type": "Intercity",
            "total_seats": 580
        },
        "Joyentika Express": {
            "departure_times": ["06:00 AM", "02:00 PM"],
            "duration": "5-6 hours",
            "facilities": ["AC", "Meal included"],
            "vehicle_type": "Express",
            "total_seats": 550
        }
    },
    "plane": {
        "Biman Bangladesh Airlines": {
            "departure_times": ["08:00 AM", "12:00 PM", "04:00 PM", "08:00 PM"],
            "duration": "45-60 minutes",
            "facilities": ["Meal included", "Baggage 20kg", "Entertainment"],
            "vehicle_type": "Boeing 737",
            "total_seats": 150
        },
        "US-Bangla Airlines": {
            "departure_times": ["09:00 AM", "01:00 PM", "05:00 PM", "09:00 PM"],
            "duration": "45-60 minutes",
            "facilities": ["Snacks included", "Baggage 15kg"],
            "vehicle_type": "ATR 72",
            "total_seats": 70
        }
    }
}

# ==================== HELPER FUNCTIONS ====================
def get_all_cities():
    """Get all unique cities from all routes"""
    cities = set()
    for transport_type in ROUTES:
        for route in ROUTES[transport_type]:
            cities.add(route["from"])
            cities.add(route["to"])
    return sorted(list(cities))

def get_routes_by_type(transport_type):
    """Get all routes for a specific transport type"""
    transport_type = transport_type.lower()
    return ROUTES.get(transport_type, [])

def get_operators_by_type(transport_type):
    """Get all operators for a specific transport type"""
    transport_type = transport_type.lower()
    return list(OPERATOR_SCHEDULES.get(transport_type, {}).keys())

def get_operator_schedule(transport_type, operator_name):
    """Get schedule details for a specific operator"""
    transport_type = transport_type.lower()
    return OPERATOR_SCHEDULES.get(transport_type, {}).get(operator_name, {})

def get_price(transport_type, from_city, to_city):
    """Get price for a specific route"""
    transport_type = transport_type.lower()
    routes = ROUTES.get(transport_type, [])
    for route in routes:
        if route["from"] == from_city and route["to"] == to_city:
            return route["price"]
    return None

def get_available_destinations(transport_type, from_city):
    """Get all available destinations from a source city"""
    transport_type = transport_type.lower()
    routes = ROUTES.get(transport_type, [])
    destinations = []
    for route in routes:
        if route["from"] == from_city:
            destinations.append({
                "to": route["to"],
                "price": route["price"]
            })
    return destinations

def get_all_operators_with_schedules(transport_type):
    """Get all operators with their full schedule information"""
    transport_type = transport_type.lower()
    operators = []
    for op_name, schedule in OPERATOR_SCHEDULES.get(transport_type, {}).items():
        operators.append({
            "name": op_name,
            "departure_times": schedule.get("departure_times", []),
            "duration": schedule.get("duration", ""),
            "facilities": schedule.get("facilities", []),
            "vehicle_type": schedule.get("vehicle_type", ""),
            "total_seats": schedule.get("total_seats", 0)
        })
    return operators