from pymongo import MongoClient

class DB:
    @staticmethod
    def get_db():
        client = MongoClient("mongodb://localhost:27017/")
        return client["ticket_system"]

# Email config
EMAIL = "zihadmuzahid2003@gmail.com"
PASSWORD = "luzwnlvtmsfhlzxt"
# JWT Secret
JWT_SECRET = "supersecretkey123"