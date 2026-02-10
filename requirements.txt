import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Stitching Management System", layout="wide")

if 'work_data' not in st.session_state:
    # Adding some initial mock data for the Reconciliation side
    st.session_state['work_data'] = pd.DataFrame({
        'Date': ['2026-02-01', '2026-02-02'],
        'Employee Name': ['Ahmed', 'Suresh'],
        'Style': ['CLASSIC DENIM', 'COTTON TEE'],
        'Challan Number': ['CH-001', 'CH-002'],
        'Hours Worked': [8.0, 7.5],
        'Weight (kg)': [12.5, 10.0],
        'Actual Cost': [450, 120],  # Added for reconciliation
        'Master Cost': [420, 150]   # Added for reconciliation
    })

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Daily Work Entry", "Cost Reconciliation"])

# --- 3. PAGE 1: DAILY WORK ENTRY ---
if page == "Daily Work Entry":
    st.title("🧵 Employee Work Entry")
    
    with st.form(key="entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Employee Name")
            style = st.text_input("Style")
        with col2:
            challan = st.text_input("Challan Number")
            hours = st.number_input("Hours Worked", min_value=0.0, step=0.5)
        with col3:
            actual_cost = st.number_input("Actual Labor Cost", min_value=0)
            master_cost = st.number_input("Master/Budget Cost", min_value=0)
            
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            new_row = {
                "Date": datetime.today().strftime('%Y-%m-%d'),
                "Employee Name": name,
                "Style": style.upper(),
                "Challan Number": challan,
                "Hours Worked": hours,
                "Actual Cost": actual_cost,
                "Master Cost": master_cost
            }
            st.session_state['work_data'] = pd.concat([st.session_state['work_data'], pd.DataFrame([new_row])], ignore_index=True)
            st.success("Entry Saved!")

    st.subheader("Recent Logs")
    st.dataframe(st.session_state['work_data'], use_container_width=True)

# --- 4. PAGE 2: COST RECONCILIATION ---
elif page == "Cost Reconciliation":
    st.title("📊 Costing & Reconciliation")
    df = st.session_state['work_data']

    if df.empty:
        st.warning("No data available. Please enter work logs first.")
    else:
        # Calculations
        df['Variance'] = df['Actual Cost'] - df['Master Cost']
        
        # Dashboard Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Actual Cost", f"₹{df['Actual Cost'].sum()}")
        m2.metric("Total Master Cost", f"₹{df['Master Cost'].sum()}")
        m3.metric("Net Variance", f"₹{df['Variance'].sum()}", delta=float(-df['Variance'].sum()), delta_color="inverse")

        # Graph
        fig = px.bar(df, x="Style", y=["Actual Cost", "Master Cost"], 
                     barmode="group", title="Actual vs Master Cost by Style")
        st.plotly_chart(fig, use_container_width=True)

        # Drill-down
        selected_style = st.selectbox("Select Style for Detail", df['Style'].unique())
        style_df = df[df['Style'] == selected_style]
        st.write(f"Detailed logs for {selected_style}:")
        st.table(style_df[['Date', 'Employee Name', 'Actual Cost', 'Master Cost', 'Variance']])
