import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

# ======================
# 🔑 Gemini API Setup
# ======================
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# ======================
# 📊 Mock Shopify Data (replace with real API calls)
# ======================
products = ["Shirt", "Shoes", "Bag", "Watch", "Cap"]
sales = [230, 180, 150, 90, 60]

customers = 120
orders = 85
revenue = 4500.75

# ======================
# 📊 Streamlit Layout
# ======================
st.set_page_config(page_title="AI-Powered eCommerce Dashboard", layout="wide")
st.title("📊 AI-Powered eCommerce Dashboard (Shopify + Gemini)")

# ======================
# 🔹 KPIs
# ======================
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛍️ Products", len(products))
col2.metric("👥 Customers", customers)
col3.metric("📦 Orders", orders)
col4.metric("💰 Revenue", f"${revenue:,.2f}")

# ======================
# 🔹 Top Selling Products Chart
# ======================
def plot_top_selling_products(products, sales):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(products, sales, color="skyblue")
    ax.set_xlabel("Units Sold")
    ax.set_ylabel("Products")
    ax.set_title("Top Selling Products")
    ax.invert_yaxis()  # Highest selling product upar aayega
    plt.tight_layout()
    return fig

st.subheader("📈 Top Selling Products")
fig = plot_top_selling_products(products, sales)
st.pyplot(fig)

# ======================
# 🔹 Gemini AI Insights
# ======================
st.subheader("🤖 AI Insights")

prompt = f"""
You are an AI eCommerce analyst. 
Here is the store data:
- Products: {products}
- Sales: {sales}
- Customers: {customers}
- Orders: {orders}
- Revenue: ${revenue}

Give a short, clear insight about store performance and improvement tips.
"""

if st.button("Generate AI Insights"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    st.success(response.text)
