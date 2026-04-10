from pymongo import MongoClient

class DB:
    _instance = None

    @staticmethod
    def get_db():
        if DB._instance is None:
            client = MongoClient("mongodb://localhost:27017/")
            DB._instance = client["ticket_system"]
        return DB._instance

# Email config
EMAIL = "zihadmuzahid2003@gmail.com"
PASSWORD = "xfevsdjdqhzszwoi"