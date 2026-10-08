import streamlit as st
from pymongo import MongoClient
import pandas as pd
from sklearn.ensemble import IsolationForest

# ================= CONNECTION =================

client = MongoClient(st.secrets["MONGO_URI"])
db = client["ecommerce_db"]

orders = db["orders"]
customers = db["customers"]
anomalies = db["anomalies"]
recommendations = db["recommendations"]

data = list(orders.find({}, {"_id": 0}))
df = pd.DataFrame(data)

# ================= PAGE =================

st.set_page_config(
    page_title="SmartCart",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SmartCart")
st.subheader("E-Commerce Big Data Intelligence System")

st.markdown("---")

# ================= KPI =================

total_orders = len(df)
total_revenue = df["total_amount"].sum()
products_sold = df["quantity"].sum()
average_rating = df["rating"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col3.metric("Products Sold", f"{products_sold:,}")
col4.metric("Average Rating", f"{average_rating:.2f} ⭐")

st.markdown("---")

# ================= CUSTOMER SEARCH =================

st.header("🔎 Customer Search")

customer_id = st.number_input(
    "Enter Customer ID",
    min_value=1,
    step=1
)

if st.button("Search Customer"):

    customer = customers.find_one(
        {"customer_id": customer_id},
        {"_id": 0}
    )

    if customer:

        st.success("Customer Found!")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Customer ID",
            customer["customer_id"]
        )

        c2.metric(
            "Total Spending",
            f"₹{customer['total_spending']:,.2f}"
        )

        c3.metric(
            "Total Orders",
            customer["total_orders"]
        )

        st.info(
            f"Customer Segment: {customer['segment']}"
        )

    else:
        st.error("Customer not found.")

# ================= SALES ANALYTICS =================

st.header("📊 Sales Analytics")

category_sales = df.groupby(
    "category"
)["total_amount"].sum().sort_values(
    ascending=False
)

st.bar_chart(category_sales)

# ================= TOP PRODUCTS =================

st.header("🏆 Top Products")

top_products = df.groupby(
    "product"
)["total_amount"].sum().sort_values(
    ascending=False
).head(10)

st.bar_chart(top_products)
# ================= TRENDING PRODUCTS =================

trending = db["trending_products"]
trending_data = list(trending.find({}, {"_id": 0}))

st.markdown(
    '<p class="section">🔥 Trending Products</p>',
    unsafe_allow_html=True
)

if trending_data:

    trending_df = pd.DataFrame(trending_data)

    top_trending = trending_df.head(5)

    cols = st.columns(len(top_trending))

    for col, (_, row) in zip(cols, top_trending.iterrows()):

        growth = row["growth"]

        col.metric(
            row["product"],
            f"{growth:.1f}%",
            f"{int(row['recent_sales'])} units"
        )

    st.dataframe(
        trending_df[
            ["product", "recent_sales", "previous_sales", "growth"]
        ],
        use_container_width=True
    )

else:
    st.info("No trending product data available.")

# ================= PRODUCT RECOMMENDATION =================

st.header("🎯 Product Recommendation")

product_list = sorted(
    df["product"].unique()
)

selected_product = st.selectbox(
    "Select a product",
    product_list
)

if st.button("Get Recommendations"):

    recommendation = recommendations.find_one(
        {"product": selected_product},
        {"_id": 0}
    )

    if recommendation:

        st.success(
            f"Customers who buy {selected_product} may also like:"
        )

        for item in recommendation[
            "recommended_products"
        ]:

            st.write(
                f"🛍️ **{item['product']}** "
                f"— Similarity: {item['similarity']}"
            )

    else:
        st.warning("No recommendations found.")

# ================= ORDER CALCULATOR =================

st.header("🧾 Order Calculator")

col1, col2 = st.columns(2)

with col1:

    price = st.number_input(
        "Product Price",
        min_value=0.0,
        value=1000.0,
        step=100.0
    )

with col2:

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=1,
        step=1
    )

total = price * quantity

st.metric(
    "Total Order Amount",
    f"₹{total:,.2f}"
)

# ================= ANOMALY CHECK =================

st.header("🚨 Order Anomaly Detection")

col1, col2, col3 = st.columns(3)

with col1:

    anomaly_quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=1,
        step=1,
        key="anomaly_quantity"
    )

with col2:

    anomaly_price = st.number_input(
        "Price",
        min_value=0.0,
        value=1000.0,
        step=100.0,
        key="anomaly_price"
    )

with col3:

    anomaly_rating = st.number_input(
        "Rating",
        min_value=1.0,
        max_value=5.0,
        value=4.0,
        step=0.1
    )

anomaly_age = st.number_input(
    "Customer Age",
    min_value=1,
    max_value=100,
    value=25
)

if st.button("Check Order"):

    input_data = pd.DataFrame({
        "quantity": [anomaly_quantity],
        "price": [anomaly_price],
        "total_amount": [
            anomaly_quantity * anomaly_price
        ],
        "customer_age": [anomaly_age],
        "rating": [anomaly_rating]
    })

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

    model.fit(df[features])

    prediction = model.predict(input_data[features])

    if prediction[0] == -1:

        st.error(
            "⚠️ Suspicious Order Detected!"
        )

    else:

        st.success(
            "✅ Order appears to be Normal."
        )

# ================= CUSTOMER SEGMENTS =================

st.header("👥 Customer Segmentation")

customer_data = list(
    customers.find({}, {"_id": 0})
)

if customer_data:

    customer_df = pd.DataFrame(customer_data)

    segment_count = customer_df[
        "segment"
    ].value_counts()

    st.bar_chart(segment_count)

# ================= PAYMENT ANALYTICS =================

st.header("💳 Payment Analytics")

payment_data = df[
    "payment_method"
].value_counts()

st.bar_chart(payment_data)

# ================= RECENT ORDERS =================

st.header("🛒 Recent Orders")

st.dataframe(
    df.tail(20),
    use_container_width=True
)

st.markdown("---")

st.success(
    "SmartCart Big Data Intelligence System is running successfully!"
)