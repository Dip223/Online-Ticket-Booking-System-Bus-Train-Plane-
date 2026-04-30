"""
config.py
=========
TRUE SINGLETON PATTERN for MongoDB Connection.

A Singleton ensures a class has ONLY ONE instance and provides
a global access point to it. This is implemented using:
  - A private class-level _instance variable
  - __new__() method override to control instantiation
  - Thread safety through class-level lock (optional for Flask)

This is NOT a simple static method — it uses __new__ which is
the true Python way to implement Singleton.
"""

from pymongo import MongoClient
import threading

# Email credentials (replace with your real Gmail App Password)
EMAIL    = "zihadmuzahid2003@gmail.com"
PASSWORD = "luzwnlvtmsfhlzxt"

# JWT Secret Key
JWT_SECRET = "bdticket_super_secret_jwt_2024"


class SingletonMeta(type):
    """
    Thread-safe Singleton Metaclass.
    Any class using this metaclass as its __metaclass__
    will be a Singleton automatically.
    """
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseConnection(metaclass=SingletonMeta):
    """
    Singleton Database Connection class.

    Because SingletonMeta is used, no matter how many times
    DatabaseConnection() is called, only ONE object is created.

    Usage:
        db = DatabaseConnection().get_database()
        db.users.find_one(...)
    """

    def __init__(self):
        # This runs ONCE in the whole application lifetime
        self._client = MongoClient("mongodb://localhost:27017/")
        self._database = self._client["bdticket_db"]
        print("✅ [Singleton] MongoDB connection established — only once.")

    def get_database(self):
        """Return the single shared database object."""
        return self._database

    def get_collection(self, name: str):
        """Return a specific collection by name."""
        return self._database[name]

    def close(self):
        """Close the MongoDB connection."""
        self._client.close()


# ── Convenience accessor ──────────────────────────────────────────────────────
# All routes use DB.get_db() which internally calls the Singleton
class DB:
    @staticmethod
    def get_db():
        return DatabaseConnection().get_database()

    @staticmethod
    def users():
        return DatabaseConnection().get_collection("users")

    @staticmethod
    def bookings():
        return DatabaseConnection().get_collection("bookings")

    @staticmethod
    def otps():
        return DatabaseConnection().get_collection("otps")

    @staticmethod
    def notifications():
        return DatabaseConnection().get_collection("notifications")
