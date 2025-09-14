# dashboard_premium.py
import os
import io
import json
import time
import random
import base64
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px

# Optional (install only if using Gemini)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Premium AI eCommerce Dashboard", layout="wide", initial_sidebar_state="expanded")

APP_TITLE = "Premium AI eCommerce Dashboard"
st.title(APP_TITLE)

# ----------------------------
# Helper: load dummy data (or replace with Shopify fetch)
# ----------------------------
def load_dummy_data():
    products = [
        {"id":101,"title":"Smart Watch","category":"Wearables","price":50,"units_sold":120,"revenue":6000,"date":"2025-08-01"},
        {"id":102,"title":"Wireless Earbuds","category":"Audio","price":50,"units_sold":200,"revenue":10000,"date":"2025-08-05"},
        {"id":103,"title":"Bluetooth Speaker","category":"Audio","price":30,"units_sold":150,"revenue":4500,"date":"2025-08-10"},
        {"id":104,"title":"Fitness Tracker","category":"Wearables","price":30,"units_sold":90,"revenue":2700,"date":"2025-08-20"},
        {"id":105,"title":"Gaming Mouse","category":"Gaming","price":50,"units_sold":75,"revenue":3750,"date":"2025-08-25"},
    ]
    # create orders synthetic (one row per order item with date)
    orders = []
    for p in products:
        for i in range(int(p["units_sold"]//10)):
            orders.append({
                "order_id": f"O{p['id']}-{i}",
                "product": p["title"],
                "quantity": 10,
                "price": p["price"],
                "amount": 10 * p["price"],
                "date": p["date"]
            })
    customers = [
        {"id": 1, "name":"Ali", "email":"ali@example.com", "orders":5, "first_order":"2025-06-01"},
        {"id": 2, "name":"Sara", "email":"sara@example.com","orders":2,"first_order":"2025-07-10"},
        {"id": 3, "name":"Ahmed", "email":"ahmed@example.com","orders":1,"first_order":"2025-08-12"},
    ]
    products_df = pd.DataFrame(products)
    orders_df = pd.DataFrame(orders)
    customers_df = pd.DataFrame(customers)
    # convert dates
    orders_df["date"] = pd.to_datetime(orders_df["date"])
    return products_df, orders_df, customers_df

# ----------------------------
# Sidebar: Settings / Filters
# ----------------------------
st.sidebar.header("Settings & Data")
use_shopify = st.sidebar.checkbox("Use Shopify (swap dummy data)", value=False)
use_gemini = st.sidebar.checkbox("Enable Gemini AI Insights", value=False)
if use_gemini and not GEMINI_AVAILABLE:
    st.sidebar.warning("google-generativeai not installed — Gemini disabled")
    use_gemini = False

# Optional secrets (recommended to set as env vars)
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")  # mystore.myshopify.com
SHOPIFY_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if use_gemini and GEMINI_AVAILABLE and GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Quick authentication (demo only)
st.sidebar.markdown("### Access (demo)")
password = st.sidebar.text_input("Enter app password", type="password")
# replace "demo123" with env var or proper auth in production
if password != "" and password != os.getenv("DASHBOARD_PASS", "demo123"):
    st.sidebar.error("Incorrect password (demo). Use demo123 or set DASHBOARD_PASS env var.")
    st.stop()

# Date range filter
st.sidebar.markdown("---")
today = datetime.utcnow().date()
start_date = st.sidebar.date_input("Start date", value=today - timedelta(days=30))
end_date = st.sidebar.date_input("End date", value=today)
if start_date > end_date:
    st.sidebar.error("Start date must be before end date")
    st.stop()

top_n = st.sidebar.slider("Top N products", min_value=3, max_value=20, value=5)
category_filter = st.sidebar.multiselect("Category (filter)", options=["Wearables","Audio","Gaming"], default=[])

# Load data (dummy or Shopify)
if use_shopify and SHOPIFY_STORE and SHOPIFY_TOKEN:
    # placeholder: replace with actual Shopify fetch function
    st.sidebar.info("Shopify integration enabled (ensure SHOPIFY_* env vars set). Using dummy fetch for demo.")
    products_df, orders_df, customers_df = load_dummy_data()
else:
    products_df, orders_df, customers_df = load_dummy_data()

# Apply date filter on orders and recompute aggregates
orders_df = orders_df[(orders_df["date"].dt.date >= start_date) & (orders_df["date"].dt.date <= end_date)]
# Recompute product aggregates from orders (safe)
product_agg = orders_df.groupby("product").agg(units_sold=("quantity","sum"), revenue=("amount","sum")).reset_index()
# Merge with product info if exists
if "title" in products_df.columns:
    merged = pd.merge(products_df, product_agg, left_on="title", right_on="product", how="left")
    merged["units_sold"] = merged["units_sold"].fillna(0).astype(int)
    merged["revenue_y"] = merged["revenue"].fillna(0)
    merged = merged.rename(columns={"revenue_y":"revenue_from_orders"})
else:
    merged = product_agg.rename(columns={"product":"title"})

if category_filter:
    merged = merged[merged["category"].isin(category_filter)]

merged = merged.sort_values(by="units_sold", ascending=False)
top_products = merged.head(top_n)

# ----------------------------
# Top area: KPIs (cards)
# ----------------------------
total_revenue = orders_df["amount"].sum() if not orders_df.empty else products_df["revenue"].sum()
total_orders = orders_df["order_id"].nunique() if not orders_df.empty else len(orders_df)
total_units = merged["units_sold"].sum()
new_customers = customers_df.shape[0]  # demo logic
returning_customers = customers_df[customers_df["orders"]>1].shape[0]

k1, k2, k3, k4, k5 = st.columns([2,2,2,2,2])
k1.metric("💰 Revenue", f"${total_revenue:,.2f}")
k2.metric("📦 Orders", f"{total_orders}")
k3.metric("📊 Units Sold", f"{total_units}")
k4.metric("🆕 New Customers", f"{new_customers}")
k5.metric("🔁 Returning", f"{returning_customers}")

st.markdown("---")

# ----------------------------
# Main layout: charts + tables
# ----------------------------
left_col, right_col = st.columns([3,2])

with left_col:
    st.subheader("Top Selling Products")
    if top_products.empty:
        st.info("No product sales found for selected range.")
    else:
        # Horizontal bar chart (premium look)
        fig = px.bar(top_products, x="units_sold", y="title", orientation='h',
                     text="units_sold", color="revenue_from_orders",
                     labels={"title":"Product","units_sold":"Units Sold","revenue_from_orders":"Revenue"},
                     title=f"Top {top_n} Products by Units Sold")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Products Table**")
    st.dataframe(merged[["title","category","price","units_sold","revenue_from_orders"]].rename(columns={"title":"Product","revenue_from_orders":"Revenue"}).fillna(0))

    # Download CSV
    csv_buffer = io.StringIO()
    merged.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode()
    st.download_button("⬇️ Download Products CSV", data=csv_bytes, file_name="products_report.csv", mime="text/csv")

with right_col:
    st.subheader("Orders Trend")
    if orders_df.empty:
        st.info("No orders in selected date range.")
    else:
        daily = orders_df.groupby(orders_df["date"].dt.date).agg(daily_revenue=("amount","sum")).reset_index()
        fig2 = px.line(daily, x="date", y="daily_revenue", markers=True, title="Revenue over time")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Quick Actions")
    if st.button("Export PDF Report (demo)"):
        # simple PDF demo export as image of top chart
        st.info("PDF export demo: download CSV + use presentation export in next step (full PDF requires reportlab)")
        st.warning("Full PDF generation can be added (requires extra libs).")

# ----------------------------
# AI Insights section
# ----------------------------
st.markdown("---")
st.subheader("🤖 AI Insights (Gemini or fallback)")

# Build short prompt (compact)
top_list = top_products[["title","units_sold"]].to_dict(orient="records")
compact_prompt = f"Revenue={total_revenue}, Orders={total_orders}, Units={total_units}. Top={top_list}. Provide 2 quick insights and 2 actions."

def gemini_insights(prompt_text, timeout=30):
    """Returns (success_flag, text)"""
    if not GEMINI_AVAILABLE or not GEMINI_KEY:
        return False, "Gemini not configured — showing suggestions."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        stream = model.generate_content(prompt_text, stream=False, request_options={"timeout": timeout})
        # response object handling may vary; extract text safely
        text = ""
        if hasattr(stream, "text"):
            text = stream.text
        elif isinstance(stream, dict):
            text = str(stream)
        else:
            text = str(stream)
        return True, text
    except Exception as e:
        return False, f"Gemini error: {e}"

if st.button("Generate AI Insights"):
    with st.spinner("Generating insights..."):
        ok, result = gemini_insights(compact_prompt, timeout=20)
        if ok:
            st.success("AI Insights:")
            st.write(result)
        else:
            st.warning("Using fallback suggestions (Gemini unavailable/slow).")
            suggestions = [
                "- Offer a bundle discount for Wireless Earbuds + Bluetooth Speaker.",
                "- Run retargeting for customers who viewed top product.",
                "- Create limited-time free-shipping for orders above $100.",
                "- Improve product page descriptions and add tutorial videos."
            ]
            for s in random.sample(suggestions, 3):
                st.write(s)

# ----------------------------
# Admin / Deployment tips (collapsed)
# ----------------------------
with st.expander("Deployment & Next Steps (click)"):
    st.markdown("""
    **To make this a full premium product:**
    1. Replace dummy data with real Shopify fetch (use Admin API, read scopes).
    2. Store secrets in environment variables / Streamlit Cloud secrets.
    3. Add proper auth (OAuth or single-sign-on) — remove the demo password.
    4. Add Stripe billing for subscriptions / paid tiers.
    5. For PDF reports use `reportlab` or generate HTML -> PDF via `weasyprint`.
    6. Deploy on Render or Streamlit Cloud; use HTTPS and domain.
    """)
    st.markdown("**requirements:** `streamlit pandas plotly google-generativeai requests`")

