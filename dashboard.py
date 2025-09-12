import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import openai

# --- Streamlit Layout ---
st.title("AI-Powered eCommerce Dashboard (API Connected)")

# --- API Input ---
st.subheader("Enter Your Store API Credentials")
store_type = st.selectbox("Store Platform", ["Shopify", "WooCommerce"])

if store_type == "Shopify":
    api_key = st.text_input("API Key")
    password = st.text_input("Password")
    store_name = st.text_input("Store Name (e.g., mystore.myshopify.com)")
elif store_type == "WooCommerce":
    consumer_key = st.text_input("Consumer Key")
    consumer_secret = st.text_input("Consumer Secret")
    store_url = st.text_input("Store URL (e.g., https://example.com)")

# --- Fetch Data Button ---
if st.button("Fetch Store Data"):
    try:
        if store_type == "Shopify":
            url = f"https://{api_key}:{password}@{store_name}/admin/api/2025-01/orders.json?status=any"
            response = requests.get(url)
            orders = response.json()['orders']
            orders_df = pd.json_normalize(orders)
        elif store_type == "WooCommerce":
            url = f"{store_url}/wp-json/wc/v3/orders"
            response = requests.get(url, auth=(consumer_key, consumer_secret))
            orders = response.json()
            orders_df = pd.json_normalize(orders)

        st.success("Store data fetched successfully!")
        st.dataframe(orders_df.head())

        # --- Example AI Insight Generation ---
        openai.api_key = st.text_input("Enter OpenAI API Key for AI Insights", type="password")

        if openai.api_key:
            total_sales = orders_df['total_price'].astype(float).sum() if 'total_price' in orders_df.columns else orders_df['total'].astype(float).sum()
            prompt = f"Analyze the following eCommerce data and provide actionable insights:\nTotal Revenue: ${total_sales}\nNumber of Orders: {len(orders_df)}"
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=200
            )
            insights = response['choices'][0]['text']
            st.subheader("AI-Generated Insights")
            st.write(insights)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
