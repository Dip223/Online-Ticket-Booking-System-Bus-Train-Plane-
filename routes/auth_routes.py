from flask import Blueprint, request, jsonify, render_template
from config import DB
from models.email_sender import send_email
from datetime import datetime, timedelta
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)


# ── Page routes ───────────────────────────────────────────────────────────────

@auth.route("/")
def home():
    return render_template("login.html")

@auth.route("/register-page")
def register_page():
    return render_template("register.html")

@auth.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@auth.route("/forgot")
def forgot_page():
    return render_template("forgot.html")

@auth.route("/bus")
def bus_page():
    return render_template("bus.html")

@auth.route("/train")
def train_page():
    return render_template("train.html")

@auth.route("/plane")
def plane_page():
    return render_template("plane.html")


# ── Send register OTP ─────────────────────────────────────────────────────────

@auth.route("/send-register-otp", methods=["POST"])
def send_register_otp():
    data     = request.json
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"message": "All fields are required ❌"}), 400

    if DB.users().find_one({"email": email}):
        return jsonify({"message": "Email already registered ❌"}), 400

    otp = str(random.randint(100000, 999999))

    DB.otps().update_one(
        {"email": email},
        {"$set": {
            "otp":       otp,
            "user_data": {
                "name":     name,
                "email":    email,
                "password": generate_password_hash(password),
                "role":     "user",
            },
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }},
        upsert=True,
    )

    send_email(email, "BD Ticket — Verify Your Account", otp, name)
    return jsonify({"message": "OTP sent to your email 📧"})


# ── Verify register OTP ───────────────────────────────────────────────────────

@auth.route("/verify-register-otp", methods=["POST"])
def verify_register_otp():
    data      = request.json
    email     = (data.get("email") or "").strip().lower()
    user_otp  = (data.get("otp")   or "").strip()

    record = DB.otps().find_one({"email": email})
    if not record:
        return jsonify({"message": "OTP not found ❌"}), 404
    if datetime.utcnow() > record["expires_at"]:
        DB.otps().delete_one({"email": email})
        return jsonify({"message": "OTP expired ⏰"}), 400
    if record["otp"] != user_otp:
        return jsonify({"message": "Invalid OTP ❌"}), 400
    if DB.users().find_one({"email": email}):
        return jsonify({"message": "Already registered ❌"}), 400

    DB.users().insert_one(record["user_data"])
    DB.otps().delete_one({"email": email})

    # Create welcome notification
    DB.notifications().insert_one({
        "email":      email,
        "message":    "Welcome to BD Ticket! 🎉 Your account has been created.",
        "type":       "welcome",
        "read":       False,
        "created_at": datetime.utcnow().isoformat(),
    })

    return jsonify({"message": "Account created successfully ✅"})


# ── Login ─────────────────────────────────────────────────────────────────────

@auth.route("/login", methods=["POST"])
def login():
    data     = request.json
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = DB.users().find_one({"email": email})
    if not user:
        return jsonify({"message": "Email not found ❌"}), 404
    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Wrong password ❌"}), 401

    token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "token":   token,
        "user_id": str(user["_id"]),
        "name":    user.get("name", ""),
        "email":   user.get("email", ""),
        "role":    user.get("role", "user"),
        "message": "Login successful ✅",
    })


# ── Forgot password ───────────────────────────────────────────────────────────

@auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.json
    email = (data.get("email") or "").strip().lower()
    user  = DB.users().find_one({"email": email})

    if not user:
        return jsonify({"message": "Email not registered ❌"}), 404

    otp = str(random.randint(100000, 999999))
    DB.otps().update_one(
        {"email": email},
        {"$set": {
            "otp":        otp,
            "type":       "reset",
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }},
        upsert=True,
    )

    send_email(email, "BD Ticket — Password Reset", otp, user.get("name", "User"))
    return jsonify({"message": "Reset OTP sent to your email 📧"})


# ── Reset password ────────────────────────────────────────────────────────────

@auth.route("/reset-password", methods=["POST"])
def reset_password():
    data         = request.json
    email        = (data.get("email") or "").strip().lower()
    otp          = (data.get("otp")   or "").strip()
    new_password = data.get("password") or ""

    record = DB.otps().find_one({"email": email})
    if not record:
        return jsonify({"message": "OTP not found ❌"}), 404
    if datetime.utcnow() > record["expires_at"]:
        DB.otps().delete_one({"email": email})
        return jsonify({"message": "OTP expired ⏰"}), 400
    if record["otp"] != otp:
        return jsonify({"message": "Invalid OTP ❌"}), 400

    DB.users().update_one(
        {"email": email},
        {"$set": {"password": generate_password_hash(new_password)}}
    )
    DB.otps().delete_one({"email": email})
    return jsonify({"message": "Password updated successfully ✅"})


# ── Debug ─────────────────────────────────────────────────────────────────────

@auth.route("/users")
def get_users():
    users = list(DB.users().find())
    for u in users:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
    return jsonify(users)


# ================= SCHEDULE PAGES (Step 2 - Operator Selection) =================

@auth.route('/bus-schedule')
def bus_schedule_page():
    return render_template("bus_schedule.html")

@auth.route('/train-schedule')
def train_schedule_page():
    return render_template("train_schedule.html")

@auth.route('/plane-schedule')
def plane_schedule_page():
    return render_template("plane_schedule.html")

# ================= NOTIFICATIONS PAGE =================

@auth.route("/notifications-page")
def notifications_page():
    return render_template("notifications.html")