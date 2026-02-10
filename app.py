import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. DATA CORE (Permanent Storage) ---
DB_FILE = "stitching_master_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['Date', 'Employee', 'Style', 'Pieces', 'Actual Cost', 'Master Cost'])

if 'work_data' not in st.session_state:
    st.session_state['work_data'] = load_data()

st.set_page_config(page_title="Ultra Max Stitching Dashboard", layout="wide")

# --- 2. THE TABS (Navigation) ---
# This creates the navigation at the top of the screen
tab1, tab2, tab3, tab4 = st.tabs(["📝 Work Entry", "📊 Analytics", "🧵 Inventory", "⚙️ Settings"])

# --- 3. TAB 1: WORK ENTRY ---
with tab1:
    st.header("Daily Production Entry")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            emp = st.text_input("Worker Name")
            style = st.text_input("Style Number")
        with col2:
            pieces = st.number_input("Pieces Done", min_value=1)
            cost = st.number_input("Labor Cost (₹)", min_value=0)
            m_cost = st.number_input("Master Budget (₹)", min_value=0)
        
        if st.form_submit_button("Save to Database"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Employee": emp, "Style": style, "Pieces": pieces, 
                "Actual Cost": cost, "Master Cost": m_cost
            }])
            updated_df = pd.concat([st.session_state['work_data'], new_row], ignore_index=True)
            updated_df.to_csv(DB_FILE, index=False)
            st.session_state['work_data'] = updated_df
            st.success("Entry Saved Successfully!")

    st.subheader("Recent Logs")
    st.dataframe(st.session_state['work_data'].tail(5), use_container_width=True)

# --- 4. TAB 2: ANALYTICS ---
with tab2:
    st.header("Financial & Production Dashboard")
    df = st.session_state['work_data']
    if not df.empty:
        # High-level Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pieces", int(df['Pieces'].sum()))
        m2.metric("Total Spend", f"₹{df['Actual Cost'].sum()}")
        variance = df['Master Cost'].sum() - df['Actual Cost'].sum()
        m3.metric("Profit/Loss", f"₹{variance}", delta=int(variance))

        # Efficiency Graph
        fig = px.bar(df, x="Style", y="Pieces", color="Employee", title="Pieces by Style")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to show yet.")

# --- 5. TAB 3: INVENTORY ---
with tab3:
    st.header("Fabric & Material Stock")
    st.write("Current Stock Levels (Demo)")
    # You can expand this later with a new CSV for materials
    inventory_data = pd.DataFrame({
        "Material": ["Denim Fabric", "Cotton Thread", "Zippers", "Buttons"],
        "Stock": ["500 Meters", "200 Rolls", "1500 Pcs", "5000 Pcs"],
        "Status": ["Good", "Low", "Good", "Good"]
    })
    st.table(inventory_data)

# --- 6. TAB 4: SETTINGS ---
with tab4:
    st.header("System Settings")
    if st.button("🗑️ Clear All Data (Permanent)"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state['work_data'] = pd.DataFrame(columns=['Date', 'Employee', 'Style', 'Pieces', 'Actual Cost', 'Master Cost'])
        st.warning("Database Deleted!")
        st.rerun()
