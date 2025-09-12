import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="AI eCommerce Dashboard (API Demo)", layout="wide")
st.title("AI-Powered eCommerce Optimization Demo")
st.subheader("Client Store Analytics & Recommendations")

# --- Fetch Dummy Data from Free API ---
st.subheader("Fetching Store Data (Free API / Demo)")

@st.cache_data
def get_demo_data():
    # Free JSON placeholder simulating store orders
    response = requests.get("https://fakestoreapi.com/products")  # Free API
    data = response.json()
    
    # Create Products DataFrame
    products_list = []
    for item in data[:5]:  # Take 5 products
        products_list.append({
            "Product Name": item['title'][:20],  # shorten title
            "Category": item['category'],
            "Units Sold": int(item['rating']['count'] / 10),
            "Revenue (USD)": int(item['price'] * item['rating']['count'] / 10),
            "AI Insight": "This is a demo AI insight for this product"
        })
    products_df = pd.DataFrame(products_list)
    
    # Create Customers DataFrame (dummy)
    customers_df = pd.DataFrame({
        "Segment": ["New Customers", "Returning Customers"],
        "Number of Customers": [250, 120],
        "AI Recommendation": [
            "Offer welcome discounts to increase first purchase",
            "Target with loyalty programs and repeat offers"
        ]
    })
    return products_df, customers_df

products_df, customers_df = get_demo_data()

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
st.info("This dashboard uses free API data to demo AI eCommerce insights. For real client stores, you can integrate Shopify/WooCommerce API for live analytics.")
