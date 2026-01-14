import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💰 Personal Finance Insights")

# Load Data
df = pd.read_csv("transactions.csv")

# Create a Metric (Total Spent)
total_spent = df[df['Amount'] < 0]['Amount'].sum()
st.metric("Total Expenses", f"${abs(total_spent):,.2f}")

# Create a Chart
fig = px.pie(df[df['Amount'] < 0], values='Amount', names='Category', title="Spending by Category")
st.plotly_chart(fig)