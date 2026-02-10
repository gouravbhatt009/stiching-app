import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Stitching Management", layout="wide")

# Initialize Session State for Data Persistence during the session
if 'work_data' not in st.session_state:
    st.session_state['work_data'] = pd.DataFrame(columns=[
        'Date', 'Employee Name', 'Style', 'Challan Number', 
        'Hours Worked', 'Weight (kg)', 'Actual Cost', 'Master Cost'
    ])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🪡 Navigation")
page = st.sidebar.radio("Select Page:", ["Work Entry Form", "Costing Dashboard"])

# --- PAGE 1: WORK ENTRY ---
if page == "Work Entry Form":
    st.title("Employee Work Entry")
    
    with st.form(key="entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Employee Name")
            style = st.text_input("Style (e.g., 1065YK)")
            challan = st.text_input("Challan Number")
        with col2:
            hours = st.number_input("Hours Worked", min_value=0.0, step=0.5)
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
            actual_cost = st.number_input("Actual Labor Cost (₹)", min_value=0)
            master_cost = st.number_input("Master/Budget Cost (₹)", min_value=0)
        
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            if not name or not style:
                st.error("Please fill in the Name and Style.")
            else:
                new_entry = {
                    "Date": datetime.today().strftime('%Y-%m-%d'),
                    "Employee Name": name,
                    "Style": style.upper(),
                    "Challan Number": challan,
                    "Hours Worked": hours,
                    "Weight (kg)": weight,
                    "Actual Cost": actual_cost,
                    "Master Cost": master_cost
                }
                # Add to dataframe
                st.session_state['work_data'] = pd.concat([st.session_state['work_data'], pd.DataFrame([new_entry])], ignore_index=True)
                st.success(f"Record for {name} added!")

    st.subheader("Today's Entries")
    st.dataframe(st.session_state['work_data'], use_container_width=True)

# --- PAGE 2: COSTING DASHBOARD ---
elif page == "Costing Dashboard":
    st.title("📊 Profit & Cost Analysis")
    df = st.session_state['work_data']

    if df.empty:
        st.info("No data available yet. Go to 'Work Entry Form' to add data.")
    else:
        # Calculations
        df['Variance'] = df['Master Cost'] - df['Actual Cost'] # Positive = Savings
        
        # Top Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Actual Spend", f"₹{df['Actual Cost'].sum()}")
        m2.metric("Total Budget (Master)", f"₹{df['Master Cost'].sum()}")
        m3.metric("Net Savings/Loss", f"₹{df['Variance'].sum()}")

        # Plotly Chart (This is what caused your error - fixed by requirements.txt)
        fig = px.bar(df, x="Style", y=["Actual Cost", "Master Cost"], 
                     barmode="group", title="Cost Comparison per Style")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detailed Reconciliation Table")
        st.table(df[['Date', 'Style', 'Employee Name', 'Actual Cost', 'Master Cost', 'Variance']])
