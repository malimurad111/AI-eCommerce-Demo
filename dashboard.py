# dashboard_premium_shopify.py
import os
import io
import json
import time
import random
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Optional Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Premium AI eCommerce Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("Premium AI eCommerce Dashboard")

# ----------------------------
# Environment / Secrets (set these locally)
# ----------------------------
# Set these in your terminal / system or Streamlit Cloud secrets:
# SHOPIFY_STORE (e.g. mystore.myshopify.com)
# SHOPIFY_ACCESS_TOKEN (Admin API access token - read-only scopes)
# GEMINI_API_KEY (optional)
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_AVAILABLE and GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# ----------------------------
# Sidebar: Settings / Filters
# ----------------------------
st.sidebar.header("Settings & Data")
use_shopify = st.sidebar.checkbox("Use Shopify (swap dummy data)", value=False)
use_gemini = st.sidebar.checkbox("Enable Gemini AI Insights", value=False)
if use_gemini and not GEMINI_AVAILABLE:
    st.sidebar.warning("google-generativeai not installed — Gemini disabled")
    use_gemini = False

# Quick demo auth
st.sidebar.markdown("### Access (demo)")
password = st.sidebar.text_input("Enter app password", type="password")
if password != "" and password != os.getenv("DASHBOARD_PASS", "demo123"):
    st.sidebar.error("Incorrect password (demo). Use demo123 or set DASHBOARD_PASS env var.")
    st.stop()

# Date filter / controls
today = datetime.utcnow().date()
start_date = st.sidebar.date_input("Start date", value=today - timedelta(days=30))
end_date = st.sidebar.date_input("End date", value=today)
if start_date > end_date:
    st.sidebar.error("Start date must be before end date")
    st.stop()

top_n = st.sidebar.slider("Top N products", min_value=3, max_value=20, value=5)
category_filter = st.sidebar.multiselect("Category (filter)", options=[], default=[])

# ----------------------------
# Dummy data loader (fallback)
# ----------------------------
def load_dummy_data():
    products = [
        {"id":101,"title":"Smart Watch","category":"Wearables","price":50,"units_sold":120,"revenue":6000,"date":"2025-08-01"},
        {"id":102,"title":"Wireless Earbuds","category":"Audio","price":50,"units_sold":200,"revenue":10000,"date":"2025-08-05"},
        {"id":103,"title":"Bluetooth Speaker","category":"Audio","price":30,"units_sold":150,"revenue":4500,"date":"2025-08-10"},
        {"id":104,"title":"Fitness Tracker","category":"Wearables","price":30,"units_sold":90,"revenue":2700,"date":"2025-08-20"},
        {"id":105,"title":"Gaming Mouse","category":"Gaming","price":50,"units_sold":75,"revenue":3750,"date":"2025-08-25"},
    ]
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
    orders_df["date"] = pd.to_datetime(orders_df["date"])
    return products_df, orders_df, customers_df

# ----------------------------
# Shopify fetch helpers
# ----------------------------
API_VERSION = "2025-07"

def shopify_request(path, params=None):
    """Simple GET helper returning JSON or raising."""
    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        raise RuntimeError("SHOPIFY_STORE or SHOPIFY_ACCESS_TOKEN not set")
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/{path}"
    headers = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_all_orders(limit=250, status="any"):
    """Paginate through orders (cursor-based) and return list of orders."""
    orders = []
    params = {"limit": limit, "status": status, "created_at_min": start_date.isoformat()+"T00:00:00Z", "created_at_max": end_date.isoformat()+"T23:59:59Z"}
    path = "orders.json"
    try:
        data = shopify_request(path, params=params)
        orders.extend(data.get("orders", []))
        # Note: for very large stores, implement cursor pagination using 'link' header
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
    return orders

def fetch_products(limit=250):
    products = []
    params = {"limit": limit}
    try:
        data = shopify_request("products.json", params=params)
        products.extend(data.get("products", []))
    except Exception as e:
        st.error(f"Error fetching products: {e}")
    return products

def fetch_customers(limit=250):
    customers = []
    params = {"limit": limit}
    try:
        data = shopify_request("customers.json", params=params)
        customers.extend(data.get("customers", []))
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
    return customers

# ----------------------------
# Data load: Shopify or dummy
# ----------------------------
if use_shopify:
    if SHOPIFY_STORE and SHOPIFY_TOKEN:
        st.sidebar.success("Shopify credentials found — fetching live data")
        # Fetch and convert to DataFrames
        raw_products = fetch_products()
        raw_orders = fetch_all_orders()
        raw_customers = fetch_customers()

        # Normalize to dataframes (safe handling)
        try:
            products_df = pd.json_normalize(raw_products) if raw_products else pd.DataFrame()
            # create simplified columns if present
            if not products_df.empty:
                products_df = products_df.rename(columns={"title":"title","variants":"variants"})
                # keep price from first variant (safe fallback)
                products_df["price"] = products_df.get("variants", pd.Series([[]]*len(products_df))).apply(lambda v: float(v[0].get("price")) if isinstance(v,list) and v and v[0].get("price") else 0)
                products_df["category"] = products_df.get("product_type", "")
            orders_df = pd.json_normalize(raw_orders) if raw_orders else pd.DataFrame()
            # Some order fields may be nested; ensure line_items exists
            if not orders_df.empty and "line_items" in orders_df.columns:
                # convert created_at to datetime
                orders_df["date"] = pd.to_datetime(orders_df["created_at"])
            customers_df = pd.json_normalize(raw_customers) if raw_customers else pd.DataFrame()
        except Exception as e:
            st.error(f"Error normalizing Shopify data: {e}")
            products_df, orders_df, customers_df = load_dummy_data()
    else:
        st.sidebar.error("SHOPIFY_STORE or SHOPIFY_ACCESS_TOKEN missing — using dummy data")
        products_df, orders_df, customers_df = load_dummy_data()
