import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Ultra Max Production Grid", layout="wide")

# Define our Hourly Columns
TIME_SLOTS = ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4", "4-5", "5-6"]

# --- 2. DATA CORE ---
DB_FILE = "hourly_production_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # If no file, create a blank starting grid for 50 workers
    initial_data = []
    for i in range(1, 51):
        row = {"Worker Name": f"Worker {i}", "Style": ""}
        for slot in TIME_SLOTS:
            row[slot] = 0  # Default production is 0
        initial_data.append(row)
    return pd.DataFrame(initial_data)

if 'grid_data' not in st.session_state:
    st.session_state['grid_data'] = load_data()

# --- 3. UI TABS ---
tab1, tab2 = st.tabs(["🕒 Hourly Production Grid", "📊 Daily Summary"])

with tab1:
    st.title("Digital Production Sheet")
    st.info("💡 Instructions: Type the **Style Name** in the Style column and the **Pieces Produced** in the hourly slots. The app saves automatically when you click the button below.")

    # --- THE EDITABLE GRID ---
    # This allows you to edit 50 rows at once like Excel
    edited_df = st.data_editor(
        st.session_state['grid_data'],
        use_container_width=True,
        num_rows="dynamic", # Allows you to add/delete workers
        column_config={
            "Worker Name": st.column_config.TextColumn("Employee Name", width="medium", required=True),
            "Style": st.column_config.TextColumn("Current Style", width="small"),
        }
    )

    # Save Button
    if st.button("💾 Save All Changes"):
        edited_df.to_csv(DB_FILE, index=False)
        st.session_state['grid_data'] = edited_df
        st.success(f"Successfully updated production for {len(edited_df)} workers!")

with tab2:
    st.header("Daily Analytics")
    df = st.session_state['grid_data']
    
    # Calculate Total Pieces across all time slots
    df['Total Daily'] = df[TIME_SLOTS].sum(axis=1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Performers")
        top_workers = df[['Worker Name', 'Total Daily']].sort_values(by='Total Daily', ascending=False).head(10)
        st.table(top_workers)
        
    with col2:
        st.subheader("Hourly Peak Flow")
        hourly_totals = df[TIME_SLOTS].sum()
        st.bar_chart(hourly_totals)

    # Download for Office Use
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Excel/CSV Report", data=csv, file_name="daily_production.csv", mime="text/csv")
