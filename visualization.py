from pymongo import MongoClient
import matplotlib.pyplot as plt

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
collection = db["orders"]

# Category Revenue
data = collection.aggregate([
    {
        "$group": {
            "_id": "$category",
            "revenue": {"$sum": "$total_amount"}
        }
    },
    {"$sort": {"revenue": -1}}
])

categories = []
revenue = []

for x in data:
    categories.append(x["_id"])
    revenue.append(x["revenue"])

plt.figure(figsize=(8, 5))
plt.bar(categories, revenue)
plt.title("Revenue by Category")
plt.xlabel("Category")
plt.ylabel("Revenue")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# Top Products
data = collection.aggregate([
    {
        "$group": {
            "_id": "$product",
            "quantity": {"$sum": "$quantity"}
        }
    },
    {"$sort": {"quantity": -1}},
    {"$limit": 5}
])

products = []
quantity = []

for x in data:
    products.append(x["_id"])
    quantity.append(x["quantity"])

plt.figure(figsize=(8, 5))
plt.bar(products, quantity)
plt.title("Top 5 Products")
plt.xlabel("Product")
plt.ylabel("Quantity Sold")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

client.close()