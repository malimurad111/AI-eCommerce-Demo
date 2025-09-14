import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import os

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Dummy Data (replace with Shopify API later) ---
products = {
    "Product Name": ["Smart Watch", "Wireless Earbuds", "Bluetooth Speaker", "Fitness Tracker", "Gaming Mouse"],
    "Units Sold": [120, 200, 150, 90, 75],
    "Revenue (USD)": [6000, 10000, 4500, 2700, 3750],
}
products_df = pd.DataFrame(products)

customers = {
    "Segment": ["New Customers", "Returning Customers"],
    "Number of Customers": [250, 120],
}
customers_df = pd.DataFrame(customers)

# --- KPIs ---
total_revenue = products_df["Revenue (USD)"].sum()
total_units = products_df["Units Sold"].sum()
new_customers = int(customers_df.loc[customers_df['Segment']=='New Customers', 'Number of Customers'])
returning_customers = int(customers_df.loc[customers_df['Segment']=='Returning Customers', 'Number of Customers'])

# --- Streamlit Layout ---
st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")
st.title("📊 AI-Powered eCommerce Dashboard (Shopify + Gemini)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Revenue", f"${total_revenue:,.2f}")
col2.metric("📦 Units Sold", f"{total_units}")
col3.metric("🆕 New Customers", f"{new_customers}")
col4.metric("👥 Returning Customers", f"{returning_customers}")

st.markdown("---")

# --- Top Selling Products Chart ---
st.subheader("Top Selling Products")
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(products_df["Product Name"], products_df["Units Sold"], color='skyblue')
ax.set_xlabel("Products")
ax.set_ylabel("Units Sold")
ax.set_title("Units Sold per Product")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig)

st.markdown("---")

# --- AI Insights with Streaming ---
st.subheader("🤖 Gemini AI Insights")

prompt = f"""
Store KPIs:
- Revenue: ${total_revenue}
- Orders: {total_orders}
- Customers: {total_customers}

Top 3 Products: {dict(list(product_sales.items())[:3])}

Give 2 insights and 1 action recommendation.
"""


if st.button("Generate AI Insights"):
    with st.spinner("⚡ Generating insights with Gemini..."):
        try:
            stream = model.generate_content(prompt, tream=True, request_options={"timeout": 20}  # 20 seconds max)
            response_text = ""
            for chunk in stream:
                if chunk.text:
                    response_text += chunk.text
                    st.markdown(response_text)  # Live update while streaming
            st.success("✅ Insights Generated")
        except Exception as e:
            st.error(f"Gemini API Error: {str(e)}")
