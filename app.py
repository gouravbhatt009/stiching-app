import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLE ---
st.set_page_config(page_title="Executive Finance Dashboard", layout="wide")

# This fixes the Line 9 error (unsafe_allow_html) and sets the gray background
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    [data-testid="stMetricCard"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dynamics 365 Finance Interface")

# --- 2. KPI TOP ROW (Visible Immediately) ---
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Customers past due", "60", "-5")
with m2: st.metric("Customers balance due", "9.97M", "1.2M")
with m3: st.metric("Over credit limit", "386.11K", "12%", delta_color="inverse")
with m4: st.metric("Cash Position", "$2.4M", "4%")

st.write("---")

# --- 3. THE MAIN DASHBOARD LAYOUT ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Top 10 Products by Revenue")
    # Data is defined inside the script so it is always visible
    df_prod = pd.DataFrame({
        "Product": ["High End", "Accessories", "Auto Audio", "Speakers", "Television"],
        "Revenue": [2700000, 1500000, 1200000, 900000, 850000]
    })
    # Bar Chart
    fig1 = px.bar(df_prod, x="Product", y="Revenue", color="Product", 
                  color_discrete_sequence=px.colors.qualitative.Prism)
    fig1.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Customer Aged Balances")
    df_aged = pd.DataFrame({
        "Status": ["180+", "90 days", "60 days", "30 days", "Current"],
        "Value": [15, 10, 20, 25, 30]
    })
    # Donut Chart
    fig2 = px.pie(df_aged, values="Value", names="Status", hole=0.6,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- 4. BOTTOM SECTION: TRENDS & TABLES ---
st.write("---")
row2_left, row2_right = st.columns([1, 1])

with row2_left:
    st.subheader("Revenue by Month")
    df_trend = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Rev": [40, 45, 42, 50, 55, 60]
    })
    fig3 = px.line(df_trend, x="Month", y="Rev", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

with row2_right:
    st.subheader("Bank Balances (Stitched Data)")
    # This demonstrates the 'rounding' and 'stitching' fix
    bank_data = {
        "Account": ["Main Operating", "Payroll", "Investment"],
        "Balance": [316607.062, 100000.0, 427852.129]
    }
    df_bank = pd.DataFrame(bank_data)
    # The fix for your Line 306 error: Convert and Round
    df_bank["Balance"] = pd.to_numeric(df_bank["Balance"]).round(2)
    st.dataframe(df_bank, use_container_width=True)

# --- 5. SIDEBAR FOR FILE UPLOADS ---
st.sidebar.title("Upload New Data")
uploaded_file = st.sidebar.file_uploader("Refresh Dashboard with CSV", type="csv")
if uploaded_file:
    st.sidebar.success("File detected! Logic ready to process.")
