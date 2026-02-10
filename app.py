import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SETTINGS & TOOL SETUP ---
st.set_page_config(page_title="Ultra-Max Production ERP", layout="wide")

# File paths
FILES = {"workers": "workers.csv", "styles": "styles.csv", "grid": "floor_sheet.csv"}

def load_data(file_key, default_df):
    if os.path.exists(FILES[file_key]):
        return pd.read_csv(FILES[file_key])
    return default_df

# --- 2. SMART DATA INITIALIZATION ---
if 'init' not in st.session_state:
    # Workers Data
    st.session_state['workers'] = load_data(
        "workers",
        pd.DataFrame({
            "Name": ["Nazim", "Rahul", "Tanu", "Raju", "Rita"],
            "Daily Wage": [500, 400, 600, 200, 300]
        })
    )

    # Styles Data
    st.session_state['styles'] = load_data(
        "styles",
        pd.DataFrame({
            "Style": ["1006YKBLUE", "1005YKBLACK", "1888WINE"],
            "Challan": ["10003", "10004", "10005"],
            "Issued Qty": [200, 150, 300]
        })
    )

    # Time slots
    time_slots = [f"{h} to {h+1}" for h in range(9, 18)]

    # Floor grid
    if os.path.exists(FILES["grid"]):
        st.session_state['grid'] = pd.read_csv(FILES["grid"])
    else:
        grid_init = pd.DataFrame({"Worker Name": st.session_state['workers']['Name']})
        for slot in time_slots:
            grid_init[slot] = None
        st.session_state['grid'] = grid_init

    st.session_state['init'] = True

# --- 3. TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🕒 Hourly Floor Sheet", "⚙️ Setup Master"])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab1:
    st.title("💰 Style-Wise Profitability")

    grid = st.session_state['grid']
    workers = st.session_state['workers']
    styles = st.session_state['styles']

    # Map wages
    wage_map = dict(zip(workers['Name'], workers['Daily Wage']))

    # Calculate labor cost per style
    style_costs = {s: 0 for s in styles['Style'].tolist()}
    time_cols = [c for c in grid.columns if " to " in c]

    for _, row in grid.iterrows():
        daily_wage = wage_map.get(row['Worker Name'], 0)
        hourly_rate = daily_wage / 8
        for col in time_cols:
            style_assigned = row[col]
            if pd.notna(style_assigned) and style_assigned in style_costs:
                style_costs[style_assigned] += hourly_rate

    # Summary table
    summary_data = []
    for _, s_row in styles.iterrows():
        s_name = s_row['Style']
        labor = style_costs.get(s_name, 0)
        total_cost = labor + 100 + 3000  # Example overheads

        summary_data.append({
            "Style": s_name,
            "Challan": s_row['Challan'],
            "Labor Cost (₹)": round(labor, 2),
            "Total Cost (Inc. Overheads)": round(total_cost, 2),
            "Cost Per Pc": round(total_cost / s_row['Issued Qty'], 2) if s_row['Issued Qty'] > 0 else 0
        })

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

    # Bar chart
    fig = px.bar(summary_df, x="Style", y="Total Cost (Inc. Overheads)", title="Budget Consumption by Style")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: HOURLY FLOOR SHEET ---
with tab2:
    st.header("Daily Production Matrix")
    st.caption("Assign Styles to workers for each hour slot below.")

    # Simple editable grid (dropdowns not forced, user can type style name)
    edited_grid = st.data_editor(
        st.session_state['grid'],
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 Save All Floor Data"):
        st.session_state['grid'] = edited_grid
        edited_grid.to_csv(FILES["grid"], index=False)
        st.success("Floor sheet updated!")

# --- TAB 3: SETUP MASTER ---
with tab3:
    st.header("Master Data Management")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Worker Wages")
        edited_workers = st.data_editor(st.session_state['workers'], num_rows="dynamic")
        if st.button("Save Workers"):
            st.session_state['workers'] = edited_workers
            edited_workers.to_csv(FILES["workers"], index=False)
            st.success("Worker master updated!")

    with c2:
        st.subheader("Style/Challan Details")
        edited_styles = st.data_editor(st.session_state['styles'], num_rows="dynamic")
        if st.button("Save Styles"):
            st.session_state['styles'] = edited_styles
            edited_styles.to_csv(FILES["styles"], index=False)
            st.success("Style master updated!")
