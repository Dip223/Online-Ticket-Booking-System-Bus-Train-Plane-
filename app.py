from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.seat_routes import seat_bp
from routes.auth_routes import auth
from routes.booking_routes import booking
from routes.route_routes import route_bp
from routes.admin_routes import admin_bp

from config import JWT_SECRET_KEY

app = Flask(__name__)
CORS(app)

# ===== SESSION SECRET KEY (Fixes the session error) =====
app.secret_key = "bdticket_super_secret_session_key_2024"
# ========================================================

# JWT Configuration
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(seat_bp)
app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(route_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)