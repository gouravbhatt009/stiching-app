import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SETTINGS & TOOL SETUP ---
st.set_page_config(page_title="Ultra-Max Production ERP", layout="wide")

# This is where your data is saved so it's never lost
FILES = {"workers": "workers.csv", "styles": "styles.csv", "grid": "floor_sheet.csv"}

def load_data(file_key, default_df):
    if os.path.exists(FILES[file_key]):
        return pd.read_csv(FILES[file_key])
    return default_df

# --- 2. SMART DATA INITIALIZATION ---
if 'init' not in st.session_state:
    # Initial Worker Data (Matches your Image 2)
    st.session_state['workers'] = load_data("workers", pd.DataFrame({
        "Name": ["Nazim", "Rahul", "Tanu", "Raju", "Rita"],
        "Daily Wage": [500, 400, 600, 200, 300]
    }))
    
    # Initial Style/Challan Data (Matches your Image 3)
    st.session_state['styles'] = load_data("styles", pd.DataFrame({
        "Style": ["1006YKBLUE", "1005YKBLACK", "1888WINE"],
        "Challan": ["10003", "10004", "10005"],
        "Issued Qty": [200, 150, 300]
    }))
    
    # Create the Time Grid (9 to 18)
    time_slots = [f"{h} to {h+1}" for h in range(9, 18)]
    if os.path.exists(FILES["grid"]):
        st.session_state['grid'] = pd.read_csv(FILES["grid"])
    else:
        # Build blank grid for all workers
        grid_init = pd.DataFrame({"Worker Name": st.session_state['workers']['Name']})
        for slot in time_slots:
            grid_init[slot] = None
        st.session_state['grid'] = grid_init
    
    st.session_state['init'] = True

# --- 3. THE INTERFACE (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🕒 Hourly Floor Sheet", "⚙️ Setup Master"])

# --- TAB 1: EXECUTIVE DASHBOARD (The "Promotion" Page) ---
with tab1:
    st.title("💰 Style-Wise Profitability")
    
    # Calculation Engine
    grid = st.session_state['grid']
    workers = st.session_state['workers']
    styles = st.session_state['styles']
    
    # Map wages to workers for easy math
    wage_map = dict(zip(workers['Name'], workers['Daily Wage']))
    
    # Calculate Total Labor Cost per Style
    style_costs = {s: 0 for s in styles['Style'].tolist()}
    time_cols = [c for c in grid.columns if " to " in c]
    
    for _, row in grid.iterrows():
        daily_wage = wage_map.get(row['Worker Name'], 0)
        hourly_rate = daily_wage / 8 # Assuming 8 hour shift
        for col in time_cols:
            style_assigned = row[col]
            if style_assigned in style_costs:
                style_costs[style_assigned] += hourly_rate

    # Create Summary Table
    summary_data = []
    for _, s_row in styles.iterrows():
        s_name = s_row['Style']
        labor = style_costs.get(s_name, 0)
        # Add dynamic overheads (like your staff/consumable expenses)
        total_cost = labor + 100 + 3000 # Example fixed overheads
        
        summary_data.append({
            "Style": s_name,
            "Challan": s_row['Challan'],
            "Labor Cost (₹)": round(labor, 2),
            "Total Cost (Inc. Overheads)": round(total_cost, 2),
            "Cost Per Pc": round(total_cost / s_row['Issued Qty'], 2) if s_row['Issued Qty'] > 0 else 0
        })
    
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    
    # Visual Chart
    fig = px.bar(pd.DataFrame(summary_data), x="Style", y="Total Cost (Inc. Overheads)", title="Budget Consumption by Style")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: HOURLY FLOOR SHEET (The Matrix) ---
with tab2:
    st.header("Daily Production Matrix")
    st.caption("Assign Styles to workers for each hour slot below.")
    
    style_options = st.session_state['styles']['Style'].tolist()
    
    # Column configuration (Fixes your SelectColumn Error)
    grid_config = {"Worker Name": st.column_config.TextColumn("Worker", disabled=True)}
    for col in [c for c in st.session_state['grid'].columns if " to " in c]:
        grid_config[col] = st.column_config.SelectColumn(col, options=style_options, width="small")

    edited_grid = st.data_editor(
        st.session_state['grid'],
        column_config=grid_config,
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
        ew = st.data_editor(st.session_state['workers'], num_rows="dynamic")
        if st.button("Save Workers"):
            st.session_state['workers'] = ew
            ew.to_csv(FILES["workers"], index=False)
            
    with c2:
        st.subheader("Style/Challan Details")
        es = st.data_editor(st.session_state['styles'], num_rows="dynamic")
        if st.button("Save Styles"):
            st.session_state['styles'] = es
            es.to_csv(FILES["styles"], index=False)
