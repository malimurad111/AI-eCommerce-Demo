import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import openai

st.set_page_config(page_title="AI eCommerce Dashboard", layout="wide")
st.title("AI-Powered eCommerce Optimization Dashboard")
st.subheader("Fetch live store data and generate AI insights")

store_type = st.selectbox("Select Store Platform", ["Shopify", "WooCommerce"])

if store_type == "Shopify":
    api_key = st.text_input("Shopify API Key")
    password = st.text_input("Shopify Password", type="password")
    store_name = st.text_input("Store Name (e.g., mystore.myshopify.com)")
elif store_type == "WooCommerce":
    consumer_key = st.text_input("Consumer Key")
    consumer_secret = st.text_input("Consumer Secret", type="password")
    store_url = st.text_input("Store URL (e.g., https://example.com)")

openai_api_key = st.text_input("OpenAI API Key (for AI insights)", type="password")

if st.button("Fetch Store Data"):
    try:
        if store_type == "Shopify":
            url = f"https://{api_key}:{password}@{store_name}/admin/api/2025-01/orders.json?status=any&limit=50"
            response = requests.get(url)
            orders = response.json().get('orders', [])
            orders_df = pd.json_normalize(orders)
        elif store_type == "WooCommerce":
            url = f"{store_url}/wp-json/wc/v3/orders?per_page=50"
            response = requests.get(url, auth=(consumer_key, consumer_secret))
            orders = response.json()
            orders_df = pd.json_normalize(orders)

        st.success("Store data fetched successfully!")

        if 'total_price' in orders_df.columns:
            orders_df['total_price'] = orders_df['total_price'].astype(float)
            revenue_col = 'total_price'
        elif 'total' in orders_df.columns:
            orders_df['total'] = orders_df['total'].astype(float)
            revenue_col = 'total'
        else:
            st.warning("No revenue column found in orders data")
            revenue_col = None

        st.subheader("Orders Data Preview")
        st.dataframe(orders_df.head())

        total_revenue = orders_df[revenue_col].sum() if revenue_col else 0
        total_orders = len(orders_df)
        st.markdown("### Key Metrics")
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue ($)", f"{total_revenue}")
        col2.metric("Total Orders", f"{total_orders}")

        if 'line_items' in orders_df.columns:
            product_list = []
            for items in orders_df['line_items']:
                if isinstance(items, list):
                    for p in items:
                        product_list.append({
                            "Product Name": p.get('name', 'N/A'),
                            "Quantity": p.get('quantity', 0),
                            "Revenue": float(p.get('price',0)) * int(p.get('quantity',0))
                        })
            products_df = pd.DataFrame(product_list)
            top_products = products_df.groupby("Product Name").sum().sort_values(by="Revenue", ascending=False).reset_index()

            st.subheader("Top Products by Revenue")
            fig, ax = plt.subplots(figsize=(8,5))
            ax.bar(top_products["Product Name"], top_products["Revenue"], color='skyblue')
            ax.set_xlabel("Products")
            ax.set_ylabel("Revenue ($)")
            ax.set_title("Top Products by Revenue")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

            st.subheader("Top Products Table")
            st.dataframe(top_products.head(10))

        if 'customer.email' in orders_df.columns:
            new_customers = orders_df[orders_df['customer.orders_count']==1].shape[0] if 'customer.orders_count' in orders_df.columns else 0
            returning_customers = total_orders - new_customers
            st.subheader("Customer Segmentation")
            st.metric("New Customers", f"{new_customers}")
            st.metric("Returning Customers", f"{returning_customers}")

        if openai_api_key:
            openai.api_key = openai_api_key
            prompt = (
                "You are an eCommerce AI assistant. "
                "Analyze this store data and give 5 actionable insights to increase revenue, product sales, and repeat customers. "
                f"Total Revenue: ${total_revenue} "
                f"Total Orders: {total_orders} "
                f"Top Products: {top_products['Product Name'].tolist() if 'top_products' in locals() else []}"
            )
            response_ai = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300
            )
            insights = response_ai['choices'][0]['text']
            st.subheader("AI-Generated Insights")
            st.write(insights)
        else:
            st.info("Enter OpenAI API Key to generate AI insights.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")
