import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="Stitching Management System", layout="wide")

# This keeps your data stored while the app is running
if 'work_data' not in st.session_state:
    st.session_state['work_data'] = pd.DataFrame(columns=[
        'Date', 'Employee Name', 'Style', 'Challan Number', 
        'Hours Worked', 'Actual Cost', 'Master Cost'
    ])

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("🧵 Stitching Dept.")
page = st.sidebar.radio("Navigation", ["Daily Work Entry", "Cost Reconciliation"])

# --- 3. PAGE: DAILY WORK ENTRY ---
if page == "Daily Work Entry":
    st.title("Employee Work Entry")
    st.write("Fill in the details below to record daily production.")
    
    with st.form(key="entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Employee Name")
            style = st.text_input("Style (e.g., 1065YK)")
            challan = st.text_input("Challan Number")
        with col2:
            hours = st.number_input("Hours Worked", min_value=0.0, step=0.5)
            actual_cost = st.number_input("Actual Labor Cost (₹)", min_value=0)
            master_cost = st.number_input("Master/Budget Cost (₹)", min_value=0)
            
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if not name or not style:
                st.error("Please provide at least Name and Style.")
            else:
                new_row = {
                    "Date": datetime.today().strftime('%Y-%m-%d'),
                    "Employee Name": name,
                    "Style": style.upper(),
                    "Challan Number": challan,
                    "Hours Worked": hours,
                    "Actual Cost": actual_cost,
                    "Master Cost": master_cost
                }
                # Add the new row to our database
                st.session_state['work_data'] = pd.concat([st.session_state['work_data'], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Record for {name} saved successfully!")

    st.subheader("Recent Entries")
    st.dataframe(st.session_state['work_data'], use_container_width=True)

# --- 4. PAGE: COST RECONCILIATION ---
elif page == "Cost Reconciliation":
    st.title("📊 Costing & Reconciliation")
    df = st.session_state['work_data']

    if df.empty:
        st.info("No data available. Please enter some records in the 'Daily Work Entry' page first.")
    else:
        # Calculate Variance
        df['Variance'] = df['Master Cost'] - df['Actual Cost']
        
        # Summary Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Actual Cost", f"₹{df['Actual Cost'].sum()}")
        m2.metric("Total Master Cost", f"₹{df['Master Cost'].sum()}")
        m3.metric("Net Profit/Loss", f"₹{df['Variance'].sum()}")

        # Dynamic Comparison Graph
        st.subheader("Actual vs Master Cost Comparison")
        fig = px.bar(df, x="Style", y=["Actual Cost", "Master Cost"], 
                     barmode="group", color_discrete_sequence=["#EF553B", "#636EFA"])
        st.plotly_chart(fig, use_container_width=True)

        # Download Option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report (CSV)", data=csv, file_name="stitching_report.csv", mime="text/csv")
