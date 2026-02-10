import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Ultra Max Factory Manager", layout="wide")

# --- FILE STORAGE ---
WORKER_FILE = "db_workers.csv"
STYLE_FILE = "db_styles.csv"
GRID_FILE = "db_production_grid.csv"

# --- HELPER FUNCTIONS ---
def load_csv(file, default_data):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(default_data)

# --- 1. INITIALIZE DATA ---
# Workers: Name and Daily Wage (from your screenshot)
if 'workers_df' not in st.session_state:
    default_workers = {
        "Worker Name": ["Nazim", "Rahul", "Tanu", "Raju", "Rita"] + [f"Worker {i}" for i in range(6, 21)],
        "Daily Wage": [500, 400, 600, 200, 300] + [350] * 15
    }
    st.session_state['workers_df'] = load_csv(WORKER_FILE, default_workers)

# Styles: Name, Challan, and Issue Qty (from your screenshot)
if 'styles_df' not in st.session_state:
    default_styles = {
        "Style Name": ["1006YKBLUE", "1005YKBLACK", "1888WINE"],
        "Challan": ["10003", "10004", "10005"],
        "Issue Qty": [200, 150, 300]
    }
    st.session_state['styles_df'] = load_csv(STYLE_FILE, default_styles)

# Production Grid: Rows = Workers, Cols = Time Slots
time_slots = ["9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18"]

if 'grid_df' not in st.session_state:
    # Create the grid based on current workers
    current_workers = st.session_state['workers_df']['Worker Name'].tolist()
    
    # Load existing grid or create new
    if os.path.exists(GRID_FILE):
        saved_grid = pd.read_csv(GRID_FILE)
        # Ensure rows match current worker list (logic to merge if needed)
        st.session_state['grid_df'] = saved_grid
    else:
        # Create blank grid
        blank_data = {"Worker Name": current_workers}
        for slot in time_slots:
            blank_data[slot] = None # Empty initially
        st.session_state['grid_df'] = pd.DataFrame(blank_data)

# --- TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["⚙️ Setup (Workers/Styles)", "🏭 Floor Sheet (Excel Grid)", "💰 Costing & Challan"])

# --- TAB 1: SETUP ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Worker Master List")
        edited_workers = st.data_editor(st.session_state['workers_df'], num_rows="dynamic", use_container_width=True)
        if st.button("💾 Save Workers"):
            edited_workers.to_csv(WORKER_FILE, index=False)
            st.session_state['workers_df'] = edited_workers
            st.rerun()

    with col2:
        st.subheader("Style & Challan Master")
        edited_styles = st.data_editor(st.session_state['styles_df'], num_rows="dynamic", use_container_width=True)
        if st.button("💾 Save Styles"):
            edited_styles.to_csv(STYLE_FILE, index=False)
            st.session_state['styles_df'] = edited_styles
            st.rerun()

# --- TAB 2: FLOOR SHEET (THE GRID) ---
with tab2:
    st.header("Daily Production Grid")
    st.info("Select the **Style** for each hour. The app will calculate the cost automatically based on the worker's wage.")

    # Prepare Dropdown Options
    style_list = st.session_state['styles_df']['Style Name'].tolist()
    
    # Configure Columns
    col_config = {
        "Worker Name": st.column_config.TextColumn("Worker", disabled=True)
    }
    for slot in time_slots:
        col_config[slot] = st.column_config.SelectColumn(
            label=f"{slot} (Style)",
            options=style_list,
            required=False
        )

    # Show Editable Grid
    edited_grid = st.data_editor(
        st.session_state['grid_df'],
        column_config=col_config,
        use_container_width=True,
        height=600
    )

    if st.button("✅ Update Floor Sheet"):
        edited_grid.to_csv(GRID_FILE, index=False)
        st.session_state['grid_df'] = edited_grid
        st.success("Floor Data Updated!")

# --- TAB 3: COSTING & REPORT ---
with tab3:
    st.header("Challan & Costing Summary")

    # --- THE CALCULATION ENGINE ---
    # 1. Merge Workers with Grid to get Wages
    grid = st.session_state['grid_df']
    workers = st.session_state['workers_df']
    styles = st.session_state['styles_df']

    # Create a cost summary dictionary
    cost_summary = {style: 0 for style in styles['Style Name']}
    
    # Iterate through the grid to calculate costs
    # Logic: If Nazim (Wage 500) works 1 hour on Style A, Cost = 500 / 8 = 62.5
    for index, row in grid.iterrows():
        worker_name = row['Worker Name']
        # Find worker wage
        worker_wage = workers.loc[workers['Worker Name'] == worker_name, 'Daily Wage'].values
        if len(worker_wage) > 0:
            hourly_rate = worker_wage[0] / 8  # Assuming 8 hour shift
            
            # Check each hour slot
            for slot in time_slots:
                assigned_style = row[slot]
                if assigned_style and assigned_style in cost_summary:
                    cost_summary[assigned_style] += hourly_rate

    # --- DISPLAY REPORT ---
    # Allow user to select a style to view detailed costing (like your Image 3)
    selected_style = st.selectbox("Select Style to View Costing", styles['Style Name'])
    
    if selected_style:
        style_data = styles[styles['Style Name'] == selected_style].iloc[0]
        calculated_labor_cost = cost_summary[selected_style]
        
        st.divider()
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader(f"Challan: {style_data['Challan']}")
            st.metric("Issued Qty", style_data['Issue Qty'])
            
            # Inputs for extra costs (from your Image 3)
            consumable = st.number_input("Consumable Expenses", value=100)
            staff_exp = st.number_input("Staff Expenses", value=3000)
            received_qty = st.number_input("Received Qty", value=100)
            
            st.write(f"**Remaining Qty:** {style_data['Issue Qty'] - received_qty}")

        with c2:
            st.subheader("Cost Breakdown")
            
            # Creating the Dataframe exactly like your Excel Image 3
            cost_df = pd.DataFrame([
                {"Category": "Employee Expenses (Calculated)", "Amount": round(calculated_labor_cost, 2)},
                {"Category": "Referment/Other", "Amount": 50}, # Placeholder
                {"Category": "Consumables", "Amount": consumable},
                {"Category": "Staff Expense", "Amount": staff_exp},
                {"Category": "TOTAL COST", "Amount": round(calculated_labor_cost + 50 + consumable + staff_exp, 2)}
            ])
            
            st.table(cost_df)
            
            if received_qty > 0:
                per_pc_cost = (calculated_labor_cost + 50 + consumable + staff_exp) / received_qty
                st.success(f"💰 Final Cost Per Piece: ₹{per_pc_cost:.2f}")
