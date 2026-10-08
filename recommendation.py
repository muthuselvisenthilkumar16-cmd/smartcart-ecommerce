from pymongo import MongoClient
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]

orders = db["orders"]
recommendations = db["recommendations"]

data = list(orders.find({}, {"_id": 0}))
df = pd.DataFrame(data)

customer_product = pd.pivot_table(
    df,
    values="quantity",
    index="customer_id",
    columns="product",
    aggfunc="sum",
    fill_value=0
)

similarity = cosine_similarity(customer_product.T)

product_names = customer_product.columns

recommendations.delete_many({})

records = []

for i, product in enumerate(product_names):

    similar_products = list(
        enumerate(similarity[i])
    )

    similar_products = sorted(
        similar_products,
        key=lambda x: x[1],
        reverse=True
    )

    top_products = []

    for index, score in similar_products[1:4]:
        top_products.append({
            "product": product_names[index],
            "similarity": round(float(score), 3)
        })

    records.append({
        "product": product,
        "recommended_products": top_products
    })

if records:
    recommendations.insert_many(records)

print("===== PRODUCT RECOMMENDATION =====")

for record in records[:5]:
    print("\nProduct:", record["product"])
    print("Recommended:")

    for item in record["recommended_products"]:
        print(
            " ",
            item["product"],
            "->",
            item["similarity"]
        )

print("\nRecommendations saved to MongoDB.")

client.close()