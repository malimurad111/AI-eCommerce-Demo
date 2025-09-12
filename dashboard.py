import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Dummy Product Data ---
products = {
    "Product Name": ["Smart Watch", "Wireless Earbuds", "Bluetooth Speaker", "Fitness Tracker", "Gaming Mouse"],
    "Category": ["Wearables", "Audio", "Audio", "Wearables", "Gaming"],
    "Units Sold": [120, 200, 150, 90, 75],
    "Revenue (USD)": [6000, 10000, 4500, 2700, 3750],
    "AI Insight": [
        "High demand, consider upselling accessories",
        "Popular item, run targeted email campaigns",
        "Good seasonal trend, offer bundle deals",
        "Focus on repeat buyers with discount codes",
        "Add product tutorial videos to increase conversion"
    ]
}

products_df = pd.DataFrame(products)

# --- Dummy Customer Data ---
customers = {
    "Segment": ["New Customers", "Returning Customers"],
    "Number of Customers": [250, 120],
    "AI Recommendation": [
        "Offer welcome discounts to increase first purchase",
        "Target with loyalty programs and repeat offers"
    ]
}

customers_df = pd.DataFrame(customers)

# --- Streamlit Layout ---
st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")
st.title("AI-Powered eCommerce Optimization Demo")
st.subheader("Client Store Analytics & Recommendations")

# --- KPI Metrics ---
total_revenue = products_df["Revenue (USD)"].sum()
total_units = products_df["Units Sold"].sum()
new_customers = customers_df.loc[customers_df['Segment']=='New Customers', 'Number of Customers'].values[0]
returning_customers = customers_df.loc[customers_df['Segment']=='Returning Customers', 'Number of Customers'].values[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue ($)", f"{total_revenue}")
col2.metric("Total Units Sold", f"{total_units}")
col3.metric("New Customers", f"{new_customers}")
col4.metric("Returning Customers", f"{returning_customers}")

st.markdown("---")

# --- Product Sales Bar Chart ---
st.subheader("Top Selling Products")
fig, ax = plt.subplots()
ax.bar(products_df["Product Name"], products_df["Units Sold"], color='skyblue')
ax.set_xlabel("Products")
ax.set_ylabel("Units Sold")
ax.set_title("Units Sold per Product")
st.pyplot(fig)

# --- Product Revenue Pie Chart ---
st.subheader("Revenue Distribution")
fig2, ax2 = plt.subplots()
ax2.pie(products_df["Revenue (USD)"], labels=products_df["Product Name"], autopct='%1.1f%%', startangle=90)
ax2.set_title("Revenue Share by Product")
st.pyplot(fig2)

st.markdown("---")

# --- Product Insights Table ---
st.subheader("AI Product Insights")
st.dataframe(products_df[["Product Name","AI Insight"]])

# --- Customer Insights Table ---
st.subheader("AI Customer Insights")
st.dataframe(customers_df[["Segment","AI Recommendation"]])

st.markdown("---")
st.info("This dashboard is a professional demo for eCommerce AI optimization services. Insights are generated using AI suggestions for better business decisions.")
