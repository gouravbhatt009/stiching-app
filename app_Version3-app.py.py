import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Stitching Department - Employee Work Entry")

if 'work_data' not in st.session_state:
    st.session_state['work_data'] = []

with st.form(key="entry_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Employee Name")
        style = st.text_input("Style (e.g., 1065YKBlack)")
    with col2:
        challan = st.text_input("Challan Number")
        hours = st.number_input("Hours Worked", min_value=0.0, step=0.5)
    with col3:
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        date = st.date_input("Date", datetime.today())
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if not name or not style or not challan or hours <= 0:
            st.error("Please fill all required fields and ensure hours > 0.")
        else:
            st.session_state['work_data'].append({
                "Date": date,
                "Employee Name": name,
                "Style": style,
                "Challan Number": challan,
                "Hours Worked": hours,
                "Weight (kg)": weight
            })
            st.success(f"Added entry for {name}!")

if st.session_state['work_data']:
    df = pd.DataFrame(st.session_state['work_data'])
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="work_entries.csv", mime="text/csv")
else:
    st.info("Add entries above to see the table here.")