from flask import Blueprint, request, jsonify, render_template
from config import DB
from models.email_sender import send_email
from datetime import datetime, timedelta
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)

# ================= PAGES =================

@auth.route('/')
def home():
    return render_template("login.html")

@auth.route('/register-page')
def register_page():
    return render_template("register.html")

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# ================= SEND REGISTER OTP =================

@auth.route('/send-register-otp', methods=['POST'])
def send_register_otp():
    data = request.json
    db = DB.get_db()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # basic validation
    if not name or not email or not password:
        return jsonify({"message": "All fields required ❌"}), 400

    # check if already registered
    if db.users.find_one({"email": email}):
        return jsonify({"message": "User already exists ❌"}), 400

    otp = str(random.randint(100000, 999999))

    # store OTP with expiry (5 min)
    db.otps.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "user_data": {
                    "name": name,
                    "email": email,
                    "password": generate_password_hash(password)  # ✅ hash early
                },
                "expires_at": datetime.utcnow() + timedelta(minutes=5)
            }
        },
        upsert=True
    )

    # send email (HTML template handled inside)
    send_email(email, "OTP Verification", otp, name)

    return jsonify({"message": "OTP sent to your email 📧"})


# ================= VERIFY OTP + CREATE ACCOUNT =================

@auth.route('/verify-register-otp', methods=['POST'])
def verify_register_otp():
    data = request.json
    db = DB.get_db()

    email = data.get('email')
    user_otp = data.get('otp')

    record = db.otps.find_one({"email": email})

    if not record:
        return jsonify({"message": "OTP not found ❌"}), 404

    # check expiry
    if datetime.utcnow() > record['expires_at']:
        db.otps.delete_one({"email": email})
        return jsonify({"message": "OTP expired ⏰"}), 400

    # check OTP
    if record['otp'] != user_otp:
        return jsonify({"message": "Invalid OTP ❌"}), 400

    user_data = record['user_data']

    # final duplicate check
    if db.users.find_one({"email": email}):
        return jsonify({"message": "User already exists ❌"}), 400

    # save user (already hashed)
    db.users.insert_one(user_data)

    # delete OTP after success
    db.otps.delete_one({"email": email})

    return jsonify({"message": "Account created successfully ✅"})


# ================= LOGIN WITH JWT =================

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    db = DB.get_db()

    email = data.get('email')
    password = data.get('password')

    user = db.users.find_one({"email": email})

    if not user:
        return jsonify({"message": "User not found ❌"}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({"message": "Wrong password ❌"}), 401

    # create JWT token
    token = create_access_token(identity=str(user['_id']))

    return jsonify({
        "token": token,
        "user_id": str(user['_id']),
        "message": "Login successful ✅"
    })


# ================= DEBUG (OPTIONAL) =================

@auth.route('/users')
def get_users():
    db = DB.get_db()
    users = list(db.users.find())

    for u in users:
        u['_id'] = str(u['_id'])

    return jsonify(users)

# ================= TRANSPORT PAGES =================

@auth.route('/bus')
def bus_page():
    return render_template("bus.html")

@auth.route('/train')
def train_page():
    return render_template("train.html")

@auth.route('/plane')
def plane_page():
    return render_template("plane.html")