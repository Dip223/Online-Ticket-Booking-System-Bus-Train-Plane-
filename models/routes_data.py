# ================= ALL LOCATIONS =================
cities = [
    "Dhaka",
    "Chattogram",
    "Cox's Bazar",
    "Sylhet",
    "Jashore",
    "Rajshahi",
    "Rangpur",
    "Barishal"
]

# ================= GENERATE ALL ROUTES =================
def generate_routes(transport_type):
    routes = []

    for source in cities:
        for destination in cities:
            if source != destination:
                routes.append({
                    "type": transport_type,
                    "from": source,
                    "to": destination,
                    "price": get_price(transport_type)
                })

    return routes


# ================= PRICE BY TYPE =================
def get_price(type):
    if type == "Bus":
        return 500
    elif type == "Train":
        return 800
    elif type == "Plane":
        return 3000