"""
admin_routes.py
===============
Admin Panel Backend Routes.
Only two hardcoded admin emails are allowed access.
"""

from flask import Blueprint, request, jsonify, render_template
from config import DB
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict

admin_bp = Blueprint("admin", __name__)

# ── Hardcoded admin emails ─────────────────────────────────────────────────────
ADMIN_EMAILS = {
    "zihadmuzahid2003@gmail.com",
    "md.soheleleven05@gmail.com",
}


def is_admin(user_id: str) -> bool:
    """Check if the given user_id belongs to an admin."""
    try:
        db = DB.get_db()
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return user and user.get("email", "").lower() in ADMIN_EMAILS
    except Exception as e:
        print(f"Admin check error: {e}")
        return False


def require_admin(fn):
    """Decorator: JWT required + admin check."""
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return jsonify({"message": "Admin access only ❌"}), 403
        return fn(*args, **kwargs)

    return wrapper


# ── Admin Panel Page ──────────────────────────────────────────────────────────

@admin_bp.route("/admin")
def admin_page():
    return render_template("admin.html")


# ── Dashboard Stats ───────────────────────────────────────────────────────────

@admin_bp.route("/admin/stats", methods=["GET"])
@require_admin
def admin_stats():
    try:
        db = DB.get_db()
        
        total_users     = db.users.count_documents({})
        total_bookings  = db.bookings.count_documents({})
        confirmed       = db.bookings.count_documents({"status": "CONFIRMED"})
        cancelled       = db.bookings.count_documents({"status": "CANCELLED"})

        # Revenue from confirmed bookings only
        pipeline = [
            {"$match": {"status": "CONFIRMED"}},
            {"$group": {"_id": None, "total": {"$sum": "$payment.amount"}}}
        ]
        rev_result = list(db.bookings.aggregate(pipeline))
        total_revenue = rev_result[0]["total"] if rev_result else 0

        # Bookings by transport type
        type_pipeline = [
            {"$group": {"_id": "$ticket.type", "count": {"$sum": 1}}}
        ]
        by_type = {}
        for doc in db.bookings.aggregate(type_pipeline):
            if doc["_id"]:
                by_type[doc["_id"]] = doc["count"]

        # Bookings by payment method
        pay_pipeline = [
            {"$group": {"_id": "$payment.method", "count": {"$sum": 1}}}
        ]
        by_payment = {}
        for doc in db.bookings.aggregate(pay_pipeline):
            if doc["_id"]:
                by_payment[doc["_id"]] = doc["count"]

        # Last 7 days bookings
        seven_days = []
        for i in range(6, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            count = db.bookings.count_documents({
                "booked_at": {"$regex": f"^{day_str}"}
            })
            seven_days.append({"date": day_str, "count": count})

        # Recent 5 bookings
        recent = list(
            db.bookings
            .find({}, {"user_id": 1, "ticket": 1, "operator": 1,
                       "journey_date": 1, "seat_no": 1, "payment": 1,
                       "status": 1, "booked_at": 1})
            .sort("booked_at", -1)
            .limit(5)
        )
        for r in recent:
            r["_id"] = str(r["_id"])
            if "booked_at" in r and isinstance(r["booked_at"], datetime):
                r["booked_at"] = r["booked_at"].isoformat()

        return jsonify({
            "total_users":    total_users,
            "total_bookings": total_bookings,
            "confirmed":      confirmed,
            "cancelled":      cancelled,
            "total_revenue":  total_revenue,
            "by_type":        by_type,
            "by_payment":     by_payment,
            "last_7_days":    seven_days,
            "recent_bookings": recent,
        })

    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({"message": str(e)}), 500


# ── All Users ────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/users", methods=["GET"])
@require_admin
def admin_users():
    try:
        db = DB.get_db()
        search = request.args.get("search", "").strip()
        query = {}
        if search:
            query = {"$or": [
                {"name":  {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]}

        users = list(
            db.users
            .find(query, {"password": 0})
            .sort("created_at", -1)
        )
        for u in users:
            u["_id"] = str(u["_id"])
            # Count bookings per user
            u["booking_count"] = db.bookings.count_documents({"user_id": str(u["_id"])})
            u["is_admin"] = u.get("email", "").lower() in ADMIN_EMAILS
            if "created_at" in u and isinstance(u["created_at"], datetime):
                u["created_at"] = u["created_at"].isoformat()

        return jsonify(users)

    except Exception as e:
        print(f"Users error: {e}")
        return jsonify({"message": str(e)}), 500


# ── Delete User ───────────────────────────────────────────────────────────────

@admin_bp.route("/admin/users/<user_id>", methods=["DELETE"])
@require_admin
def delete_user(user_id):
    try:
        db = DB.get_db()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"message": "User not found ❌"}), 404

        if user.get("email", "").lower() in ADMIN_EMAILS:
            return jsonify({"message": "Cannot delete an admin account ❌"}), 403

        db.users.delete_one({"_id": ObjectId(user_id)})
        db.bookings.delete_many({"user_id": user_id})
        db.notifications.delete_many({"user_id": user_id})

        return jsonify({"message": "User deleted successfully ✅"})

    except Exception as e:
        print(f"Delete user error: {e}")
        return jsonify({"message": str(e)}), 500


# ── All Bookings ──────────────────────────────────────────────────────────────

@admin_bp.route("/admin/bookings", methods=["GET"])
@require_admin
def admin_bookings():
    try:
        db = DB.get_db()
        search     = request.args.get("search", "").strip()
        transport  = request.args.get("type", "").strip()
        status     = request.args.get("status", "").strip()
        page       = int(request.args.get("page", 1))
        per_page   = int(request.args.get("per_page", 20))

        query = {}
        if transport:
            query["ticket.type"] = {"$regex": transport, "$options": "i"}
        if status:
            query["status"] = status.upper()
        if search:
            query["$or"] = [
                {"operator":    {"$regex": search, "$options": "i"}},
                {"seat_no":     {"$regex": search, "$options": "i"}},
                {"journey_date":{"$regex": search, "$options": "i"}},
                {"ticket.source":      {"$regex": search, "$options": "i"}},
                {"ticket.destination": {"$regex": search, "$options": "i"}},
            ]

        total = db.bookings.count_documents(query)
        bookings = list(
            db.bookings
            .find(query)
            .sort("booked_at", -1)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
        for b in bookings:
            b["_id"] = str(b["_id"])
            if "booked_at" in b and isinstance(b["booked_at"], datetime):
                b["booked_at"] = b["booked_at"].isoformat()

        return jsonify({
            "bookings": bookings,
            "total":    total,
            "page":     page,
            "pages":    max(1, -(-total // per_page)),
        })

    except Exception as e:
        print(f"Bookings error: {e}")
        return jsonify({"message": str(e)}), 500


# ── Cancel Booking ────────────────────────────────────────────────────────────

@admin_bp.route("/admin/bookings/<booking_id>/cancel", methods=["POST"])
@require_admin
def cancel_booking(booking_id):
    try:
        db = DB.get_db()
        result = db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": "CANCELLED", "cancelled_at": datetime.utcnow().isoformat()}}
        )
        if result.matched_count == 0:
            return jsonify({"message": "Booking not found ❌"}), 404

        return jsonify({"message": "Booking cancelled ✅"})

    except Exception as e:
        print(f"Cancel error: {e}")
        return jsonify({"message": str(e)}), 500


# ── Delete Booking ────────────────────────────────────────────────────────────

@admin_bp.route("/admin/bookings/<booking_id>", methods=["DELETE"])
@require_admin
def delete_booking(booking_id):
    try:
        db = DB.get_db()
        result = db.bookings.delete_one({"_id": ObjectId(booking_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "Booking not found ❌"}), 404

        return jsonify({"message": "Booking deleted ✅"})

    except Exception as e:
        print(f"Delete booking error: {e}")
        return jsonify({"message": str(e)}), 500


# ── Revenue Report ────────────────────────────────────────────────────────────

@admin_bp.route("/admin/revenue", methods=["GET"])
@require_admin
def admin_revenue():
    try:
        db = DB.get_db()
        # Monthly revenue for the last 6 months
        monthly = []
        for i in range(5, -1, -1):
            d = datetime.utcnow() - timedelta(days=i * 30)
            month_str = d.strftime("%Y-%m")
            pipeline = [
                {"$match": {"booked_at": {"$regex": f"^{month_str}"}, "status": "CONFIRMED"}},
                {"$group": {"_id": None, "revenue": {"$sum": "$payment.amount"}, "count": {"$sum": 1}}}
            ]
            result = list(db.bookings.aggregate(pipeline))
            monthly.append({
                "month":   d.strftime("%b %Y"),
                "revenue": result[0]["revenue"] if result else 0,
                "count":   result[0]["count"]   if result else 0,
            })

        # Revenue by transport
        by_type_pipeline = [
            {"$match": {"status": "CONFIRMED"}},
            {"$group": {"_id": "$ticket.type", "revenue": {"$sum": "$payment.amount"}, "count": {"$sum": 1}}}
        ]
        by_type = [
            {"type": d["_id"], "revenue": d["revenue"], "count": d["count"]}
            for d in db.bookings.aggregate(by_type_pipeline) if d["_id"]
        ]

        return jsonify({"monthly": monthly, "by_type": by_type})

    except Exception as e:
        print(f"Revenue error: {e}")
        return jsonify({"message": str(e)}), 500


# ── Admin Notifications Broadcast ────────────────────────────────────────────

@admin_bp.route("/admin/broadcast", methods=["POST"])
@require_admin
def broadcast_notification():
    try:
        db = DB.get_db()
        data    = request.json or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"message": "Message is required ❌"}), 400

        users = list(db.users.find({}, {"_id": 1}))
        now   = datetime.utcnow().isoformat()
        notifs = [
            {
                "user_id":    str(u["_id"]),
                "message":    message,
                "type":       "admin_broadcast",
                "read":       False,
                "created_at": now,
            }
            for u in users
        ]
        if notifs:
            db.notifications.insert_many(notifs)

        return jsonify({"message": f"Broadcast sent to {len(notifs)} users ✅"})

    except Exception as e:
        print(f"Broadcast error: {e}")
        return jsonify({"message": str(e)}), 500