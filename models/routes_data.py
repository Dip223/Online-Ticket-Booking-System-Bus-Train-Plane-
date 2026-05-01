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

# ==================== OPERATORS WITH DETAILED SCHEDULES ====================
OPERATOR_SCHEDULES = {
    "bus": {
        "Ena Transport": {
            "vehicle": "Volvo AC",
            "total_seats": 40,
            "facilities": ["AC", "WiFi", "Snacks", "Water bottle"],
            "duration": "6-7 hours",
            "schedules": [
                {"departure": "06:00 AM", "arrival": "12:00 PM"},
                {"departure": "08:00 AM", "arrival": "02:00 PM"},
                {"departure": "10:00 AM", "arrival": "04:00 PM"},
                {"departure": "02:00 PM", "arrival": "08:00 PM"},
                {"departure": "06:00 PM", "arrival": "12:00 AM"},
                {"departure": "08:00 PM", "arrival": "02:00 AM"}
            ]
        },
        "Green Line": {
            "vehicle": "Scania AC",
            "total_seats": 38,
            "facilities": ["AC", "TV", "Snacks", "Blanket"],
            "duration": "5-6 hours",
            "schedules": [
                {"departure": "07:00 AM", "arrival": "12:30 PM"},
                {"departure": "09:00 AM", "arrival": "02:30 PM"},
                {"departure": "11:00 AM", "arrival": "04:30 PM"},
                {"departure": "03:00 PM", "arrival": "08:30 PM"},
                {"departure": "07:00 PM", "arrival": "12:30 AM"}
            ]
        },
        "Hanif": {
            "vehicle": "Hino AC",
            "total_seats": 42,
            "facilities": ["AC", "Charging point"],
            "duration": "7-8 hours",
            "schedules": [
                {"departure": "05:30 AM", "arrival": "12:30 PM"},
                {"departure": "07:30 AM", "arrival": "02:30 PM"},
                {"departure": "12:00 PM", "arrival": "07:00 PM"},
                {"departure": "04:00 PM", "arrival": "11:00 PM"},
                {"departure": "09:00 PM", "arrival": "04:00 AM"}
            ]
        },
        "Shyamoli": {
            "vehicle": "Standard Non-AC",
            "total_seats": 45,
            "facilities": ["Non-AC", "Economy"],
            "duration": "6-7 hours",
            "schedules": [
                {"departure": "06:30 AM", "arrival": "12:30 PM"},
                {"departure": "09:30 AM", "arrival": "03:30 PM"},
                {"departure": "01:00 PM", "arrival": "07:00 PM"},
                {"departure": "05:00 PM", "arrival": "11:00 PM"},
                {"departure": "10:00 PM", "arrival": "04:00 AM"}
            ]
        }
    },
    "train": {
        "Upokul Express": {
            "vehicle": "Intercity",
            "total_seats": 600,
            "facilities": ["AC", "Non-AC", "Food available"],
            "duration": "4-5 hours",
            "schedules": [
                {"departure": "07:00 AM", "arrival": "11:30 AM"},
                {"departure": "03:00 PM", "arrival": "07:30 PM"}
            ]
        },
        "Shundorbon Express": {
            "vehicle": "Intercity",
            "total_seats": 580,
            "facilities": ["AC", "Non-AC", "Snacks"],
            "duration": "4-5 hours",
            "schedules": [
                {"departure": "08:30 AM", "arrival": "01:00 PM"},
                {"departure": "10:00 PM", "arrival": "02:30 AM"}
            ]
        },
        "Joyentika Express": {
            "vehicle": "Express",
            "total_seats": 550,
            "facilities": ["AC", "Meal included"],
            "duration": "5-6 hours",
            "schedules": [
                {"departure": "06:00 AM", "arrival": "11:00 AM"},
                {"departure": "02:00 PM", "arrival": "07:00 PM"}
            ]
        }
    },
    "plane": {
        "Biman Bangladesh Airlines": {
            "vehicle": "Boeing 737",
            "total_seats": 150,
            "facilities": ["Meal included", "Baggage 20kg", "Entertainment"],
            "duration": "45-60 minutes",
            "schedules": [
                {"departure": "08:00 AM", "arrival": "09:00 AM"},
                {"departure": "12:00 PM", "arrival": "01:00 PM"},
                {"departure": "04:00 PM", "arrival": "05:00 PM"},
                {"departure": "08:00 PM", "arrival": "09:00 PM"}
            ]
        },
        "US-Bangla Airlines": {
            "vehicle": "ATR 72",
            "total_seats": 70,
            "facilities": ["Snacks included", "Baggage 15kg"],
            "duration": "45-60 minutes",
            "schedules": [
                {"departure": "09:00 AM", "arrival": "10:00 AM"},
                {"departure": "01:00 PM", "arrival": "02:00 PM"},
                {"departure": "05:00 PM", "arrival": "06:00 PM"},
                {"departure": "09:00 PM", "arrival": "10:00 PM"}
            ]
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
    """Get all operators with their full schedule information (grouped by operator)"""
    transport_type = transport_type.lower()
    operators = []
    for op_name, op_data in OPERATOR_SCHEDULES.get(transport_type, {}).items():
        operators.append({
            "name": op_name,
            "departure_times": [s["departure"] for s in op_data.get("schedules", [])],
            "duration": op_data.get("duration", ""),
            "facilities": op_data.get("facilities", []),
            "vehicle_type": op_data.get("vehicle", ""),
            "total_seats": op_data.get("total_seats", 0)
        })
    return operators

def get_all_schedules_as_list(transport_type):
    """Get all schedules as individual items (each departure time as separate entry)"""
    transport_type = transport_type.lower()
    all_schedules = []
    
    for op_name, op_data in OPERATOR_SCHEDULES.get(transport_type, {}).items():
        for schedule in op_data.get("schedules", []):
            all_schedules.append({
                "operator": op_name,
                "vehicle": op_data.get("vehicle", ""),
                "total_seats": op_data.get("total_seats", 0),
                "facilities": op_data.get("facilities", []),
                "duration": op_data.get("duration", ""),
                "departure": schedule.get("departure", ""),
                "arrival": schedule.get("arrival", "")
            })
    
    # Sort by departure time
    all_schedules.sort(key=lambda x: x["departure"])
    return all_schedules