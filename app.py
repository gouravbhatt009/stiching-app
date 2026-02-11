import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO

# ------------------------------------------------------------
# 1. CONSTANTS & CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(page_title="ProFactory ERP v2", layout="wide")

FILES = {
    "workers": "workers.csv",
    "styles": "styles.csv",
    "grid": "floor_sheet.csv",
    "stitching_master": "stitching_master.csv"
}

TIME_SLOTS = [f"{h} to {h+1}" for h in range(9, 18)]
DEFAULT_OVERHEAD = 3150  # used in executive summary

# ------------------------------------------------------------
# 2. HELPER FUNCTIONS (Data IO, calculations)
# ------------------------------------------------------------
def load_dataframe(file_key, required_columns, default_data=None):
    """Load CSV if exists; else return empty DataFrame with required columns."""
    if os.path.exists(FILES[file_key]):
        df = pd.read_csv(FILES[file_key])
        # ensure all columns exist
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        return df
    else:
        if default_data is None:
            return pd.DataFrame(columns=required_columns)
        return pd.DataFrame(default_data, columns=required_columns)

def save_dataframe(df, file_key):
    """Save DataFrame to CSV."""
    df.to_csv(FILES[file_key], index=False)

def compute_actual_costs(grid, workers_df):
    """Return DataFrame with Style and Actual Labor Cost from floor sheet."""
    wage_map = dict(zip(workers_df["Name"], workers_df["Daily Wage"]))
    time_cols = [c for c in grid.columns if " to " in c]
    cost_per_style = {}
    
    for _, row in grid.iterrows():
        worker = row["Worker Name"]
        if pd.isna(worker) or worker not in wage_map:
            continue
        hourly_rate = wage_map[worker] / 8  # ₹ per hour
        for col in time_cols:
            style = row[col]
            if pd.notna(style):
                cost_per_style[style] = cost_per_style.get(style, 0) + hourly_rate
                
    return pd.DataFrame(list(cost_per_style.items()), columns=["Style", "Actual_Labor_Cost"])

def rebuild_grid_from_workers(workers_df, old_grid):
    """Create a new grid with current workers, preserving existing assignments where possible."""
    new_grid = pd.DataFrame({"Worker Name": workers_df["Name"]})
    for slot in TIME_SLOTS:
        new_grid[slot] = None
    
    if old_grid is not None and not old_grid.empty:
        for idx, row in new_grid.iterrows():
            worker = row["Worker Name"]
            if worker in old_grid["Worker Name"].values:
                old_row = old_grid[old_grid["Worker Name"] == worker].iloc[0]
                for slot in TIME_SLOTS:
                    new_grid.at[idx, slot] = old_row[slot]
    return new_grid

# ------------------------------------------------------------
# 3. INITIALISE SESSION STATE (runs only once)
# ------------------------------------------------------------
if 'initialised' not in st.session_state:
    # ----- Workers -----
    st.session_state.workers = load_dataframe(
        "workers",
        ["Name", "Daily Wage"],
        [["Nazim", 500]]
    )
    
    # ----- Styles -----
    st.session_state.styles = load_dataframe(
        "styles",
        ["Style", "Challan", "Issued Qty"],
        [["1006YKBLUE", "10003", 200]]
    )
    
    # ----- Floor Grid -----
    default_grid = pd.DataFrame({"Worker Name": st.session_state.workers["Name"]})
    for slot in TIME_SLOTS:
        default_grid[slot] = None
    st.session_state.grid = load_dataframe(
        "grid",
        default_grid.columns.tolist(),
        default_grid.values
    )
    
    # ----- Stitching Master Cost -----
    # Default master: one row per existing style
    master_default_data = []
    for style in st.session_state.styles["Style"].tolist():
        master_default_data.append([style, 20.0, 1.25, 15, 0.0])  # SMV, rate/min, overhead%, std cost (calc later)
    master_default_df = pd.DataFrame(
        master_default_data,
        columns=["Style", "SMV", "Labor_Rate_per_min", "Overhead_%", "Std_Stitching_Cost"]
    )
    master_default_df["Std_Stitching_Cost"] = (
        master_default_df["SMV"] * 
        master_default_df["Labor_Rate_per_min"] * 
        (1 + master_default_df["Overhead_%"] / 100)
    ).round(2)
    
    st.session_state.stitching_master = load_dataframe(
        "stitching_master",
        ["Style", "SMV", "Labor_Rate_per_min", "Overhead_%", "Std_Stitching_Cost"],
        master_default_df.values
    )
    
    st.session_state.initialised = True

# ------------------------------------------------------------
# 4. UI TABS
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Analysis",
    "🕒 Live Floor Sheet",
    "⚙️ Setup & Data Bridge",
    "🧵 Stitching Costing"
])

