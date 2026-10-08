from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
collection = db["orders"]

total_orders = collection.count_documents({})

result = collection.aggregate([
    {
        "$group": {
            "_id": None,
            "revenue": {"$sum": "$total_amount"},
            "products_sold": {"$sum": "$quantity"}
        }
    }
])

summary = list(result)[0]

print("===== E-COMMERCE ANALYTICS =====")
print("Total Orders:", total_orders)
print("Total Products Sold:", summary["products_sold"])
print("Total Revenue: ₹", summary["revenue"])

print("\n===== TOP PRODUCTS =====")

products = collection.aggregate([
    {
        "$group": {
            "_id": "$product",
            "quantity": {"$sum": "$quantity"}
        }
    },
    {"$sort": {"quantity": -1}},
    {"$limit": 5}
])

for p in products:
    print(p["_id"], "-", p["quantity"], "units")

print("\n===== CATEGORY SALES =====")

categories = collection.aggregate([
    {
        "$group": {
            "_id": "$category",
            "revenue": {"$sum": "$total_amount"}
        }
    },
    {"$sort": {"revenue": -1}}
])

for c in categories:
    print(c["_id"], "- ₹", c["revenue"])

client.close()