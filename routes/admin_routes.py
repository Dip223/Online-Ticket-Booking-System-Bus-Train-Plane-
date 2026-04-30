from flask import Blueprint, request, jsonify, render_template
from config import DB
from datetime import datetime
from bson import ObjectId

admin_bp = Blueprint("admin", __name__)

ADMIN_EMAIL    = "admin@bdticket.com"
ADMIN_PASSWORD = "admin123"   # change in production


# ── Admin page ────────────────────────────────────────────────────────────────

@admin_bp.route("/admin")
def admin_page():
    return render_template("admin.html")


# ── Admin login ───────────────────────────────────────────────────────────────

@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    if data.get("email") == ADMIN_EMAIL and data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True, "message": "Admin logged in ✅"})
    return jsonify({"success": False, "message": "Invalid credentials ❌"}), 401


# ── Stats ─────────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/stats")
def admin_stats():
    total_users    = DB.users().count_documents({})
    total_bookings = DB.bookings().count_documents({})
    bus_count      = DB.bookings().count_documents({"ticket.type": "Bus"})
    train_count    = DB.bookings().count_documents({"ticket.type": "Train"})
    plane_count    = DB.bookings().count_documents({"ticket.type": "Plane"})

    # Revenue
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$ticket.price"}}}]
    rev      = list(DB.bookings().aggregate(pipeline))
    revenue  = rev[0]["total"] if rev else 0

    return jsonify({
        "total_users":    total_users,
        "total_bookings": total_bookings,
        "bus_count":      bus_count,
        "train_count":    train_count,
        "plane_count":    plane_count,
        "revenue":        revenue,
    })


# ── All users ─────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/users")
def admin_users():
    users = list(DB.users().find())
    for u in users:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
    return jsonify(users)


# ── All bookings ──────────────────────────────────────────────────────────────

@admin_bp.route("/admin/bookings")
def admin_bookings():
    bookings = list(DB.bookings().find().sort("booked_at", -1).limit(100))
    for b in bookings:
        b["_id"] = str(b["_id"])
    return jsonify(bookings)


# ── Delete user ───────────────────────────────────────────────────────────────

@admin_bp.route("/admin/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        DB.users().delete_one({"_id": ObjectId(user_id)})
        return jsonify({"message": "User deleted ✅"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500