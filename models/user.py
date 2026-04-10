from config import DB

class User:
    @staticmethod
    def register(data):
        db = DB.get_db()
        data['verified'] = False
        return db.users.insert_one(data)

    @staticmethod
    def verify(email):
        db = DB.get_db()
        db.users.update_one({"email": email}, {"$set": {"verified": True}})