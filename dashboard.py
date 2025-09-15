import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ============ Load Data ============
@st.cache_data
def load_data():
    revenue_df = pd.read_csv("data/revenue.csv")
    customers_df = pd.read_csv("data/customers.csv")
    products_df = pd.read_csv("data/products.csv")
    return revenue_df, customers_df, products_df

revenue_df, customers_df, products_df = load_data()

# ============ Metrics ============
total_revenue = revenue_df["Revenue"].sum()
total_orders = revenue_df["Orders"].sum()

# Fix for FutureWarning (iloc instead of int(series))
try:
    new_customers = int(customers_df.loc[customers_df['Segment'] == 'New Customers', 'Number of Customers'].iloc[0])
except IndexError:
    new_customers = 0

try:
    returning_customers = int(customers_df.loc[customers_df['Segment'] == 'Returning Customers', 'Number of Customers'].iloc[0])
except IndexError:
    returning_customers = 0

# ============ Merge Data ============
merged = pd.merge(products_df, revenue_df, how="left", on="Product ID")

# Handle missing / inconsistent column names
if "Units Sold" in merged.columns:
    merged.rename(columns={"Units Sold": "units_sold"}, inplace=True)

if "units_sold" not in merged.columns:
    merged["units_sold"] = 0  # default column if missing

merged["units_sold"] = merged["units_sold"].fillna(0).astype(int)

# ============ Streamlit Dashboard ============
st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")

st.title("📊 AI-Powered eCommerce Dashboard (Shopify + Gemini)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Revenue", f"${total_revenue:,.2f}")
col2.metric("📦 Units Sold", merged["units_sold"].sum())
col3.metric("🆕 New Customers", new_customers)
col4.metric("👥 Returning Customers", returning_customers)

# ============ Top Selling Products ============
st.subheader("🏆 Top Selling Products")
top_products = merged.groupby("Product Name")["units_sold"].sum().sort_values(ascending=False).head(10).reset_index()

fig = px.bar(
    top_products,
    x="Product Name",
    y="units_sold",
    text="units_sold",
    title="Top 10 Products",
)
fig.update_traces(texttemplate="%{text}", textposition="outside")
fig.update_layout(xaxis_tickangle=-40, height=500)
st.plotly_chart(fig, use_container_width=True)

# ============ Gemini AI Insights ============
st.subheader("🤖 Gemini AI Insights")

prompt = f"""
Ecommerce Analytics Report:
- Revenue: {total_revenue}
- Orders: {total_orders}
- New Customers: {new_customers}
- Returning Customers: {returning_customers}
- Top Products: {top_products.to_dict(orient='records')}
Provide 3 actionable business insights.
"""

try:
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt, request_options={"timeout": 20})
    ai_insights = response.text if response else "No response from Gemini."
except Exception as e:
    ai_insights = """
Gemini slow hai, showing default insights:

1. Focus on your best selling product.
2. Improve returning customer offers.
3. Bundle discounts on top-selling products.
"""

st.info(ai_insights)
