from config import DB

class Booking:
    @staticmethod
    def create(data):
        db = DB.get_db()
        return db.bookings.insert_one(data)