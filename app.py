from flask import Flask
from flask_cors import CORS

from routes.auth_routes import auth
from routes.ticket_routes import ticket
from routes.booking_routes import booking
from routes.route_routes import route_bp

# ✅ CREATE APP FIRST
app = Flask(__name__)
CORS(app)

# ✅ THEN REGISTER ROUTES
app.register_blueprint(auth)
app.register_blueprint(ticket)
app.register_blueprint(booking)
app.register_blueprint(route_bp)

# ✅ RUN
if __name__ == "__main__":
    app.run(debug=True)