import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# Custom CSS for a professional "Dark Mode" Portfolio look
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
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Retail Data Science Dashboard")
st.markdown("Analyzing global transaction patterns and revenue trends.")

# 2. Bulletproof Data Loading
@st.cache_data
def load_data():
    # Load the file with specific encoding
    df = pd.read_csv("transactions.csv", encoding='ISO-8859-1')
    
    # Remove hidden spaces from column names
    df.columns = df.columns.str.strip()
    
    # Mathematical calculation for Total Amount
    # Using your specific column: NumberOfItemsPurchased
    df['TotalAmount'] = df['NumberOfItemsPurchased'] * df['CostPerItem']
    
    # Filter out invalid or return data
    df = df[df['TotalAmount'] > 0]
    return df

try:
    df = load_data()

    # 3. Sidebar - Filters & Search
    st.sidebar.header("🎯 Dashboard Controls")
    
    # Search Feature
    search_query = st.sidebar.text_input("🔍 Search Product:", "").upper()
    
    # Country Filter
    countries = st.sidebar.multiselect(
        "Select Countries:",
        options=sorted(df["Country"].unique()),
        default=df["Country"].unique()[:5] 
    )

    # Revenue Goal Input
    st.sidebar.markdown("---")
    target_goal = st.sidebar.number_input("Set Revenue Target ($):", min_value=0.0, value=10000.0)

    # --- Applying Filters ---
    df_selection = df[df["Country"].isin(countries)]
    
    if search_query:
        df_selection = df_selection[df_selection['ItemDescription'].str.contains(search_query, na=False)]

    # 4. Top Metrics (KPIs)
    total_revenue = df_selection['TotalAmount'].sum()
    total_units = df_selection['NumberOfItemsPurchased'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Units Sold", f"{int(total_units):,}")
    with col3:
        # Goal Progress logic
        delta = total_revenue - target_goal
        st.metric("Goal Status", f"${total_revenue:,.2f}", delta=f"${delta:,.2f}")

    # Progress Bar to Target
    progress_pct = min(total_revenue / target_goal, 1.0) if target_goal > 0 else 1.0
    st.progress(progress_pct)

    st.markdown("---")

    # 5. Charts
    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Top Products by Revenue")
        top_items = df_selection.groupby('ItemDescription')['TotalAmount'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(
            top_items,
            x="TotalAmount",
            y="ItemDescription",
            orientation="h",
            color="TotalAmount",
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with right_chart:
        st.subheader("Market Share by Country")
        fig_pie = px.pie(
            df_selection, 
            values='TotalAmount', 
            names='Country',
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 6. Data Viewer
    with st.expander("👀 View Raw Transaction Data"):
        st.dataframe(df_selection)

except Exception as e:
    st.error(f"Error: {e}")