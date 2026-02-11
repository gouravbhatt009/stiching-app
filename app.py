import streamlit as st
import pandas as pd
import plotly.express as px

# --- SETTINGS ---
st.set_page_config(page_title="Executive Sales Dashboard", layout="wide")
st.title("📈 Multi-Channel Sales & Settlement Analytics")

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_and_merge_data():
    # 1. Load Sales Data
    sales_df = pd.read_csv('Sales Jan-26 - Copy (1).xlsx - Sales Jan-26.csv')
    sales_df['order_created_date'] = pd.to_datetime(sales_df['order_created_date'], format='%Y%m%d')
    
    # 2. Load Forward Settlements
    fwd_df = pd.read_csv('PG Forward Jan-26.csv')
    
    # 3. Load Reverse (Returns) Settlements
    rev_df = pd.read_csv('PG Reverse Jan-26.csv')
    
    # Cleaning: Handle common IDs
    sales_df['packet_id'] = sales_df['packet_id'].astype(str)
    fwd_df['packet_id'] = fwd_df['packet_id'].astype(str)
    rev_df['packet_id'] = rev_df['packet_id'].astype(str)
    
    return sales_df, fwd_df, rev_df

try:
    sales, forward, reverse = load_and_merge_data()

    # --- TOP ROW: KPI METRICS ---
    total_gross = sales['invoiceamount'].sum()
    total_units = sales['quantity'].sum()
    return_units = len(reverse)
    net_units = total_units - return_units
    
    # Settlement Analysis
    total_settled_fwd = forward['total_actual_settlement'].sum()
    total_settled_rev = reverse['total_actual_settlement'].sum()
    net_settlement = total_settled_fwd + total_settled_rev # Rev is usually negative in financial terms

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Sales Value", f"₹{total_gross:,.0f}")
    m2.metric("Net Settlement", f"₹{net_settlement:,.0f}")
    m3.metric("Net Units (After Returns)", f"{net_units:,}")
    m4.metric("Return Rate", f"{(return_units/total_units)*100:.1f}%")

    st.divider()

    # --- MIDDLE ROW: TRENDS & PRODUCTS ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📅 Daily Sales Volume (Jan 2026)")
        daily_trend = sales.groupby('order_created_date')['invoiceamount'].sum().reset_index()
        fig_line = px.line(daily_trend, x='order_created_date', y='invoiceamount', template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.subheader("🔝 Top 10 SKUs by Sales")
        top_skus = sales.groupby('SKU')['invoiceamount'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(top_skus, x='invoiceamount', y='SKU', orientation='h', color='invoiceamount')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- BOTTOM ROW: GEOGRAPHY & SETTLEMENT ---
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("📍 Geographical Sales Heatmap")
        geo_data = sales.groupby('location')['invoiceamount'].sum().reset_index()
        fig_geo = px.bar(geo_data.sort_values('invoiceamount', ascending=False).head(15), 
                         x='location', y='invoiceamount', color='location')
        st.plotly_chart(fig_geo, use_container_width=True)

    with c4:
        st.subheader("💸 Settlement: Forward vs Reverse")
        settle_data = pd.DataFrame({
            "Type": ["Forward (Sales)", "Reverse (Returns)"],
            "Amount": [total_settled_fwd, abs(total_settled_rev)]
        })
        fig_pie = px.pie(settle_data, values='Amount', names='Type', hole=0.5, 
                         color_discrete_sequence=['#2ECC71', '#E74C3C'])
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("🔍 Deep Dive: Transactional Audit"):
        st.write("This table shows the relationship between Order Amount and Final Settlement.")
        # Merging for an audit view
        audit_df = sales.merge(forward[['packet_id', 'total_actual_settlement']], on='packet_id', how='left')
        st.dataframe(audit_df[['order_id', 'SKU', 'invoiceamount', 'total_actual_settlement', 'order_status']].head(100))

except Exception as e:
    st.error(f"Critical Error: {e}")
    st.info("Check if all three CSV files are in the same folder as the script.")