# ---------- TAB 1 : EXECUTIVE ANALYSIS (unchanged, but uses DEFAULT_OVERHEAD) ----------
with tab1:
    st.title("💰 Production & Costing Summary")
    
    workers = st.session_state.workers
    grid = st.session_state.grid
    wage_map = dict(zip(workers['Name'], workers['Daily Wage']))
    
    style_costs = {s: 0 for s in st.session_state.styles['Style'].tolist()}
    time_cols = [c for c in grid.columns if " to " in c]

    for _, row in grid.iterrows():
        hourly_rate = wage_map.get(row['Worker Name'], 0) / 8
        for col in time_cols:
            if pd.notna(row[col]) and row[col] in style_costs:
                style_costs[row[col]] += hourly_rate

    summary_df = pd.DataFrame([
        {"Style": k, "Labor Cost": round(v, 2), "Total with Overheads": round(v + DEFAULT_OVERHEAD, 2)} 
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

# ---------- TAB 2 : LIVE FLOOR SHEET ----------
with tab2:
    st.header("Daily Matrix")
    st.caption("Edit the worker assignments for each time slot directly below:")

    edited_grid = st.data_editor(
        st.session_state.grid,
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("💾 Save Matrix"):
        st.session_state.grid = edited_grid
        save_dataframe(edited_grid, "grid")
        st.success("Matrix saved successfully!")

# ---------- TAB 3 : SETUP & DATA BRIDGE ----------
with tab3:
    st.title("🛠️ System Administration")
    
    # ----- Data Bridge (Upload) -----
    st.subheader("📥 Data Bridge (Upload Excel/CSV)")
    st.markdown("Upload Excel/CSV files to bulk-update your Worker or Style lists.")
    
    up_col1, up_col2 = st.columns(2)
    
    with up_col1:
        uploaded_workers = st.file_uploader("Upload Worker List (Excel/CSV)", type=['csv', 'xlsx'])
        if uploaded_workers:
            df_up = pd.read_excel(uploaded_workers, engine='openpyxl') if uploaded_workers.name.endswith('.xlsx') else pd.read_csv(uploaded_workers)
            if st.button("Confirm Worker Import"):
                st.session_state.workers = df_up
                save_dataframe(df_up, "workers")
                st.success(f"Imported {len(df_up)} workers!")

    with up_col2:
        uploaded_styles = st.file_uploader("Upload Style Master (Excel/CSV)", type=['csv', 'xlsx'])
        if uploaded_styles:
            df_up_s = pd.read_excel(uploaded_styles, engine='openpyxl') if uploaded_styles.name.endswith('.xlsx') else pd.read_csv(uploaded_styles)
            if st.button("Confirm Style Import"):
                st.session_state.styles = df_up_s
                save_dataframe(df_up_s, "styles")
                st.success("Styles updated!")
    
    st.divider()
    
    # ----- Manual Editors with Save Buttons -----
    st.subheader("✏️ Manual Worker Editor")
    edited_workers = st.data_editor(
        st.session_state.workers,
        num_rows="dynamic",
        key="manual_worker_editor"
    )
    if st.button("💾 Save Workers", key="save_workers_btn"):
        st.session_state.workers = edited_workers
        save_dataframe(edited_workers, "workers")
        st.success("Workers saved!")
    
    st.subheader("✏️ Manual Style Editor")
    edited_styles = st.data_editor(
        st.session_state.styles,
        num_rows="dynamic",
        key="manual_style_editor"
    )
    if st.button("💾 Save Styles", key="save_styles_btn"):
        st.session_state.styles = edited_styles
        save_dataframe(edited_styles, "styles")
        st.success("Styles saved!")
    
    st.divider()
    
    # ----- Rebuild Grid from Workers -----
    st.subheader("🔄 Rebuild Floor Grid")
    st.warning("If you added/removed workers, rebuild the floor sheet grid to match the current worker list. Existing assignments for remaining workers will be preserved.")
    if st.button("🔄 Rebuild Grid Now"):
        new_grid = rebuild_grid_from_workers(st.session_state.workers, st.session_state.grid)
        st.session_state.grid = new_grid
        save_dataframe(new_grid, "grid")
        st.success("Floor grid rebuilt!")
    
    # ----- Sync Stitching Master with Styles -----
    st.subheader("🔄 Sync Stitching Master")
    st.info("Add any new Styles to the Stitching Cost master with default values.")
    if st.button("➕ Sync Styles to Stitching Master"):
        master = st.session_state.stitching_master
        existing_styles = set(master["Style"])
        all_styles = set(st.session_state.styles["Style"])
        new_styles = all_styles - existing_styles
        
        if new_styles:
            new_rows = []
            for style in new_styles:
                new_rows.append([style, 20.0, 1.25, 15, 20.0 * 1.25 * 1.15])  # default SMV=20, rate=1.25, overhead=15%
            new_df = pd.DataFrame(new_rows, columns=master.columns)
            master = pd.concat([master, new_df], ignore_index=True)
            st.session_state.stitching_master = master
            save_dataframe(master, "stitching_master")
            st.success(f"Added {len(new_styles)} new style(s) to Stitching Master.")
        else:
            st.info("All styles already present in Stitching Master.")

# ---------- TAB 4 : STITCHING COSTING (NEW) ----------
with tab4:
    st.title("🧵 Stitching Costing – Standard vs Actual")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Master Cost Settings")
        st.caption("Edit standard values per SKU (changes auto-calculate Std Cost).")
        
        # Editable master table
        edited_master = st.data_editor(
            st.session_state.stitching_master,
            column_config={
                "Style": st.column_config.TextColumn("Style", disabled=True),
                "SMV": st.column_config.NumberColumn("SMV (min)", min_value=0.0, step=0.1),
                "Labor_Rate_per_min": st.column_config.NumberColumn("Rate (₹/min)", min_value=0.0, format="₹%.2f"),
                "Overhead_%": st.column_config.NumberColumn("Overhead %", min_value=0.0, max_value=100.0, step=1),
                "Std_Stitching_Cost": st.column_config.NumberColumn("Std Cost (₹)", disabled=True, format="₹%.2f")
            },
            use_container_width=True,
            num_rows="dynamic",
            key="master_editor"
        )
        
        # Auto‑calculate standard cost
        edited_master["Std_Stitching_Cost"] = (
            edited_master["SMV"] * 
            edited_master["Labor_Rate_per_min"] * 
            (1 + edited_master["Overhead_%"] / 100)
        ).round(2)
        
        if st.button("💾 Save Master Costs", use_container_width=True):
            st.session_state.stitching_master = edited_master
            save_dataframe(edited_master, "stitching_master")
            st.success("Master costing saved!")
    
    with col2:
        st.subheader("📊 Actual vs Standard Analysis")
        
        # Compute actual costs from current floor grid
        actual_df = compute_actual_costs(st.session_state.grid, st.session_state.workers)
        
        # Merge with master
        merged = edited_master.merge(actual_df, on="Style", how="left").fillna(0)
        merged["Actual_Labor_Cost"] = merged["Actual_Labor_Cost"].round(2)
        merged["Variance (₹)"] = merged["Actual_Labor_Cost"] - merged["Std_Stitching_Cost"]
        merged["Variance (%)"] = (merged["Variance (₹)"] / merged["Std_Stitching_Cost"] * 100).round(1)
        merged["Variance (%)"] = merged["Variance (%)"].fillna(0).replace([float('inf'), -float('inf')], 0)
        
        # Summary metrics
        total_std = merged["Std_Stitching_Cost"].sum()
        total_actual = merged["Actual_Labor_Cost"].sum()
        total_var = total_actual - total_std
        var_percent = (total_var / total_std * 100) if total_std != 0 else 0
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Total Std Cost", f"₹{total_std:,.0f}")
        mcol2.metric("Total Actual Cost", f"₹{total_actual:,.0f}")
        mcol3.metric("Variance", f"₹{total_var:,.0f}", delta=f"{var_percent:.1f}%")
        mcol4.metric("Overhead (avg)", f"{edited_master['Overhead_%'].mean():.0f}%")
        
        # Bar chart
        fig = px.bar(
            merged,
            x="Style",
            y=["Std_Stitching_Cost", "Actual_Labor_Cost"],
            barmode="group",
            title="Standard vs Actual Stitching Cost per Style",
            labels={"value": "Cost (₹)", "variable": "Cost Type"},
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Variance table
        st.subheader("📋 Variance Details")
        st.dataframe(
            merged[["Style", "Std_Stitching_Cost", "Actual_Labor_Cost", "Variance (₹)", "Variance (%)"]],
            use_container_width=True,
            column_config={
                "Std_Stitching_Cost": st.column_config.NumberColumn(format="₹%.2f"),
                "Actual_Labor_Cost": st.column_config.NumberColumn(format="₹%.2f"),
                "Variance (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Variance (%)": st.column_config.NumberColumn(format="%.1f%%"),
            }
        )
        
        # Export variance report
        st.subheader("📤 Export Variance Report")
        buffer_var = BytesIO()
        with pd.ExcelWriter(buffer_var, engine='openpyxl') as writer:
            merged.to_excel(writer, index=False, sheet_name='Stitching_Variance')
        st.download_button(
            label="📥 Download Variance as Excel",
            data=buffer_var.getvalue(),
            file_name="Stitching_Variance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
