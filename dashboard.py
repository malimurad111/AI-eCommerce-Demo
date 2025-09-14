import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import matplotlib.pyplot as plt

# --- Shopify Config ---
STORE_DOMAIN = "512mpk-48.myshopify.com"   # apna store domain
API_VERSION = "2025-07"
ACCESS_TOKEN = "YOUR_SHOPIFY_ADMIN_API_TOKEN"   # Shopify Admin API token

# --- Gemini Config ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Fetch Data from Shopify ---
def fetch_shopify_data(endpoint):
    url = f"https://{STORE_DOMAIN}/admin/api/{API_VERSION}/{endpoint}.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# --- AI Insight Generator ---
def get_ai_insight(data_text):
    try:
        prompt = f"Analyze the following eCommerce data and give a short business insight:\n\n{data_text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "⚠️ AI insight not available (fallback)."

# --- Streamlit Layout ---
st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")
st.title("📊 AI-Powered eCommerce Dashboard (Shopify + Gemini)")

# --- Products ---
products_data = fetch_shopify_data("products")
products = products_data.get("products", [])

# --- Customers ---
customers_data = fetch_shopify_data("customers")
customers = customers_data.get("customers", [])

# --- Orders ---
orders_data = fetch_shopify_data("orders")
orders = orders_data.get("orders", [])

# --- KPIs ---
total_products = len(products)
total_customers = len(customers)
total_orders = len(orders)
total_revenue = sum(float(o["total_price"]) for o in orders) if orders else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("🛍️ Products", total_products)
col2.metric("👥 Customers", total_customers)
col3.metric("📦 Orders", total_orders)
col4.metric("💰 Revenue", f"${total_revenue:,.2f}")

st.markdown("---")

# --- Products Table + AI ---
if products:
    products_df = pd.DataFrame([{
        "Product": p["title"],
        "Vendor": p["vendor"],
        "Status": p["status"]
    } for p in products])
    st.subheader("🛍️ Products")
    st.dataframe(products_df)

    ai_text = f"Total Products: {total_products}, Vendors: {products_df['Vendor'].nunique()}"
    st.info(get_ai_insight(ai_text))

# --- Customers Table + AI ---
if customers:
    customers_df = pd.DataFrame([{
        "Customer": f"{c.get('first_name','')} {c.get('last_name','')}",
        "Email": c.get("email"),
        "Orders": c.get("orders_count")
    } for c in customers])
    st.subheader("👥 Customers")
    st.dataframe(customers_df)

    returning_customers = sum(1 for c in customers if c["orders_count"] > 1)
    ai_text = f"Total Customers: {total_customers}, Returning: {returning_customers}"
    st.info(get_ai_insight(ai_text))

    # Chart: Orders per customer
    st.subheader("📈 Customer Orders Distribution")
    fig, ax = plt.subplots()
    customers_df["Orders"].value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_xlabel("Orders per Customer")
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)

# --- Orders Table + AI ---
if orders:
    orders_df = pd.DataFrame([{
        "Order ID": o["id"],
        "Customer": o.get("customer", {}).get("first_name", "Unknown"),
        "Total Price": float(o["total_price"])
    } for o in orders])
    st.subheader("📦 Orders")
    st.dataframe(orders_df)

    ai_text = f"Total Orders: {total_orders}, Revenue: {total_revenue}"
    st.info(get_ai_insight(ai_text))

    # Chart: Revenue Trend
    st.subheader("📊 Revenue Trend")
    fig, ax = plt.subplots()
    orders_df["Total Price"].plot(kind="line", marker="o", ax=ax)
    ax.set_xlabel("Order Index")
    ax.set_ylabel("Revenue ($)")
    st.pyplot(fig)

st.markdown("---")
st.success("✅ Dashboard live with KPIs, Charts & Gemini AI Insights")
