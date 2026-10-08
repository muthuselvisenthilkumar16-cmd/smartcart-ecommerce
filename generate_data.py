from pymongo import MongoClient
import random
from datetime import datetime, timedelta

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
collection = db["orders"]

collection.delete_many({})

categories = ["Electronics", "Clothing", "Beauty", "Home", "Sports"]
products = [
    "Laptop", "Mobile", "Headphones", "T-Shirt", "Shoes",
    "Face Cream", "Sofa", "Mixer", "Cricket Bat", "Smart Watch"
]
payments = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery"]

data = []

for i in range(50000):
    quantity = random.randint(1, 5)
    price = random.randint(200, 80000)

    order = {
        "order_id": i + 1,
        "customer_id": random.randint(1001, 5000),
        "product_id": random.randint(101, 110),
        "product": random.choice(products),
        "category": random.choice(categories),
        "quantity": quantity,
        "price": price,
        "total_amount": quantity * price,
        "order_date": datetime.now() - timedelta(days=random.randint(0, 730)),
        "payment_method": random.choice(payments),
        "customer_age": random.randint(18, 60),
        "rating": random.randint(1, 5)
    }

    data.append(order)

    if len(data) == 1000:
        collection.insert_many(data)
        data = []

if data:
    collection.insert_many(data)

print("50,000 e-commerce orders inserted successfully!")
print("Total records:", collection.count_documents({}))

client.close()