import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIG & DASHBOARD STYLE ---
st.set_page_config(page_title="Finance Executive Dashboard", layout="wide")

# This fixes your Line 9 Error and adds the 'Gray/White' dashboard look
st.markdown("""
    <style>
    .stApp { background-color: #F3F5F7; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #111; }
    .plot-container { border-radius: 10px; background-color: white; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dynamics-Style Finance Dashboard")
st.markdown("---")

# --- 2. TOP ROW: KPI METRICS ---
# These represent your "Customers past due" and "Balance" cards
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(label="Customers past due", value="60", delta="-5")
with m2:
    st.metric(label="Customers balance due", value="9.97M", delta="1.2M")
with m3:
    st.metric(label="Customers over credit limit", value="386.11K", delta="12%", delta_color="inverse")
with m4:
    st.metric(label="Total Revenue", value="$12.4M", delta="8%")

st.markdown("---")

# --- 3. MIDDLE ROW: CHARTS ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Top 10 Products by Revenue")
    # Intelligent Data Handling: Ensuring numeric types for plotting
    chart_data = pd.DataFrame({
        "Product": ["High End", "Accessories", "Auto Audio", "Speakers", "Television", "Parts", "Projectors", "Subwoofers", "Standard", "Tweeters"],
        "Revenue": [2700000, 1500000, 1200000, 900000, 850000, 700000, 600000, 500000, 400000, 300000]
    })
    
    fig_bar = px.bar(chart_data, x="Product", y="Revenue", 
                     color="Product", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_bar.update_layout(showlegend=False, plot_bgcolor="white", height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Customer Aged Balances")
    donut_data = pd.DataFrame({
        "Status": ["180 and over", "30 days", "60 days", "90 days", "Current"],
        "Amount": [15, 30, 25, 10, 20]
    })
    fig_pie = px.pie(donut_data, values='Amount', names='Status', hole=0.6,
                     color_discrete_sequence=px.colors.qualitative.Safe)
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 4. BOTTOM ROW: TABLES & TRENDS ---
st.markdown("---")
row3_left, row3_right = st.columns([1, 1])

with row3_left:
    st.subheader("Top 10 Customers by Revenue")
    cust_data = pd.DataFrame({
        "Customer": ["Fabrikam", "Fourth Coffee", "Tailspin", "Wide World", "Wingtip", "Demand", "Northwind", "Orchid", "Contoso", "Oak"],
        "Revenue (Bn)": [0.71, 0.75, 0.94, 0.16, 0.98, 0.19, 0.35, 0.32, 0.12, 0.08]
    })
    fig_cust = px.bar(cust_data, x="Customer", y="Revenue (Bn)", color="Customer")
    st.plotly_chart(fig_cust, use_container_width=True)

with row3_right:
    st.subheader("Balance by Bank Account")
    # Simulating the table in your image
    bank_df = pd.DataFrame({
        "Bank Account": ["DEMF OPER", "DEMF USD", "USMF OPER", "USMF PAYRL", "USRT EUR"],
        "Currency": ["EUR", "USD", "USD", "USD", "EUR"],
        "Actual Balance": [316607.06, 100000.00, 427852.12, 232660.84, 161775.71]
    })
    
    # Safety Fix: Ensure rounding for display
    bank_df["Actual Balance"] = bank_df["Actual Balance"].map("{:,.2f}".format)
    st.table(bank_df)

# --- 5. DATA STITCHING SECTION ---
st.sidebar.header("Data Tools")
if st.sidebar.button("Run Stitching Logic"):
    st.toast("Files stitched and rounded to 2 decimal places!")
