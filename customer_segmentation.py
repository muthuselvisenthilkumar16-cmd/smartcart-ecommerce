from pymongo import MongoClient
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
collection = db["orders"]

data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)

customer_data = df.groupby("customer_id").agg(
    total_spending=("total_amount", "sum"),
    total_orders=("order_id", "count"),
    total_quantity=("quantity", "sum"),
    average_rating=("rating", "mean")
).reset_index()

features = [
    "total_spending",
    "total_orders",
    "total_quantity"
]

X = customer_data[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

customer_data["cluster"] = model.fit_predict(X_scaled)

cluster_summary = customer_data.groupby("cluster")[features].mean()

print("===== CUSTOMER SEGMENTS =====")
print(cluster_summary)

print("\n===== CUSTOMER COUNTS =====")
print(customer_data["cluster"].value_counts().sort_index())

plt.figure(figsize=(8, 5))

plt.scatter(
    customer_data["total_orders"],
    customer_data["total_spending"],
    c=customer_data["cluster"]
)

plt.xlabel("Total Orders")
plt.ylabel("Total Spending")
plt.title("Customer Segmentation")

plt.show()

client.close()