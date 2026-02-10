import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="ProFactory ERP System", layout="wide", page_icon="🏭")

# --- FILE CONSTANTS ---
FILES = {
    "workers": "db_workers.csv",
    "styles": "db_styles.csv",
    "grid": "db_floor_sheet.csv",
    "config": "db_config.csv"
}

# --- HELPER: LOAD/SAVE DATA ---
def load_data(key, default_data):
    if os.path.exists(FILES[key]):
        return pd.read_csv(FILES[key])
    return pd.DataFrame(default_data)

def save_data(key, df):
    df.to_csv(FILES[key], index=False)
    st.toast(f"✅ {key.capitalize()} Saved Successfully!", icon="💾")

# --- INITIALIZATION (SESSION STATE) ---
if 'init' not in st.session_state:
    # 1. Workers Data (Name, Daily Wage, Role)
    st.session_state['workers'] = load_data("workers", {
        "Worker ID": ["W001", "W002", "W003", "W004", "W005"],
        "Name": ["Nazim", "Rahul", "Tanu", "Raju", "Rita"],
        "Daily Wage": [500, 400, 600, 200, 300],
        "Role": ["Stitcher", "Helper", "Master", "Helper", "Stitcher"]
    })

    # 2. Styles Data (Budgeting)
    st.session_state['styles'] = load_data("styles", {
        "Style Code": ["1006YKBLUE", "1005YKBLACK", "1888WINE"],
        "Challan No": ["10003", "10004", "10005"],
        "Order Qty": [200, 150, 300],
        "Target Cost/Pc": [150.0, 120.0, 180.0] # Budget per piece
    })

    # 3. Floor Sheet (The Grid)
    time_slots = [f"{h:02d}:00-{h+1:02d}:00" for h in range(9, 18)] # 09:00-10:00...
    
    # Load grid or create blank based on active workers
    if os.path.exists(FILES["grid"]):
        st.session_state['grid'] = pd.read_csv(FILES["grid"])
    else:
        # Initialize blank grid
        df_grid = st.DataFrame({"Worker Name": st.session_state['workers']['Name']})
        for slot in time_slots:
            df_grid[slot] = None
        st.session_state['grid'] = df_grid

    # 4. Global Settings (Overheads)
    st.session_state['config'] = load_data("config", {
        "Setting": ["Overhead % (Rent/Elec)", "Work Hours/Day"],
        "Value": [15.0, 9.0] # 15% extra cost, 9 hour shift
    })
    
    st.session_state['init'] = True

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏭 ProFactory ERP")
menu = st.sidebar.radio("Navigate", ["📊 Executive Dashboard", "🗓️ Floor Sheet (Production)", "⚙️ Master Setup"])

