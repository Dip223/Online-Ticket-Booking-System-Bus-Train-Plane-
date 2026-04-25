from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.auth_routes import auth
from routes.booking_routes import booking
from routes.ticket_routes import ticket
from routes.route_routes import route_bp

from config import JWT_SECRET

app = Flask(__name__)
CORS(app)

# JWT config
app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)

# register routes
app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(ticket)
app.register_blueprint(route_bp)

if __name__ == "__main__":
    app.run(debug=True)