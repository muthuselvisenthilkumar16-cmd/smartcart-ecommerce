from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["ecommerce_db"]
collection = db["orders"]

print("MongoDB Connected Successfully!")
print("Database:", db.name)
print("Collection:", collection.name)

client.close()
