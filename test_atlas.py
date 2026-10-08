from pymongo import MongoClient

password = "selvi160806"

uri = f"mongodb+srv://smartcart_user:{password}@cluster0.pwoc2qw.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)

client.admin.command("ping")

print("MongoDB Atlas connected successfully!")

db = client["ecommerce_db"]

print("Database:", db.name)
print("Collections:", db.list_collection_names())