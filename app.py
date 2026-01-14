import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retail Insights", layout="wide")
st.title("📊 Retail Analytics Dashboard")

# 1. Load your new CSV
# Make sure the file in your folder is named 'retail_data.csv'
df = pd.read_csv("transactions.csv", encoding='ISO-8859-1')

# 2. Data Cleaning (The 'Data Science' part)
df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
df = df[df['TotalAmount'] > 0] # Remove returns/errors

# 3. Sidebar Filter by Country
countries = st.sidebar.multiselect("Select Countries:", options=df["Country"].unique(), default=["United Kingdom", "France"])
df_selection = df[df["Country"].isin(countries)]

# 4. Top Metrics
total_sales = df_selection['TotalAmount'].sum()
avg_order = df_selection['TotalAmount'].mean()
st.metric("Total Revenue", f"${total_sales:,.2f}")

# 5. Visualizing 'Top Products'
st.subheader("Top 10 Selling Products")
top_products = df_selection.groupby('Description')['TotalAmount'].sum().nlargest(10).reset_index()
fig_bar = px.bar(top_products, x='TotalAmount', y='Description', orientation='h', color='TotalAmount')
st.plotly_chart(fig_bar, use_container_width=True)