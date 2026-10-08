from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]

orders = db["orders"]

data = list(orders.find({}, {"_id": 0}))
df = pd.DataFrame(data)

df["order_date"] = pd.to_datetime(df["order_date"])

daily_sales = df.groupby(
    df["order_date"].dt.date
)["total_amount"].sum().reset_index()

daily_sales.columns = ["date", "revenue"]

daily_sales["date"] = pd.to_datetime(daily_sales["date"])

daily_sales["day_number"] = range(len(daily_sales))

X = daily_sales[["day_number"]]
y = daily_sales["revenue"]

model = LinearRegression()
model.fit(X, y)

future_days = 7

last_day = daily_sales["day_number"].max()

future = pd.DataFrame({
    "day_number": range(
        last_day + 1,
        last_day + future_days + 1
    )
})

future["predicted_revenue"] = model.predict(
    future[["day_number"]]
)

future["date"] = pd.date_range(
    daily_sales["date"].max() + pd.Timedelta(days=1),
    periods=future_days
)

print("===== SALES FORECAST =====")

for _, row in future.iterrows():
    print(
        row["date"].strftime("%Y-%m-%d"),
        "->",
        round(row["predicted_revenue"], 2)
    )

plt.figure(figsize=(10, 5))

plt.plot(
    daily_sales["date"],
    daily_sales["revenue"],
    label="Actual Revenue"
)

plt.plot(
    future["date"],
    future["predicted_revenue"],
    marker="o",
    label="Predicted Revenue"
)

plt.xlabel("Date")
plt.ylabel("Revenue")
plt.title("E-Commerce Sales Forecast")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

client.close()