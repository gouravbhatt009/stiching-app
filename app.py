import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="ProFactory ERP v2", layout="wide")
FILES = {"workers": "workers.csv", "styles": "styles.csv", "grid": "floor_sheet.csv"}

def load_data(file_key, default_df):
    if os.path.exists(FILES[file_key]):
        return pd.read_csv(FILES[file_key])
    return default_df

# --- 2. DATA INITIALIZATION ---
if 'init' not in st.session_state:
    st.session_state['workers'] = load_data(
        "workers", 
        pd.DataFrame({"Name": ["Nazim"], "Daily Wage": [500]})
    )
    st.session_state['styles'] = load_data(
        "styles", 
        pd.DataFrame({"Style": ["1006YKBLUE"], "Challan": ["10003"], "Issued Qty": [200]})
    )
    
    # Time slots for floor sheet
    time_slots = [f"{h} to {h+1}" for h in range(9, 18)]
    grid_init = pd.DataFrame({"Worker Name": st.session_state['workers']['Name']})
    for slot in time_slots:
        grid_init[slot] = None
    st.session_state['grid'] = load_data("grid", grid_init)
    st.session_state['init'] = True

# --- 3. UI TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Analysis", "🕒 Live Floor Sheet", "⚙️ Setup & Data Bridge"])

# --- TAB 1: EXECUTIVE ANALYSIS (Export Reports) ---
with tab1:
    st.title("💰 Production & Costing Summary")
    
    workers = st.session_state['workers']
    grid = st.session_state['grid']
    wage_map = dict(zip(workers['Name'], workers['Daily Wage']))
    
    style_costs = {s: 0 for s in st.session_state['styles']['Style'].tolist()}
    time_cols = [c for c in grid.columns if " to " in c]

    for _, row in grid.iterrows():
        hourly_rate = wage_map.get(row['Worker Name'], 0) / 8
        for col in time_cols:
            if pd.notna(row[col]) and row[col] in style_costs:
                style_costs[row[col]] += hourly_rate

    summary_df = pd.DataFrame([
        {"Style": k, "Labor Cost": round(v, 2), "Total with Overheads": round(v + 3150, 2)} 
        for k, v in style_costs.items()
    ])

    st.dataframe(summary_df, use_container_width=True)

    # --- EXPORT SECTION ---
    st.subheader("📤 Export for Management")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Costing_Report')
        grid.to_excel(writer, index=False, sheet_name='Floor_Attendance')
    
    st.download_button(
        label="📥 Download Full Excel Report",
        data=buffer.getvalue(),
        file_name=f"Factory_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- TAB 2: LIVE FLOOR SHEET ---
with tab2:
    st.header("Daily Matrix")
    st.caption("Edit the worker assignments for each time slot directly below:")

    # Editable grid without SelectColumn
    edited_grid = st.data_editor(
        st.session_state['grid'],
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("💾 Save Matrix"):
        st.session_state['grid'] = edited_grid
        edited_grid.to_csv(FILES["grid"], index=False)
        st.success("Matrix saved successfully!")

# --- TAB 3: SETUP & DATA BRIDGE (Upload Function) ---
with tab3:
    st.title("🛠️ System Administration")
    
    st.subheader("📥 Data Bridge (Upload Excel/CSV)")
    st.markdown("Upload Excel/CSV files to bulk-update your Worker or Style lists.")
    
    up_col1, up_col2 = st.columns(2)
    
    with up_col1:
        uploaded_workers = st.file_uploader("Upload Worker List (Excel/CSV)", type=['csv', 'xlsx'])
        if uploaded_workers:
            df_up = pd.read_excel(uploaded_workers) if uploaded_workers.name.endswith('.xlsx') else pd.read_csv(uploaded_workers)
            if st.button("Confirm Worker Import"):
                st.session_state['workers'] = df_up
                df_up.to_csv(FILES["workers"], index=False)
                st.success(f"Imported {len(df_up)} workers!")

    with up_col2:
        uploaded_styles = st.file_uploader("Upload Style Master (Excel/CSV)", type=['csv', 'xlsx'])
        if uploaded_styles:
            df_up_s = pd.read_excel(uploaded_styles) if uploaded_styles.name.endswith('.xlsx') else pd.read_csv(uploaded_styles)
            if st.button("Confirm Style Import"):
                st.session_state['styles'] = df_up_s
                df_up_s.to_csv(FILES["styles"], index=False)
                st.success("Styles updated!")

    st.divider()
    st.write("Current Manual Setup:")
    st.data_editor(st.session_state['workers'], num_rows="dynamic", key="manual_worker")
    st.data_editor(st.session_state['styles'], num_rows="dynamic", key="manual_style")
