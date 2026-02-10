import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- SETTINGS & PERSISTENCE ---
DB_FILE = "ultra_max_stitching_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        'Date', 'Employee', 'Style', 'Hours', 'Weight', 
        'Actual Cost', 'Master Cost', 'Pieces Done', 'Efficiency %'
    ])

if 'work_data' not in st.session_state:
    st.session_state['work_data'] = load_data()

st.set_page_config(page_title="Ultra Max Stitching Pro", layout="wide")

# --- SIDEBAR: MASTER SETTINGS ---
st.sidebar.title("🛠️ Control Center")
menu = st.sidebar.selectbox("Go to", ["Live Production Entry", "Ultra Analytics", "Worker Payroll"])

# Preset Rates (You can change these in code or make them settings)
STYLE_TARGETS = {"1065YK": 10, "TSHIRT": 25, "DENIM": 8} # Pieces per hour

# --- PAGE 1: DIGITAL ENTRY ---
if menu == "Live Production Entry":
    st.title("🚀 Live Production Input")
    
    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            emp = st.text_input("Worker Name")
            style = st.selectbox("Style Code", list(STYLE_TARGETS.keys()))
        with c2:
            hrs = st.number_input("Hours Worked", min_value=0.1, value=8.0)
            pieces = st.number_input("Total Pieces Produced", min_value=1)
        with c3:
            act_cost = st.number_input("Labor Paid (₹)", min_value=0)
            mas_cost = st.number_input("Master Budget (₹)", min_value=0)

        if st.form_submit_button("Submit to Cloud"):
            # --- ULTRA MAX CALCULATIONS ---
            # 1. Efficiency Calculation
            target_for_hrs = STYLE_TARGETS[style] * hrs
            efficiency = (pieces / target_for_hrs) * 100
            
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Employee": emp,
                "Style": style,
                "Hours": hrs,
                "Pieces Done": pieces,
                "Actual Cost": act_cost,
                "Master Cost": mas_cost,
                "Efficiency %": round(efficiency, 2)
            }
            
            # Save to File
            df = pd.concat([st.session_state['work_data'], pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state['work_data'] = df
            st.success(f"Record Saved! Worker Efficiency: {efficiency:.1f}%")

    st.subheader("Today's Production Log")
    st.dataframe(st.session_state['work_data'].tail(10), use_container_width=True)

# --- PAGE 2: ULTRA ANALYTICS ---
elif menu == "Ultra Analytics":
    st.title("📊 Ultra Max Dashboard")
    df = st.session_state['work_data']
    
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pieces Produced", int(df['Pieces Done'].sum()))
        m2.metric("Avg Department Efficiency", f"{df['Efficiency %'].mean():.1f}%")
        
        # Financial Health
        total_variance = df['Master Cost'].sum() - df['Actual Cost'].sum()
        m3.metric("Net Savings/Loss", f"₹{total_variance}", delta=int(total_variance))

        # Efficiency Chart
        import plotly.express as px
        fig = px.line(df, x="Date", y="Efficiency %", color="Employee", title="Worker Performance Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Wait for data entry to see analytics.")

# --- PAGE 3: WORKER PAYROLL ---
elif menu == "Worker Payroll":
    st.title("💰 Worker Salary Summary")
    df = st.session_state['work_data']
    if not df.empty:
        salary_sheet = df.groupby("Employee").agg({
            'Actual Cost': 'sum',
            'Pieces Done': 'sum',
            'Hours': 'sum'
        }).reset_index()
        st.table(salary_sheet)
