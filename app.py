import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Finance Insights", layout="wide")
st.title("💰 Personal Finance Insights Dashboard")

# 2. Load the Data
# Ensure transactions.csv is in the same folder!
df = pd.read_csv("transactions.csv")
df['Date'] = pd.to_datetime(df['Date']) # Makes sure dates are readable

# 3. Sidebar Filters
st.sidebar.header("Filter Data")
category = st.sidebar.multiselect("Select Category:", options=df["Category"].unique(), default=df["Category"].unique())
df_selection = df[df["Category"].isin(category)]

# 4. Top Metrics
total_income = df_selection[df_selection['Amount'] > 0]['Amount'].sum()
total_spent = df_selection[df_selection['Amount'] < 0]['Amount'].sum()
net_balance = total_income + total_spent


# --- Add this right after your 'Net Balance' metric ---

st.sidebar.markdown("---")
st.sidebar.header("🎯 Budget Settings")
monthly_budget = st.sidebar.number_input("Set Monthly Budget ($):", min_value=0.0, value=2000.0)

# Calculate if we are over budget
is_over_budget = abs(total_spent) > monthly_budget
percent_used = (abs(total_spent) / monthly_budget) * 100

# Display Budget Alert
if is_over_budget:
    st.error(f"🚨 ALERT: You are over budget by ${abs(total_spent) - monthly_budget:,.2f}!")
else:
    st.success(f"✅ Great job! You have ${monthly_budget - abs(total_spent):,.2f} remaining in your budget.")

st.progress(min(percent_used / 100, 1.0)) # Visual progress bar
st.write(f"Budget used: **{percent_used:.1f}%**")


col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${abs(total_spent):,.2f}", delta_color="inverse")
col3.metric("Net Balance", f"${net_balance:,.2f}")

st.markdown("---")

# 5. Charts
left_chart, right_chart = st.columns(2)

# Pie Chart for Spending
with left_chart:
    st.subheader("Spending by Category")
    expenses_df = df_selection[df_selection['Amount'] < 0]
    fig_pie = px.pie(expenses_df, values=abs(expenses_df['Amount']), names='Category', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# Line Chart for Trends
with right_chart:
    st.subheader("Cash Flow Over Time")
    fig_line = px.line(df_selection.sort_values("Date"), x="Date", y="Amount", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)