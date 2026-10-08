from pymongo import MongoClient
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]
orders = db["orders"]
customers = db["customers"]

data = list(orders.find({}, {"_id": 0}))
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

scaler = StandardScaler()
X = scaler.fit_transform(customer_data[features])

model = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

customer_data["cluster"] = model.fit_predict(X)

cluster_spending = customer_data.groupby("cluster")["total_spending"].mean()

sorted_clusters = cluster_spending.sort_values(ascending=False).index.tolist()

labels = {
    sorted_clusters[0]: "VIP",
    sorted_clusters[1]: "Regular",
    sorted_clusters[2]: "Occasional"
}

customer_data["segment"] = customer_data["cluster"].map(labels)

customers.delete_many({})

records = customer_data.to_dict("records")

if records:
    customers.insert_many(records)

print("===== CUSTOMER SEGMENTATION =====")

print(
    customer_data["segment"]
    .value_counts()
)

print("\nCustomer segments saved to MongoDB.")

client.close()