# --- PAGE 1: EXECUTIVE DASHBOARD (THE PROMOTION MAKER) ---
if menu == "📊 Executive Dashboard":
    st.title("💰 Costing & Profitability Center")
    st.markdown("Real-time analysis of production costs vs. budget.")

    # --- CALCULATION ENGINE ---
    grid = st.session_state['grid']
    workers = st.session_state['workers']
    styles = st.session_state['styles']
    config = st.session_state['config']
    
    overhead_pct = float(config.loc[config['Setting']=="Overhead % (Rent/Elec)", "Value"].values[0])
    work_hours = float(config.loc[config['Setting']=="Work Hours/Day", "Value"].values[0])

    # 1. Calculate Cost Per Style
    style_costs = {code: 0.0 for code in styles['Style Code']}
    
    time_cols = [c for c in grid.columns if "-" in c] # Get time columns
    
    for _, row in grid.iterrows():
        worker_name = row['Worker Name']
        # Find worker wage
        w_row = workers[workers['Name'] == worker_name]
        if not w_row.empty:
            hourly_rate = w_row['Daily Wage'].values[0] / work_hours
            
            for col in time_cols:
                assigned_style = row[col]
                if assigned_style and assigned_style in style_costs:
                    style_costs[assigned_style] += hourly_rate

    # 2. Build Report Dataframe
    report_data = []
    for _, s_row in styles.iterrows():
        code = s_row['Style Code']
        direct_labor = style_costs.get(code, 0)
        overhead_cost = direct_labor * (overhead_pct / 100)
        total_spent = direct_labor + overhead_cost
        
        target_budget = s_row['Target Cost/Pc'] * s_row['Order Qty']
        
        # Avoid division by zero
        actual_cost_pc = total_spent / s_row['Order Qty'] if s_row['Order Qty'] > 0 else 0
        
        status = "🟢 Profitable" if total_spent <= target_budget else "🔴 Over Budget"
        
        report_data.append({
            "Style": code,
            "Challan": s_row['Challan No'],
            "Total Labor": round(direct_labor, 2),
            "Overheads": round(overhead_cost, 2),
            "Total Actual Cost": round(total_spent, 2),
            "Budget Limit": round(target_budget, 2),
            "Variance": round(target_budget - total_spent, 2),
            "Actual Cost/Pc": round(actual_cost_pc, 2),
            "Status": status
        })
    
    df_report = pd.DataFrame(report_data)

    # --- DISPLAY METRICS ---
    total_spend = df_report['Total Actual Cost'].sum()
    total_budget = df_report['Budget Limit'].sum()
    net_profit = total_budget - total_spend
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Production Cost", f"₹{total_spend:,.0f}")
    m2.metric("Total Budget Value", f"₹{total_budget:,.0f}")
    m3.metric("Net Variance", f"₹{net_profit:,.0f}", delta=round(net_profit), delta_color="normal")
    m4.metric("Active Styles", len(df_report))
    
    st.divider()

    # --- DETAILED TABLE WITH HIGHLIGHTS ---
    st.subheader("Style-wise Profitability")
    
    # Color code the table
    def highlight_status(val):
        color = '#ffcdd2' if val == "🔴 Over Budget" else '#c8e6c9'
        return f'background-color: {color}'

    st.dataframe(
        df_report.style.applymap(highlight_status, subset=['Status']),
        use_container_width=True
    )

    # --- CHARTS ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cost Breakdown")
        fig_bar = px.bar(df_report, x="Style", y=["Total Labor", "Overheads"], title="Labor vs Overhead Cost")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        st.subheader("Budget vs Actual")
        fig_dual = px.bar(df_report, x="Style", y=["Total Actual Cost", "Budget Limit"], barmode="group", title="Are we within budget?")
        st.plotly_chart(fig_dual, use_container_width=True)

# --- PAGE 2: FLOOR SHEET (PRODUCTION) ---
elif menu == "🗓️ Floor Sheet (Production)":
    st.title("🏭 Daily Production Log")
    st.info("Assign styles to workers for each hour. Calculations are automatic.")

    # Dropdown Options
    style_opts = st.session_state['styles']['Style Code'].tolist()
    
    # Configure Grid
    time_cols = [f"{h:02d}:00-{h+1:02d}:00" for h in range(9, 18)]
    
    col_config = {
        "Worker Name": st.column_config.TextColumn("Employee", disabled=True)
    }
    # Dynamic columns for time slots
    for slot in time_cols:
        col_config[slot] = st.column_config.SelectColumn(
            slot,
            options=style_opts,
            required=False,
            width="small"
        )

    # The Editor
    edited_grid = st.data_editor(
        st.session_state['grid'],
        column_config=col_config,
        use_container_width=True,
        height=600,
        num_rows="dynamic"
    )

    if st.button("💾 Save Production Sheet", type="primary"):
        st.session_state['grid'] = edited_grid
        save_data("grid", edited_grid)


# --- PAGE 3: MASTER SETUP ---
elif menu == "⚙️ Master Setup":
    st.title("⚙️ System Configuration")
    
    t1, t2, t3 = st.tabs(["👥 Workers", "👕 Styles & Budget", "🔧 General Settings"])
    
    with t1:
        st.caption("Manage your employee list and daily wages.")
        edited_workers = st.data_editor(st.session_state['workers'], num_rows="dynamic", use_container_width=True)
        if st.button("Save Workers"):
            st.session_state['workers'] = edited_workers
            save_data("workers", edited_workers)
            
    with t2:
        st.caption("Define your styles and the TARGET cost per piece (Budget).")
        edited_styles = st.data_editor(st.session_state['styles'], num_rows="dynamic", use_container_width=True)
        if st.button("Save Styles"):
            st.session_state['styles'] = edited_styles
            save_data("styles", edited_styles)
            
    with t3:
        st.caption("Adjust factory overheads.")
        edited_config = st.data_editor(st.session_state['config'], use_container_width=True)
        if st.button("Save Config"):
            st.session_state['config'] = edited_config
            save_data("config", edited_config)
