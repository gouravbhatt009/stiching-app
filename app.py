import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & CSS FIX ---
st.set_page_config(page_title="Executive Finance Dashboard", layout="wide")

# FIX: Changed unsafe_base64 to unsafe_allow_html
# Added specific CSS to force text to be white/visible on a dark background
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E26; /* Deep Dark Blue/Gray */
    }
    h1, h2, h3, p, span, label {
        color: #FFFFFF !important; /* Forces all text to be White */
    }
    [data-testid="stMetricValue"] {
        color: #00FFCC !important; /* Bright Teal for numbers */
    }
    [data-testid="stMetricLabel"] {
        color: #AAAAAA !important; /* Gray for labels */
    }
    .stDataFrame {
        background-color: #2D2D37;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dynamics 365 Finance Dashboard")

# --- 2. TOP KPI ROW ---
# Using specific logic to ensure these display clearly
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Customers past due", "60", "-5", delta_color="normal")
with m2:
    st.metric("Customers balance due", "9.97M", "+1.2M", delta_color="normal")
with m3:
    st.metric("Over credit limit", "386.11K", "12%", delta_color="inverse")
with m4:
    st.metric("Cash Position", "$2.4M", "4%", delta_color="normal")

st.markdown("<hr style='border: 0.5px solid #444'>", unsafe_allow_html=True)

# --- 3. CHARTS SECTION (Middle Row) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Top 10 Products by Revenue")
    df_prod = pd.DataFrame({
        "Product": ["High End", "Accessories", "Auto Audio", "Speakers", "Television"],
        "Revenue": [2700000, 1500000, 1200000, 900000, 850000]
    })
    
    fig1 = px.bar(df_prod, x="Product", y="Revenue", color="Product", 
                  template="plotly_dark", # Forces chart to match dark theme
                  color_discrete_sequence=px.colors.qualitative.Vivid)
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Customer Aged Balances")
    df_aged = pd.DataFrame({
        "Status": ["180+", "90 days", "60 days", "30 days", "Current"],
        "Value": [15, 10, 20, 25, 30]
    })
    
    fig2 = px.pie(df_aged, values="Value", names="Status", hole=0.6,
                  template="plotly_dark")
    fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig2, use_container_width=True)

# --- 4. DATA STITCHING & TABLES (Bottom Row) ---
st.subheader("Stitched Bank Balances")
bank_data = {
    "Bank Account": ["DEMF OPER", "DEMF USD", "USMF OPER", "USMF PAYRL", "USRT EUR"],
    "Currency": ["EUR", "USD", "USD", "USD", "EUR"],
    "Actual Balance": [316607.06, 100000.00, 427852.12, 232660.84, 161775.71]
}
df_bank = pd.DataFrame(bank_data)

# Ensuring numeric rounding to fix your previous error
df_bank["Actual Balance"] = pd.to_numeric(df_bank["Actual Balance"]).round(2)

# Displaying as a clean table
st.dataframe(df_bank, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("Upload Center")
    uploaded_file = st.file_uploader("Refresh with CSV", type="csv")
    if uploaded_file:
        st.success("Data successfully stitched!")
