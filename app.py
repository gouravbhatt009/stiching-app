import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.title("📈 Sales Performance Analytics (Jan 2026)")

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data():
    # Replace with your actual filename
    df = pd.read_csv('Sales Jan-26 - Copy (1).xlsx - Sales Jan-26.csv')
    
    # Convert date to datetime format (YYYYMMDD)
    df['order_created_date'] = pd.to_datetime(df['order_created_date'], format='%Y%m%d')
    
    # Calculate Profitability/Margin Estimate
    # (Selling Price - Platform Charges - Taxes)
    df['Net_Revenue'] = df['invoiceamount'] - df['platform_charges'] - df['tax_amount']
    
    return df

try:
    df = load_and_clean_data()

    # --- TOP ROW: KPI METRICS ---
    total_sales = df['invoiceamount'].sum()
    total_qty = df['quantity'].sum()
    avg_order_val = df['invoiceamount'].mean()
    total_discount = df['discount'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Gross Sales", f"₹{total_sales:,.0f}")
    col2.metric("Total Units Sold", f"{total_qty:,}")
    col3.metric("Avg Order Value", f"₹{avg_order_val:,.2f}")
    col4.metric("Total Discounts Given", f"₹{total_discount:,.0f}")

    st.divider()

    # --- ROW 2: TRENDS ---
    st.subheader("📅 Daily Sales Volume Trend")
    daily_sales = df.groupby('order_created_date')['invoiceamount'].sum().reset_index()
    fig_trend = px.line(daily_sales, x='order_created_date', y='invoiceamount', 
                        labels={'invoiceamount': 'Sales (₹)', 'order_created_date': 'Date'},
                        line_shape='spline', render_mode='svg')
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- ROW 3: PRODUCT & CATEGORY ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔝 Top 10 SKUs by Revenue")
        top_skus = df.groupby('SKU')['invoiceamount'].sum().nlargest(10).reset_index()
        fig_sku = px.bar(top_skus, x='invoiceamount', y='SKU', orientation='h', 
                         color='invoiceamount', color_continuous_scale='Viridis')
        st.plotly_chart(fig_sku, use_container_width=True)

    with col_right:
        st.subheader("👗 Category Wise Distribution")
        cat_sales = df.groupby('article_type')['quantity'].sum().reset_index()
        fig_cat = px.pie(cat_sales, values='quantity', names='article_type', hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- ROW 4: GEOGRAPHICAL & STATUS ---
    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
        st.subheader("📍 State-wise Revenue Heatmap")
        state_sales = df.groupby('location')['invoiceamount'].sum().reset_index()
        fig_state = px.bar(state_sales, x='location', y='invoiceamount', color='invoiceamount')
        st.plotly_chart(fig_state, use_container_width=True)

    with col_g2:
        st.subheader("📦 Order Status Breakdown")
        status_count = df['order_status'].value_counts().reset_index()
        fig_status = px.bar(status_count, x='order_status', y='count', color='order_status')
        st.plotly_chart(fig_status, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("🔍 View Raw Transactional Data"):
        st.dataframe(df[['order_id', 'SKU', 'article_type', 'location', 'quantity', 'invoiceamount', 'order_status']])

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure the CSV file is in the same directory as this script.")
