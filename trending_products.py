from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]

orders = db["orders"]
trending = db["trending_products"]

data = list(orders.find({}, {"_id": 0}))
df = pd.DataFrame(data)

df["order_date"] = pd.to_datetime(df["order_date"])

latest_date = df["order_date"].max()

recent_start = latest_date - pd.Timedelta(days=7)
previous_start = latest_date - pd.Timedelta(days=14)

recent = df[
    df["order_date"] >= recent_start
]

previous = df[
    (df["order_date"] >= previous_start) &
    (df["order_date"] < recent_start)
]

recent_sales = recent.groupby(
    "product"
)["quantity"].sum()

previous_sales = previous.groupby(
    "product"
)["quantity"].sum()

trend = pd.DataFrame({
    "recent_sales": recent_sales,
    "previous_sales": previous_sales
}).fillna(0)

trend["growth"] = (
    (trend["recent_sales"] - trend["previous_sales"])
    / trend["previous_sales"].replace(0, 1)
) * 100

trend = trend.sort_values(
    "growth",
    ascending=False
)

trend["growth"] = trend["growth"].round(2)

trending.delete_many({})

records = trend.reset_index().to_dict("records")

if records:
    trending.insert_many(records)

print("===== TRENDING PRODUCTS =====")

print(
    trend.head(10)
)

print("\nTrending products saved to MongoDB.")

client.close()