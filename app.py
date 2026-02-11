import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Consolidated Business Audit", layout="wide")
st.title("🛡️ Jan 2026: Sales & Settlement Reconciliation")

@st.cache_data
def load_and_reconcile():
    # 1. Load Files with standard string IDs to prevent merge errors
    sales = pd.read_csv('Sales Jan-26 - Copy (1).xlsx - Sales Jan-26.csv', dtype={'packet_id': str})
    fwd = pd.read_csv('PG Forward Jan-26.csv', dtype={'packet_id': str})
    rev = pd.read_csv('PG Reverse Jan-26.csv', dtype={'packet_id': str})

    # 2. Date Cleaning
    sales['order_created_date'] = pd.to_datetime(sales['order_created_date'], format='%Y%m%d')
    
    # 3. Calculate Financial Metrics
    # Forward Settlement = Money coming in
    # Reverse Settlement = Money being deducted for returns
    total_fwd = fwd['total_actual_settlement'].sum()
    total_rev = rev['total_actual_settlement'].sum() # Usually negative values
    
    # Marketplace Leakage (Commission + Fees)
    # Estimated as: Invoice Amount - Actual Settlement
    fwd_merged = sales.merge(fwd[['packet_id', 'total_actual_settlement']], on='packet_id', how='inner')
    fwd_merged['leakage'] = fwd_merged['invoiceamount'] - fwd_merged['total_actual_settlement']
    
    return sales, fwd, rev, fwd_merged, total_fwd, total_rev

try:
    df_sales, df_fwd, df_rev, df_audit, fwd_sum, rev_sum = load_and_reconcile()

    # --- TOP ROW: RECONCILIATION SUMMARY ---
    total_invoice = df_sales['invoiceamount'].sum()
    net_payout = fwd_sum + rev_sum
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoice Value", f"₹{total_invoice:,.0f}")
    c2.metric("Net Bank Payout", f"₹{net_payout:,.0f}", help="Total Forward - Total Reverse deductions")
    c3.metric("Returns (Reverse)", f"₹{abs(rev_sum):,.0f}", delta_color="inverse")
    c4.metric("Avg. Marketplace Fee", f"₹{df_audit['leakage'].mean():,.2f}")

    st.divider()

    # --- MIDDLE ROW: SALES VS SETTLEMENT ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📦 Sales vs. Actual Payout by SKU")
        sku_compare = df_audit.groupby('SKU').agg({
            'invoiceamount': 'sum',
            'total_actual_settlement': 'sum'
        }).nlargest(10, 'invoiceamount').reset_index()
        
        fig_sku = px.bar(sku_compare, x='SKU', y=['invoiceamount', 'total_actual_settlement'],
                         barmode='group', title="Top 10 SKUs: What you billed vs What you got")
        st.plotly_chart(fig_sku, use_container_width=True)

    with col_right:
        st.subheader("🚩 Return Analysis (Reverse Report)")
        # Article types causing the most returns
        rev_merged = df_rev.merge(df_sales[['packet_id', 'article_type']], on='packet_id', how='left')
        rev_stats = rev_merged.groupby('article_type').size().reset_index(name='Return Count')
        fig_pie = px.pie(rev_stats, values='Return Count', names='article_type', 
                         hole=0.4, title="Returns by Category")
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- BOTTOM ROW: GEOGRAPHICAL PERFORMANCE ---
    st.subheader("🌍 Revenue Heatmap (By State)")
    state_perf = df_sales.groupby('location')['invoiceamount'].sum().sort_values(ascending=False).reset_index()
    fig_state = px.bar(state_perf, x='location', y='invoiceamount', color='invoiceamount',
                       color_continuous_scale='Greens')
    st.plotly_chart(fig_state, use_container_width=True)

    # --- AUDIT TABLE ---
    with st.expander("📝 Detailed Audit: Packet-by-Packet Settlement"):
        st.write("Compare the order value with the bank settlement for every single packet.")
        st.dataframe(df_audit[['order_id', 'packet_id', 'SKU', 'invoiceamount', 'total_actual_settlement', 'leakage']])

except Exception as e:
    st.error(f"Execution Error: {e}")
    st.info("Ensure all three filenames match exactly: 'Sales Jan-26...', 'PG Forward...', 'PG Reverse...'")
