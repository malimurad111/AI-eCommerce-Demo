import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
import os

# ----------------------------
# Gemini API Configuration
# ----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ----------------------------
# Dashboard Title
# ----------------------------
st.set_page_config(page_title="AI-Powered eCommerce Dashboard", layout="wide")
st.title("📊 AI-Powered eCommerce Dashboard (Shopify + Gemini)")

# ----------------------------
# Sample Data (replace with Shopify API later)
# ----------------------------
products = ["Shoes", "T-Shirts", "Jeans", "Hoodies", "Jackets"]
sales = [120, 90, 75, 60, 40]
customers = 230
orders = 180
revenue = 15250.75

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛍️ Products", len(products))
col2.metric("👥 Customers", customers)
col3.metric("📦 Orders", orders)
col4.metric("💰 Revenue", f"${revenue:,.2f}")

st.markdown("---")

# ----------------------------
# Top Selling Products (Bar Chart)
# ----------------------------
st.subheader("📈 Top Selling Products")
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(products, sales, color="skyblue", edgecolor="black")

# Labels above bars
for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        str(bar.get_height()),
        ha="center",
        fontsize=10,
        fontweight="bold"
    )

ax.set_xlabel("Products")
ax.set_ylabel("Sales")
ax.set_title("Top Selling Products")
plt.tight_layout()
st.pyplot(fig)

st.markdown("---")

# ----------------------------
# AI Insights Section
# ----------------------------
st.subheader("🤖 Gemini AI Insights")

prompt = f"""
Analyze the eCommerce store performance.

Products: {", ".join(products)}
Sales: {", ".join(map(str, sales))}
Customers: {customers}
Orders: {orders}
Revenue: ${revenue}

Give 3 short insights and 2 actionable suggestions to improve sales.
"""

if st.button("Generate AI Insights"):
    with st.spinner("Generating insights with Gemini..."):
        try:
            response = model.generate_content(prompt)
            if response and hasattr(response, "text"):
                st.success("✅ Insights Generated Successfully")
                st.write(response.text)
            else:
                st.warning("⚠️ No response received from Gemini API.")
        except Exception as e:
            st.error(f"Gemini API Error: {str(e)}")
