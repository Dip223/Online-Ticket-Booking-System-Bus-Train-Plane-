from flask import Blueprint, request, jsonify, render_template
from models.email_sender import send_email
from config import DB
import random

auth = Blueprint("auth", __name__)

# ================== MEMORY STORE ==================
otp_store = {}

# ================== PAGES ==================

@auth.route('/')
def home():
    return render_template("login.html")


@auth.route('/register-page')
def register_page():
    return render_template("register.html")


@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@auth.route('/forgot')
def forgot_page():
    return render_template("forgot.html")


# ===== NEW PAGES (IMPORTANT) =====

@auth.route('/bus')
def bus_page():
    return render_template("bus.html")


@auth.route('/train')
def train_page():
    return render_template("train.html")


@auth.route('/plane')
def plane_page():
    return render_template("plane.html")


# ================== REGISTER ==================

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    db = DB.get_db()

    # Save user
    db.users.insert_one({
        "name": data['name'],
        "email": data['email'],
        "password": data['password']
    })

    # Send welcome email
    send_email(
        data['email'],
        "Welcome 🎉",
        f"Hello {data['name']}, your account is created!"
    )

    return jsonify({"message": "Registered + Email Sent"})


# ================== LOGIN ==================

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    db = DB.get_db()

    user = db.users.find_one({
        "email": data['email'],
        "password": data['password']
    })

    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user)

    return jsonify({"message": "Invalid login"})


# ================== USERS DEBUG ==================

@auth.route('/users')
def get_users():
    db = DB.get_db()
    users = list(db.users.find())

    for u in users:
        u['_id'] = str(u['_id'])

    return users


# ================== OTP SYSTEM ==================

@auth.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data['email']

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    send_email(email, "Your OTP", f"Your OTP is: {otp}")

    return {"message": "OTP sent"}


@auth.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data['email']
    otp = data['otp']

    if otp_store.get(email) == otp:
        return {"message": "Verified ✅"}

    return {"message": "Wrong OTP ❌"}


# ================== PASSWORD RESET ==================

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data['email']

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    send_email(email, "Reset OTP", f"Your reset OTP is: {otp}")

    return {"message": "Reset OTP sent"}


@auth.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data['email']
    otp = data['otp']
    new_password = data['password']

    if otp_store.get(email) == otp:
        db = DB.get_db()

        db.users.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
        )

        return {"message": "Password updated ✅"}

    return {"message": "Invalid OTP ❌"}