import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# Custom CSS to make it look like your Portfolio theme
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    </style>
    """, unsafe_allow_index=True)

st.title("📊 Retail Data Science Dashboard")
st.markdown("Analyzing global transaction patterns and revenue trends.")

# 2. Load the Data
@st.cache_data # This makes the app load much faster!
def load_data():
    # Using your specific filename and encoding
    df = pd.read_csv("transactions.csv", encoding='ISO-8859-1')
    
    # Create the TotalAmount column (Data Engineering)
    df['TotalAmount'] = df['NumberOrdered'] * df['CostPerItem']
    
    # Remove any rows with negative or zero sales
    df = df[df['TotalAmount'] > 0]
    return df

try:
    df = load_data()

    # 3. Sidebar Filters
    st.sidebar.header("🎯 Dashboard Filters")
    
    # Filter by Country
    countries = st.sidebar.multiselect(
        "Select Countries:",
        options=df["Country"].unique(),
        default=df["Country"].unique()[:3] # Default to first 3 countries
    )

    # Filter by Budget Goal (The feature we added earlier)
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Revenue Goal")
    target_goal = st.sidebar.number_input("Set Revenue Target ($):", min_value=0.0, value=50000.0)

    # Apply filters to the dataframe
    df_selection = df[df["Country"].isin(countries)]

    # 4. Top Metrics (KPIs)
    total_revenue = df_selection['TotalAmount'].sum()
    avg_sale = df_selection['TotalAmount'].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        # Conditional Logic: Show green if goal met, red if not
        delta = total_revenue - target_goal
        st.metric("Goal Progress", f"${total_revenue:,.2f}", delta=f"${delta:,.2f}")

    if total_revenue >= target_goal:
        st.success("🎉 Target Revenue Achieved!")
    else:
        st.warning(f"Keep going! You are ${abs(delta):,.2f} away from your goal.")

    st.markdown("---")

    # 5. Charts and Visualizations
    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Top 10 Products by Revenue")
        # Grouping data (The 'Science' part)
        top_items = df_selection.groupby('ItemDescription')['TotalAmount'].sum().nlargest(10).reset_index()
        fig_product_sales = px.bar(
            top_items,
            x="TotalAmount",
            y="ItemDescription",
            orientation="h",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        st.plotly_chart(fig_product_sales, use_container_width=True)

    with right_column:
        st.subheader("Revenue Distribution by Country")
        fig_country_pie = px.pie(
            df_selection, 
            values='TotalAmount', 
            names='Country',
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_country_pie, use_container_width=True)

    # 6. Data Table View
    with st.expander("👀 View Raw Filtered Data"):
        st.dataframe(df_selection)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Check if your CSV file is named 'transactions.csv' and is in the same folder.")