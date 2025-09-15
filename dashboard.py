import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

# ---------------------------
# Step 1: Ensure data folder + dummy CSVs
# ---------------------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Dummy Revenue Data
revenue_file = os.path.join(DATA_DIR, "revenue.csv")
if not os.path.exists(revenue_file):
    dates = pd.date_range(datetime.today() - timedelta(days=30), periods=30).date
    revenue = np.random.randint(500, 3000, size=30)
    pd.DataFrame({"date": dates, "revenue": revenue}).to_csv(revenue_file, index=False)

# Dummy Customers Data
customers_file = os.path.join(DATA_DIR, "customers.csv")
if not os.path.exists(customers_file):
    pd.DataFrame({
        "Segment": ["New Customers", "Returning Customers"],
        "Number of Customers": [250, 120]
    }).to_csv(customers_file, index=False)

# Dummy Products Data
products_file = os.path.join(DATA_DIR, "products.csv")
if not os.path.exists(products_file):
    pd.DataFrame({
        "Product": ["Smart Watch", "Wireless Earbuds", "Bluetooth Speaker", "Gaming Mouse"],
        "Category": ["Wearables", "Audio", "Audio", "Gaming"],
        "Price": [120, 80, 60, 40],
        "Units Sold": [150, 200, 100, 75],
        "Revenue": [18000, 16000, 6000, 3000]
    }).to_csv(products_file, index=False)

# ---------------------------
# Step 2: Load Data
# ---------------------------
@st.cache_data
def load_data():
    revenue_df = pd.read_csv(revenue_file)
    customers_df = pd.read_csv(customers_file)
    products_df = pd.read_csv(products_file)
    return revenue_df, customers_df, products_df

revenue_df, customers_df, products_df = load_data()

# ---------------------------
# Step 3: Dashboard Layout
# ---------------------------
st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")

st.title("📊 AI-Powered eCommerce Dashboard")

# KPIs
total_revenue = revenue_df["revenue"].sum()
new_customers = int(customers_df.loc[customers_df["Segment"] == "New Customers", "Number of Customers"].iloc[0])
returning_customers = int(customers_df.loc[customers_df["Segment"] == "Returning Customers", "Number of Customers"].iloc[0])
total_units = products_df["Units Sold"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
kpi2.metric("🆕 New Customers", new_customers)
kpi3.metric("🔁 Returning Customers", returning_customers)
kpi4.metric("📦 Units Sold", total_units)

st.markdown("---")

# Revenue Trend
st.subheader("📈 Revenue Over Time")
fig1 = px.line(revenue_df, x="date", y="revenue", markers=True, title="Daily Revenue")
st.plotly_chart(fig1, use_container_width=True)

# Products Performance
st.subheader("🏆 Top Products")
fig2 = px.bar(products_df, x="Product", y="Units Sold", color="Category", text="Units Sold")
st.plotly_chart(fig2, use_container_width=True)

# Customers
st.subheader("👥 Customer Breakdown")
fig3 = px.pie(customers_df, names="Segment", values="Number of Customers", title="Customer Segments")
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# Step 4: AI Insights (Fallback)
# ---------------------------
st.markdown("## 🤖 AI Insights")
st.info("Gemini slow hai, showing default insights:")
st.write("- Focus on your best selling product.")
st.write("- Offer bundle discounts on top-selling items.")
st.write("- Improve offers for returning customers.")