else:
    products_df, orders_df, customers_df = load_dummy_data()

# ----------------------------
# Recompute aggregates & apply filters
# ----------------------------
if not orders_df.empty:
    orders_df = orders_df[(orders_df["date"].dt.date >= start_date) & (orders_df["date"].dt.date <= end_date)]

# Build product aggregates from orders (safe)
if not orders_df.empty and "line_items" in orders_df.columns:
    product_rows = []
    for items in orders_df["line_items"]:
        if isinstance(items, list):
            for li in items:
                product_rows.append({"title": li.get("name"), "quantity": int(li.get("quantity", 0)), "amount": float(li.get("price",0))*int(li.get("quantity",0))})
    product_agg = pd.DataFrame(product_rows).groupby("title").agg(units_sold=("quantity","sum"), revenue=("amount","sum")).reset_index()
else:
    # If orders_df doesn't have line_items (dummy path), use products_df fields or aggregated orders
    if "units_sold" in products_df.columns and "revenue" in products_df.columns:
        product_agg = products_df.rename(columns={"title":"title", "units_sold":"units_sold", "revenue":"revenue"})[["title","units_sold","revenue"]]
    else:
        product_agg = pd.DataFrame(columns=["title","units_sold","revenue"])

# Merge product info
if "title" in products_df.columns and not product_agg.empty:
    merged = pd.merge(products_df, product_agg, left_on="title", right_on="title", how="left")
    merged["units_sold"] = merged["units_sold"].fillna(0).astype(int)
    merged["revenue"] = merged["revenue"].fillna(0)
else:
    merged = product_agg.rename(columns={"title":"title", "revenue":"revenue"})

# Filter by category if selected (only when products_df has category)
if category_filter and "category" in merged.columns:
    merged = merged[merged["category"].isin(category_filter)]

merged = merged.sort_values(by="units_sold", ascending=False)
top_products = merged.head(top_n)

# KPIs
total_revenue = orders_df["amount"].sum() if not orders_df.empty else merged["revenue"].sum()
total_orders = orders_df["order_id"].nunique() if not orders_df.empty else 0
total_units = merged["units_sold"].sum() if not merged.empty else 0
new_customers = customers_df.shape[0] if not customers_df.empty else 0
returning_customers = customers_df[customers_df.get("orders",0) > 1].shape[0] if not customers_df.empty else 0

# Top KPI cards
k1, k2, k3, k4, k5 = st.columns([2,2,2,2,2])
k1.metric("💰 Revenue", f"${total_revenue:,.2f}")
k2.metric("📦 Orders", f"{total_orders}")
k3.metric("📊 Units Sold", f"{total_units}")
k4.metric("🆕 New Customers", f"{new_customers}")
k5.metric("🔁 Returning", f"{returning_customers}")

st.markdown("---")

# ----------------------------
# Charts & Tables
# ----------------------------
left_col, right_col = st.columns([3,2])
with left_col:
    st.subheader("Top Selling Products")
    if top_products.empty:
        st.info("No product sales found for selected range.")
    else:
        fig = px.bar(top_products, x="units_sold", y="title", orientation='h',
                     text="units_sold", color="revenue",
                     labels={"title":"Product","units_sold":"Units Sold","revenue":"Revenue"},
                     title=f"Top {top_n} Products by Units Sold")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Products Table**")
    display_cols = [c for c in ["title","category","price","units_sold","revenue"] if c in merged.columns]
    st.dataframe(merged[display_cols].rename(columns={"title":"Product","revenue":"Revenue"}).fillna(0))

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
        st.info("PDF export demo: download CSV + use presentation export in next step (full PDF requires reportlab).")

# ----------------------------
# AI Insights (Gemini or fallback)
# ----------------------------
st.markdown("---")
st.subheader("🤖 AI Insights (Gemini or fallback)")
top_list = top_products[["title","units_sold"]].to_dict(orient="records")
compact_prompt = f"Revenue={total_revenue}, Orders={total_orders}, Units={total_units}. Top={top_list}. Provide 2 quick insights and 2 actions."

def gemini_insights(prompt_text, timeout=20):
    """Return (ok, text)"""
    if not GEMINI_AVAILABLE or not GEMINI_KEY:
        return False, "Gemini not configured — showing suggestions."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt_text, stream=False, request_options={"timeout": timeout})
        text = ""
        if hasattr(resp, "text"):
            text = resp.text
        elif isinstance(resp, dict):
            text = json.dumps(resp)
        else:
            text = str(resp)
        return True, text
    except Exception as e:
        return False, f"Gemini error: {e}"

if st.button("Generate AI Insights"):
    with st.spinner("Generating insights..."):
        ok, result = gemini_insights(compact_prompt, timeout=25)
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
# Deployment notes
# ----------------------------
with st.expander("Deployment & Next Steps (click)"):
    st.markdown("""
    **Make production-ready:**
    1. Put SHOPIFY_STORE & SHOPIFY_ACCESS_TOKEN in environment or Streamlit Cloud secrets.
    2. Ensure your Shopify app has read scopes: read_products, read_orders, read_customers, read_analytics.
    3. Replace demo auth with OAuth or other secure auth.
    4. Add rate-limit handling / cursor pagination for very large stores (Link header).
    5. For PDF exports use reportlab or weasyprint; for images use plotly.to_image().
    """)
    st.markdown("**requirements:** streamlit pandas plotly requests google-generativeai")

