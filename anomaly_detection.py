from pymongo import MongoClient
import pandas as pd
from sklearn.ensemble import IsolationForest

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]

orders = db["orders"]
anomalies = db["anomalies"]

data = list(orders.find({}, {"_id": 0}))
df = pd.DataFrame(data)

features = [
    "quantity",
    "price",
    "total_amount",
    "customer_age",
    "rating"
]

model = IsolationForest(
    contamination=0.02,
    random_state=42
)

df["anomaly"] = model.fit_predict(df[features])

df["status"] = df["anomaly"].map({
    1: "Normal",
    -1: "Suspicious"
})

anomaly_data = df[df["status"] == "Suspicious"].copy()

anomalies.delete_many({})

if not anomaly_data.empty:
    anomalies.insert_many(
        anomaly_data.to_dict("records")
    )

print("===== ANOMALY DETECTION =====")
print("Total orders:", len(df))
print("Suspicious orders:", len(anomaly_data))
print("Normal orders:", len(df) - len(anomaly_data))

print("\nSuspicious orders saved to MongoDB.")

client.close()