from flask import Blueprint, request, jsonify, render_template
from config import DB
from models.email_sender import send_email
from datetime import datetime, timedelta
import random
import requests

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

# ===== THIS IS THE BLUEPRINT - MUST EXIST! =====
auth = Blueprint("auth", __name__)
# =================================================

# ================= SMS OTP CONFIGURATION =================
SMS_API_KEY = "487be90134311b08750e0e14bb47d0ac9d378f7397695f50"
sms_otp_store = {}


# ================= SMS OTP FUNCTIONS =================

def send_sms_via_api(phone_number, otp_code):
    try:
        if phone_number.startswith('01') and len(phone_number) == 11:
            formatted_number = '+880' + phone_number[1:]
        else:
            formatted_number = phone_number
        
        print(f"📱 Converting {phone_number} → {formatted_number}")
        
        url = "https://api.smsmobileapi.com/sendsms/"
        params = {
            "apikey": SMS_API_KEY,
            "recipients": formatted_number,
            "message": f"Your OTP for BD Ticket is: {otp_code}. Valid for 5 minutes."
        }
        
        response = requests.get(url, params=params, timeout=30)
        result = response.json()
        
        if result.get("result", {}).get("error") == 0:
            print(f"✅ SMS sent successfully to {phone_number}")
            return True
        else:
            print(f"❌ SMS failed: {result}")
            return False
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False


def send_sms_demo(phone_number, otp_code):
    print("\n" + "="*60)
    print(f"📱 DEMO SMS - OTP VERIFICATION")
    print("="*60)
    print(f"To: {phone_number}")
    print(f"OTP Code: {otp_code}")
    print("="*60 + "\n")
    return True


# ================= PAGE ROUTES =================

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

@auth.route("/bus-schedule")
def bus_schedule_page():
    return render_template("bus_schedule.html")

@auth.route("/train-schedule")
def train_schedule_page():
    return render_template("train_schedule.html")

@auth.route("/plane-schedule")
def plane_schedule_page():
    return render_template("plane_schedule.html")

@auth.route("/notifications-page")
def notifications_page():
    return render_template("notifications.html")


# ================= EMAIL OTP (REGISTRATION) =================

@auth.route("/send-register-otp", methods=["POST"])
def send_register_otp():
    data = request.json
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"message": "All fields are required ❌"}), 400

    db = DB.get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"message": "Email already registered ❌"}), 400

    otp = str(random.randint(100000, 999999))

    db.otps.update_one(
        {"email": email},
        {"$set": {
            "otp": otp,
            "user_data": {
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "role": "user",
            },
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }},
        upsert=True,
    )

    send_email(email, "BD Ticket — Verify Your Account", otp, name)
    return jsonify({"message": "OTP sent to your email 📧"})


@auth.route("/verify-register-otp", methods=["POST"])
def verify_register_otp():
    data = request.json
    email = (data.get("email") or "").strip().lower()
    user_otp = (data.get("otp") or "").strip()

    db = DB.get_db()
    record = db.otps.find_one({"email": email})
    if not record:
        return jsonify({"message": "OTP not found ❌"}), 404
    if datetime.utcnow() > record["expires_at"]:
        db.otps.delete_one({"email": email})
        return jsonify({"message": "OTP expired ⏰"}), 400
    if record["otp"] != user_otp:
        return jsonify({"message": "Invalid OTP ❌"}), 400
    if db.users.find_one({"email": email}):
        return jsonify({"message": "Already registered ❌"}), 400

    db.users.insert_one(record["user_data"])
    db.otps.delete_one({"email": email})
    return jsonify({"message": "Account created successfully ✅"})


# ================= LOGIN =================

@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    db = DB.get_db()
    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Email not found ❌"}), 404
    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Wrong password ❌"}), 401

    token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "token": token,
        "user_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "message": "Login successful ✅",
    })


# ================= EMAIL PASSWORD RESET =================

@auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = (data.get("email") or "").strip().lower()
    db = DB.get_db()
    user = db.users.find_one({"email": email})

    if not user:
        return jsonify({"message": "Email not registered ❌"}), 404

    otp = str(random.randint(100000, 999999))
    db.otps.update_one(
        {"email": email},
        {"$set": {
            "otp": otp,
            "type": "reset",
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
        }},
        upsert=True,
    )

    send_email(email, "BD Ticket — Password Reset", otp, user.get("name", "User"))
    return jsonify({"message": "Reset OTP sent to your email 📧"})


@auth.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()
    new_password = data.get("password") or ""

    db = DB.get_db()
    record = db.otps.find_one({"email": email})
    if not record:
        return jsonify({"message": "OTP not found ❌"}), 404
    if datetime.utcnow() > record["expires_at"]:
        db.otps.delete_one({"email": email})
        return jsonify({"message": "OTP expired ⏰"}), 400
    if record["otp"] != otp:
        return jsonify({"message": "Invalid OTP ❌"}), 400

    db.users.update_one(
        {"email": email},
        {"$set": {"password": generate_password_hash(new_password)}}
    )
    db.otps.delete_one({"email": email})
    return jsonify({"message": "Password updated successfully ✅"})


# ================= SMS OTP FOR BOOKING =================

@auth.route("/send-sms-otp", methods=["POST"])
def send_sms_otp():
    try:
        data = request.json
        phone_number = data.get('phone_number', '').strip()
        nid = data.get('nid', '').strip()
        
        if not phone_number or not phone_number.startswith('01') or len(phone_number) != 11:
            return jsonify({"message": "Enter valid 11-digit number (01XXXXXXXXX)"}), 400
        if not nid or len(nid) < 10:
            return jsonify({"message": "Enter valid NID (10-17 digits)"}), 400
        
        otp_code = str(random.randint(100000, 999999))
        
        sms_otp_store[phone_number] = {
            'otp': otp_code,
            'nid': nid,
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'attempts': 0
        }
        
        print(f"\n🔐 Sending OTP to {phone_number}...")
        success = send_sms_via_api(phone_number, otp_code)
        
        if success:
            return jsonify({"message": f"✓ OTP sent to {phone_number} via SMS!"})
        else:
            send_sms_demo(phone_number, otp_code)
            return jsonify({"message": f"⚠️ Check terminal for OTP code."})
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@auth.route("/verify-sms-otp", methods=["POST"])
def verify_sms_otp():
    try:
        data = request.json
        phone_number = data.get('phone_number', '').strip()
        user_otp = data.get('otp', '').strip()
        
        stored_data = sms_otp_store.get(phone_number)
        if not stored_data:
            return jsonify({"message": "Request OTP first", "verified": False}), 400
        
        if datetime.utcnow() > stored_data['expires_at']:
            del sms_otp_store[phone_number]
            return jsonify({"message": "OTP expired", "verified": False}), 400
        
        stored_data['attempts'] += 1
        if stored_data['attempts'] > 3:
            del sms_otp_store[phone_number]
            return jsonify({"message": "Too many attempts", "verified": False}), 400
        
        if stored_data['otp'] == user_otp:
            del sms_otp_store[phone_number]
            return jsonify({"message": "OTP verified ✅", "verified": True})
        else:
            remaining = 3 - stored_data['attempts']
            return jsonify({"message": f"Invalid OTP. {remaining} attempts left.", "verified": False}), 400
            
    except Exception as e:
        return jsonify({"message": str(e), "verified": False}), 500


# ================= DEBUG =================

@auth.route("/users")
def get_users():
    db = DB.get_db()
    users = list(db.users.find())
    for u in users:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
    return jsonify(users)