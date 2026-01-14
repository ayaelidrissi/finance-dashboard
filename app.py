import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# Custom CSS to fix the previous TypeError and match your portfolio
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Retail Data Science Dashboard")
st.markdown("Analyzing global transaction patterns and revenue trends using Python.")

# 2. Bulletproof Data Loading Function
@st.cache_data
def load_data():
    # Load the file with specific encoding for retail data
    df = pd.read_csv("transactions.csv", encoding='ISO-8859-1')
    
    # FIX: Remove hidden spaces from column names to prevent KeyErrors
    df.columns = df.columns.str.strip()
    
    # Mapping your specific Excel columns to the dashboard logic
    # Expected: 'NumberOrdered', 'CostPerItem', 'ItemDescription', 'Country'
    
    # Create the TotalAmount column (Quantity * Price)
    if 'NumberOrdered' in df.columns and 'CostPerItem' in df.columns:
        df['TotalAmount'] = df['NumberOrdered'] * df['CostPerItem']
    else:
        # Fallback if names are slightly different in your online CSV
        st.error(f"Column mismatch! Available columns: {list(df.columns)}")
        st.stop()
        
    # Filter out invalid data
    df = df[df['TotalAmount'] > 0]
    return df

try:
    df = load_data()

    # 3. Sidebar Filters
    st.sidebar.header("🎯 Dashboard Filters")
    
    # Country Multi-select
    countries = st.sidebar.multiselect(
        "Select Countries:",
        options=sorted(df["Country"].unique()),
        default=df["Country"].unique()[:5] 
    )

    # Revenue Goal Slider
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Business Goals")
    target_goal = st.sidebar.number_input("Set Revenue Target ($):", min_value=0.0, value=10000.0)

    # Apply filters to the dataframe
    df_selection = df[df["Country"].isin(countries)]

    # 4. Top Metrics (KPIs)
    total_revenue = df_selection['TotalAmount'].sum()
    total_items = df_selection['NumberOrdered'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Items Sold", f"{int(total_items):,}")
    with col3:
        # Goal Progress Logic
        delta = total_revenue - target_goal
        st.metric("Goal Progress", f"${total_revenue:,.2f}", delta=f"${delta:,.2f}")

    # Progress Bar
    progress_val = min(total_revenue / target_goal, 1.0) if target_goal > 0 else 1.0
    st.progress(progress_val)

    st.markdown("---")

    # 5. Visualizations
    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Top Products by Revenue")
        # Aggregating data by ItemDescription
        top_items = df_selection.groupby('ItemDescription')['TotalAmount'].sum().nlargest(10).reset_index()
        fig_product = px.bar(
            top_items,
            x="TotalAmount",
            y="ItemDescription",
            orientation="h",
            color="TotalAmount",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        st.plotly_chart(fig_product, use_container_width=True)

    with right_column:
        st.subheader("Market Share by Country")
        fig_country = px.pie(
            df_selection, 
            values='TotalAmount', 
            names='Country',
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_country, use_container_width=True)

    # 6. Raw Data Expander
    with st.expander("👀 View Filtered Transaction Data"):
        st.dataframe(df_selection)

except Exception as e:
    st.error(f"Critical Error: {e}")