"""
Stitching Costing Interface - Streamlit App
Textile Garments Company - Karigar Time Tracking & Costing System
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import json
import io

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stitching Costing Interface",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2rem; letter-spacing: 1px; }
    .main-header p { margin: 5px 0 0; opacity: 0.75; font-size: 0.95rem; }

    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 18px 20px;
        border-left: 5px solid #0f3460;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }
    .metric-card .label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    .metric-card .sub { font-size: 0.85rem; color: #0f3460; }

    .efficiency-high { color: #28a745 !important; }
    .efficiency-mid  { color: #ffc107 !important; }
    .efficiency-low  { color: #dc3545 !important; }

    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f3460;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }
    .info-box {
        background: #f0f4ff;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #c5d5ff;
        font-size: 0.9rem;
        color: #2c3e6e;
        margin-bottom: 12px;
    }
    div[data-testid="stTabs"] button { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────
def init_state():
    # ── Master Style Operations ──────────────────────────
    if "style_master" not in st.session_state:
        st.session_state.style_master = pd.DataFrame([
            {"Style": "1065YKBLUE", "Operation": "Cutting",        "Target": 120, "Rate_Rs": 2.50},
            {"Style": "1065YKBLUE", "Operation": "Stitching Front","Target": 80,  "Rate_Rs": 4.00},
            {"Style": "1065YKBLUE", "Operation": "Stitching Back", "Target": 80,  "Rate_Rs": 4.00},
            {"Style": "1065YKBLUE", "Operation": "Collar Attach",  "Target": 60,  "Rate_Rs": 5.50},
            {"Style": "1065YKBLUE", "Operation": "Sleeve Attach",  "Target": 60,  "Rate_Rs": 5.50},
            {"Style": "1065YKBLUE", "Operation": "Side Seam",      "Target": 90,  "Rate_Rs": 3.50},
            {"Style": "1065YKBLUE", "Operation": "Hemming",        "Target": 100, "Rate_Rs": 3.00},
            {"Style": "1065YKBLUE", "Operation": "Button Hole",    "Target": 110, "Rate_Rs": 2.00},
            {"Style": "1065YKBLUE", "Operation": "Button Attach",  "Target": 110, "Rate_Rs": 2.00},
            {"Style": "1065YKBLUE", "Operation": "Finishing",      "Target": 70,  "Rate_Rs": 4.50},
        ])

    # ── Karigar Master ────────────────────────────────────
    if "karigar_master" not in st.session_state:
        st.session_state.karigar_master = pd.DataFrame([
            {"Karigar_ID": "K001", "Name": "Ramesh Kumar",  "Skill": "Stitching", "Daily_Rate_Rs": 450},
            {"Karigar_ID": "K002", "Name": "Suresh Singh",  "Skill": "Cutting",   "Daily_Rate_Rs": 420},
            {"Karigar_ID": "K003", "Name": "Priya Devi",    "Skill": "Finishing",  "Daily_Rate_Rs": 400},
            {"Karigar_ID": "K004", "Name": "Mohan Lal",     "Skill": "Stitching", "Daily_Rate_Rs": 460},
            {"Karigar_ID": "K005", "Name": "Sunita Sharma", "Skill": "Hemming",   "Daily_Rate_Rs": 410},
        ])

    # ── Challan Master ────────────────────────────────────
    if "challan_master" not in st.session_state:
        st.session_state.challan_master = pd.DataFrame([
            {"Challan_No": "CH-001", "Style": "1065YKBLUE", "SKU": "YK-BLU-M",  "Qty": 200, "Date": "2025-01-15"},
            {"Challan_No": "CH-002", "Style": "1065YKBLUE", "SKU": "YK-BLU-L",  "Qty": 150, "Date": "2025-01-16"},
            {"Challan_No": "CH-003", "Style": "1065YKBLUE", "SKU": "YK-BLU-XL", "Qty": 100, "Date": "2025-01-17"},
        ])

    # ── Karigar Time Log (Hour-wise) ───────────────────────
    if "time_log" not in st.session_state:
        st.session_state.time_log = pd.DataFrame(columns=[
            "Date", "Karigar_ID", "Karigar_Name", "Hour_Slot",
            "Style", "Challan_No", "Operation", "Pieces_Done"
        ])

    # ── Karigar Daily Sheet (Operation-wise) ──────────────
    if "daily_sheet" not in st.session_state:
        st.session_state.daily_sheet = pd.DataFrame(columns=[
            "Date", "Karigar_ID", "Karigar_Name",
            "Style", "Challan_No", "Operation",
            "Target", "Achieved", "Rate_Rs"
        ])

init_state()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧵 Stitching Costing Interface</h1>
    <p>Karigar Time Tracking · Challan-wise Costing · Efficiency Analysis · Payroll</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Dashboard",
    "⏱️ Hour-wise Time Log",
    "📋 Karigar Daily Sheet",
    "🧾 Challan Management",
    "📊 Efficiency & Costing",
    "💰 Payroll Calculator",
    "⚙️ Master Data",
])

tab_dash, tab_timelog, tab_daily, tab_challan, tab_efficiency, tab_payroll, tab_master = tabs

# ════════════════════════════════════════════════════════════
# TAB 1 – DASHBOARD
# ════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown('<div class="section-title">📈 Today\'s Overview</div>', unsafe_allow_html=True)

    today_str = str(date.today())
    today_log  = st.session_state.time_log[st.session_state.time_log["Date"] == today_str]
    today_daily = st.session_state.daily_sheet[st.session_state.daily_sheet["Date"] == today_str]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        active_karigar = today_log["Karigar_ID"].nunique() if not today_log.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Active Karigar Today</div>
            <div class="value">{active_karigar}</div>
            <div class="sub">of {len(st.session_state.karigar_master)} total</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        total_pieces = int(today_log["Pieces_Done"].sum()) if not today_log.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Pieces Done Today</div>
            <div class="value">{total_pieces}</div>
            <div class="sub">across all operations</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        if not today_daily.empty and "Target" in today_daily.columns and "Achieved" in today_daily.columns:
            avg_eff = (today_daily["Achieved"] / today_daily["Target"] * 100).mean()
            eff_class = "efficiency-high" if avg_eff >= 90 else ("efficiency-mid" if avg_eff >= 70 else "efficiency-low")
        else:
            avg_eff = 0
            eff_class = "efficiency-low"
        st.markdown(f"""<div class="metric-card">
            <div class="label">Avg Efficiency</div>
            <div class="value {eff_class}">{avg_eff:.1f}%</div>
            <div class="sub">Target: 100%</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        if not today_daily.empty and "Achieved" in today_daily.columns and "Rate_Rs" in today_daily.columns:
            total_cost = (today_daily["Achieved"] * today_daily["Rate_Rs"]).sum()
        else:
            total_cost = 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Today's Labour Cost</div>
            <div class="value">₹{total_cost:,.0f}</div>
            <div class="sub">piece-rate earned</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">👷 Karigar Status</div>', unsafe_allow_html=True)
        km = st.session_state.karigar_master.copy()
        if not today_log.empty:
            active_ids = today_log["Karigar_ID"].unique().tolist()
            km["Status"] = km["Karigar_ID"].apply(lambda x: "🟢 Working" if x in active_ids else "⚪ Idle")
        else:
            km["Status"] = "⚪ Idle"
        st.dataframe(km[["Karigar_ID","Name","Skill","Status"]], use_container_width=True, hide_index=True)

    with col_b:
        st.markdown('<div class="section-title">🧾 Active Challans</div>', unsafe_allow_html=True)
        st.dataframe(
            st.session_state.challan_master[["Challan_No","Style","SKU","Qty","Date"]],
            use_container_width=True, hide_index=True
        )

    if not today_daily.empty:
        st.markdown("---")
        st.markdown('<div class="section-title">📋 Today\'s Daily Sheet Summary</div>', unsafe_allow_html=True)
        summary = today_daily.copy()
        if "Achieved" in summary.columns and "Target" in summary.columns:
            summary["Efficiency_%"] = (summary["Achieved"] / summary["Target"] * 100).round(1)
            summary["Earned_Rs"] = (summary["Achieved"] * summary["Rate_Rs"]).round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
# TAB 2 – HOUR-WISE TIME LOG
# ════════════════════════════════════════════════════════════
with tab_timelog:
    st.markdown('<div class="section-title">⏱️ Karigar Hour-wise Time Entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Log which karigar worked on which style/challan for each hour of the 11-hour shift (8 AM – 7 PM).</div>', unsafe_allow_html=True)

    hour_slots = [f"{h:02d}:00–{h+1:02d}:00" for h in range(8, 19)]
    styles_list  = st.session_state.style_master["Style"].unique().tolist()
    challan_list = st.session_state.challan_master["Challan_No"].tolist()
    karigar_options = {
        f"{row['Karigar_ID']} – {row['Name']}": row['Karigar_ID']
        for _, row in st.session_state.karigar_master.iterrows()
    }

    with st.form("time_log_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            tl_date = st.date_input("Date", value=date.today())
            tl_karigar_label = st.selectbox("Karigar", list(karigar_options.keys()))
            tl_hour = st.selectbox("Hour Slot", hour_slots)
        with col2:
            tl_style = st.selectbox("Style", styles_list)
            tl_challan = st.selectbox("Challan No", challan_list)
        with col3:
            tl_ops_for_style = st.session_state.style_master[
                st.session_state.style_master["Style"] == tl_style
            ]["Operation"].tolist()
            tl_operation = st.selectbox("Operation", tl_ops_for_style)
            tl_pieces = st.number_input("Pieces Done in this Hour", min_value=0, step=1)

        submitted = st.form_submit_button("✅ Save Time Entry", use_container_width=True)
        if submitted:
            karigar_id = karigar_options[tl_karigar_label]
            karigar_name = tl_karigar_label.split("–")[1].strip()
            new_row = {
                "Date": str(tl_date),
                "Karigar_ID": karigar_id,
                "Karigar_Name": karigar_name,
                "Hour_Slot": tl_hour,
                "Style": tl_style,
                "Challan_No": tl_challan,
                "Operation": tl_operation,
                "Pieces_Done": tl_pieces
            }
            st.session_state.time_log = pd.concat(
                [st.session_state.time_log, pd.DataFrame([new_row])], ignore_index=True
            )
            st.success(f"✅ Saved: {karigar_name} | {tl_hour} | {tl_style} | {tl_operation} | {tl_pieces} pcs")

    st.markdown("---")
    st.markdown('<div class="section-title">📄 Time Log Records</div>', unsafe_allow_html=True)

    if not st.session_state.time_log.empty:
        filter_date = st.date_input("Filter by Date", value=date.today(), key="tl_filter")
        filtered = st.session_state.time_log[st.session_state.time_log["Date"] == str(filter_date)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            # Hour-wise pivot
            st.markdown('<div class="section-title">🕐 Hour-wise Karigar Heatmap</div>', unsafe_allow_html=True)
            if "Karigar_Name" in filtered.columns and "Hour_Slot" in filtered.columns:
                pivot = filtered.pivot_table(
                    index="Karigar_Name", columns="Hour_Slot",
                    values="Pieces_Done", aggfunc="sum", fill_value=0
                )
                st.dataframe(pivot.style.background_gradient(cmap="Blues"), use_container_width=True)
        else:
            st.info("No entries for the selected date.")
    else:
        st.info("No time log entries yet. Use the form above to add entries.")


# ════════════════════════════════════════════════════════════
# TAB 3 – KARIGAR DAILY SHEET
# ════════════════════════════════════════════════════════════
with tab_daily:
    st.markdown('<div class="section-title">📋 Karigar Daily Sheet – Operation-wise Entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Enter daily production per karigar per operation. System auto-fetches target & rate from master data.</div>', unsafe_allow_html=True)

    karigar_options2 = {
        f"{row['Karigar_ID']} – {row['Name']}": row['Karigar_ID']
        for _, row in st.session_state.karigar_master.iterrows()
    }
    styles_list2  = st.session_state.style_master["Style"].unique().tolist()
    challan_list2 = st.session_state.challan_master["Challan_No"].tolist()

    with st.form("daily_sheet_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ds_date    = st.date_input("Date", value=date.today(), key="ds_date")
            ds_karigar = st.selectbox("Karigar", list(karigar_options2.keys()), key="ds_karigar")
            ds_style   = st.selectbox("Style", styles_list2, key="ds_style")

        with col2:
            ds_challan = st.selectbox("Challan No", challan_list2, key="ds_challan")
            ds_ops = st.session_state.style_master[
                st.session_state.style_master["Style"] == ds_style
            ][["Operation","Target","Rate_Rs"]]
            ds_operation = st.selectbox("Operation", ds_ops["Operation"].tolist(), key="ds_op")

        # Show target
        op_row = ds_ops[ds_ops["Operation"] == ds_operation]
        target_val = int(op_row["Target"].values[0]) if not op_row.empty else 0
        rate_val   = float(op_row["Rate_Rs"].values[0]) if not op_row.empty else 0.0

        st.info(f"📌 Target for **{ds_operation}**: **{target_val} pcs** | Rate: **₹{rate_val}/pc**")
        ds_achieved = st.number_input("Pieces Achieved Today", min_value=0, step=1)

        ds_submitted = st.form_submit_button("💾 Save Daily Entry", use_container_width=True)
        if ds_submitted:
            karigar_id2   = karigar_options2[ds_karigar]
            karigar_name2 = ds_karigar.split("–")[1].strip()
            new_ds = {
                "Date": str(ds_date),
                "Karigar_ID": karigar_id2,
                "Karigar_Name": karigar_name2,
                "Style": ds_style,
                "Challan_No": ds_challan,
                "Operation": ds_operation,
                "Target": target_val,
                "Achieved": ds_achieved,
                "Rate_Rs": rate_val
            }
            st.session_state.daily_sheet = pd.concat(
                [st.session_state.daily_sheet, pd.DataFrame([new_ds])], ignore_index=True
            )
            eff = (ds_achieved / target_val * 100) if target_val > 0 else 0
            earned = ds_achieved * rate_val
            st.success(f"✅ Saved! Efficiency: {eff:.1f}% | Earned: ₹{earned:.2f}")

    st.markdown("---")
    if not st.session_state.daily_sheet.empty:
        st.markdown('<div class="section-title">📄 Daily Sheet Records</div>', unsafe_allow_html=True)
        ds_filter = st.date_input("Filter by Date", value=date.today(), key="ds_filter")
        ds_filtered = st.session_state.daily_sheet[st.session_state.daily_sheet["Date"] == str(ds_filter)].copy()

        if not ds_filtered.empty:
            ds_filtered["Efficiency_%"] = (ds_filtered["Achieved"] / ds_filtered["Target"] * 100).round(1)
            ds_filtered["Earned_Rs"]   = (ds_filtered["Achieved"] * ds_filtered["Rate_Rs"]).round(2)
            ds_filtered["Status"] = ds_filtered["Efficiency_%"].apply(
                lambda x: "🟢 On Target" if x >= 100 else ("🟡 Near Target" if x >= 80 else "🔴 Below Target")
            )
            st.dataframe(ds_filtered, use_container_width=True, hide_index=True)

            # Summary by karigar
            st.markdown('<div class="section-title">👷 Karigar Summary</div>', unsafe_allow_html=True)
            karigar_summary = ds_filtered.groupby("Karigar_Name").agg(
                Operations=("Operation","count"),
                Total_Target=("Target","sum"),
                Total_Achieved=("Achieved","sum"),
                Total_Earned_Rs=("Earned_Rs","sum")
            ).reset_index()
            karigar_summary["Overall_Efficiency_%"] = (
                karigar_summary["Total_Achieved"] / karigar_summary["Total_Target"] * 100
            ).round(1)
            st.dataframe(karigar_summary, use_container_width=True, hide_index=True)
        else:
            st.info("No entries for selected date.")
    else:
        st.info("No daily sheet entries yet.")


# ════════════════════════════════════════════════════════════
# TAB 4 – CHALLAN MANAGEMENT
# ════════════════════════════════════════════════════════════
with tab_challan:
    st.markdown('<div class="section-title">🧾 Challan-wise Style Costing</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Each Style can have multiple Challans (batches). Track costing per challan across all operations.</div>', unsafe_allow_html=True)

    # Add new challan
    with st.expander("➕ Add New Challan", expanded=False):
        with st.form("challan_form", clear_on_submit=True):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                c_no    = st.text_input("Challan No (e.g. CH-004)")
                c_style = st.selectbox("Style", st.session_state.style_master["Style"].unique().tolist())
            with cc2:
                c_sku  = st.text_input("SKU")
                c_qty  = st.number_input("Quantity", min_value=1, step=1)
            with cc3:
                c_date = st.date_input("Challan Date", value=date.today())
            c_submit = st.form_submit_button("Add Challan")
            if c_submit and c_no:
                new_challan = {"Challan_No": c_no, "Style": c_style, "SKU": c_sku, "Qty": c_qty, "Date": str(c_date)}
                st.session_state.challan_master = pd.concat(
                    [st.session_state.challan_master, pd.DataFrame([new_challan])], ignore_index=True
                )
                st.success(f"✅ Challan {c_no} added!")

    st.markdown("---")
    st.dataframe(st.session_state.challan_master, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">📊 Challan-wise Costing Report</div>', unsafe_allow_html=True)
    if not st.session_state.daily_sheet.empty:
        challan_cost = st.session_state.daily_sheet.copy()
        challan_cost["Earned_Rs"] = challan_cost["Achieved"] * challan_cost["Rate_Rs"]
        challan_summary = challan_cost.groupby(["Style","Challan_No","Operation"]).agg(
            Total_Achieved=("Achieved","sum"),
            Total_Earned_Rs=("Earned_Rs","sum")
        ).reset_index()

        selected_challan = st.selectbox(
            "Select Challan to View Costing",
            st.session_state.challan_master["Challan_No"].tolist()
        )
        challan_view = challan_summary[challan_summary["Challan_No"] == selected_challan]
        if not challan_view.empty:
            st.dataframe(challan_view, use_container_width=True, hide_index=True)
            total = challan_view["Total_Earned_Rs"].sum()
            ch_row = st.session_state.challan_master[st.session_state.challan_master["Challan_No"] == selected_challan]
            qty = int(ch_row["Qty"].values[0]) if not ch_row.empty else 1
            cost_per_pc = total / qty if qty > 0 else 0
            col_x, col_y = st.columns(2)
            col_x.metric("Total Labour Cost", f"₹{total:,.2f}")
            col_y.metric("Cost per Piece", f"₹{cost_per_pc:.2f}")
        else:
            st.info("No production data for this challan yet. Add daily sheet entries first.")
    else:
        st.info("Add daily sheet entries to see challan-wise costing.")


# ════════════════════════════════════════════════════════════
# TAB 5 – EFFICIENCY & COSTING ANALYSIS
# ════════════════════════════════════════════════════════════
with tab_efficiency:
    st.markdown('<div class="section-title">📊 Efficiency & Deep Analysis</div>', unsafe_allow_html=True)

    if st.session_state.daily_sheet.empty:
        st.info("No data yet. Fill in the Karigar Daily Sheet to see analysis here.")
    else:
        df = st.session_state.daily_sheet.copy()
        df["Efficiency_%"] = (df["Achieved"] / df["Target"] * 100).round(1)
        df["Earned_Rs"]    = (df["Achieved"] * df["Rate_Rs"]).round(2)
        df["Date"] = pd.to_datetime(df["Date"])

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            date_range = st.date_input("Date Range", value=[date.today() - timedelta(days=7), date.today()])
        with col_f2:
            style_filter = st.multiselect("Filter Style", df["Style"].unique().tolist(), default=df["Style"].unique().tolist())

        if len(date_range) == 2:
            mask = (
                (df["Date"] >= pd.Timestamp(date_range[0])) &
                (df["Date"] <= pd.Timestamp(date_range[1])) &
                (df["Style"].isin(style_filter))
            )
            df_f = df[mask].copy()
        else:
            df_f = df[df["Style"].isin(style_filter)].copy()

        if df_f.empty:
            st.warning("No data for selected filters.")
        else:
            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Efficiency", f"{df_f['Efficiency_%'].mean():.1f}%")
            c2.metric("Total Earned", f"₹{df_f['Earned_Rs'].sum():,.0f}")
            c3.metric("Total Pieces", f"{int(df_f['Achieved'].sum()):,}")

            st.markdown("---")

            # Karigar Efficiency Table
            st.markdown('<div class="section-title">👷 Karigar-wise Efficiency</div>', unsafe_allow_html=True)
            karigar_eff = df_f.groupby("Karigar_Name").agg(
                Avg_Efficiency=("Efficiency_%","mean"),
                Total_Achieved=("Achieved","sum"),
                Total_Earned_Rs=("Earned_Rs","sum"),
                Operations_Done=("Operation","count")
            ).round(2).reset_index()
            karigar_eff["Grade"] = karigar_eff["Avg_Efficiency"].apply(
                lambda x: "🏆 A" if x >= 100 else ("✅ B" if x >= 85 else ("⚠️ C" if x >= 70 else "❌ D"))
            )
            st.dataframe(karigar_eff, use_container_width=True, hide_index=True)

            # Operation-wise Efficiency
            st.markdown('<div class="section-title">🔧 Operation-wise Performance</div>', unsafe_allow_html=True)
            op_eff = df_f.groupby("Operation").agg(
                Avg_Efficiency=("Efficiency_%","mean"),
                Total_Achieved=("Achieved","sum"),
                Total_Cost_Rs=("Earned_Rs","sum")
            ).round(2).reset_index().sort_values("Avg_Efficiency")
            st.dataframe(op_eff, use_container_width=True, hide_index=True)

            # Bottleneck Detection
            bottleneck = op_eff[op_eff["Avg_Efficiency"] < 80]
            if not bottleneck.empty:
                st.warning(f"⚠️ **Bottleneck Operations** (Efficiency < 80%): {', '.join(bottleneck['Operation'].tolist())}")

            # Style-wise Costing
            st.markdown('<div class="section-title">👗 Style-wise Labour Costing</div>', unsafe_allow_html=True)
            style_cost = df_f.groupby(["Style","Operation"]).agg(
                Total_Pieces=("Achieved","sum"),
                Total_Cost_Rs=("Earned_Rs","sum")
            ).reset_index()
            st.dataframe(style_cost, use_container_width=True, hide_index=True)

            total_by_style = style_cost.groupby("Style")["Total_Cost_Rs"].sum().reset_index()
            total_by_style.columns = ["Style","Total_Labour_Cost_Rs"]
            st.dataframe(total_by_style, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
# TAB 6 – PAYROLL CALCULATOR
# ════════════════════════════════════════════════════════════
with tab_payroll:
    st.markdown('<div class="section-title">💰 Karigar Payroll Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Calculate how much to pay each karigar based on piece-rate earned vs. daily rate guarantee.</div>', unsafe_allow_html=True)

    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        pay_start = st.date_input("Pay Period Start", value=date.today() - timedelta(days=6))
    with pay_col2:
        pay_end   = st.date_input("Pay Period End",   value=date.today())

    if st.button("📊 Calculate Payroll", use_container_width=True):
        if st.session_state.daily_sheet.empty:
            st.warning("No daily sheet data available.")
        else:
            df_pay = st.session_state.daily_sheet.copy()
            df_pay["Date_dt"] = pd.to_datetime(df_pay["Date"])
            df_pay = df_pay[
                (df_pay["Date_dt"] >= pd.Timestamp(pay_start)) &
                (df_pay["Date_dt"] <= pd.Timestamp(pay_end))
            ]

            if df_pay.empty:
                st.warning("No data in this pay period.")
            else:
                df_pay["Piece_Earned"] = df_pay["Achieved"] * df_pay["Rate_Rs"]
                days_in_period = (pay_end - pay_start).days + 1

                payroll = df_pay.groupby("Karigar_ID").agg(
                    Total_Piece_Earned=("Piece_Earned","sum"),
                    Total_Pieces=("Achieved","sum")
                ).reset_index()

                km = st.session_state.karigar_master[["Karigar_ID","Name","Daily_Rate_Rs"]]
                payroll = payroll.merge(km, on="Karigar_ID", how="left")
                payroll["Guaranteed_Pay"] = payroll["Daily_Rate_Rs"] * days_in_period
                payroll["Final_Pay_Rs"] = payroll[["Total_Piece_Earned","Guaranteed_Pay"]].max(axis=1)
                payroll["Pay_Basis"] = payroll.apply(
                    lambda r: "Piece-rate 💪" if r["Total_Piece_Earned"] >= r["Guaranteed_Pay"] else "Daily-rate 📅",
                    axis=1
                )
                payroll["Efficiency_Bonus"] = 0.0
                # Bonus: if piece-rate > 120% of guaranteed, add 5% bonus
                payroll.loc[payroll["Total_Piece_Earned"] > payroll["Guaranteed_Pay"] * 1.2, "Efficiency_Bonus"] = (
                    payroll["Final_Pay_Rs"] * 0.05
                )
                payroll["Total_with_Bonus"] = payroll["Final_Pay_Rs"] + payroll["Efficiency_Bonus"]

                display_cols = ["Name","Total_Pieces","Total_Piece_Earned","Guaranteed_Pay","Final_Pay_Rs","Efficiency_Bonus","Total_with_Bonus","Pay_Basis"]
                payroll_display = payroll[display_cols].copy()
                payroll_display = payroll_display.round(2)
                st.dataframe(payroll_display, use_container_width=True, hide_index=True)

                st.markdown("---")
                total_payroll = payroll_display["Total_with_Bonus"].sum()
                st.metric("💰 Total Payroll Amount", f"₹{total_payroll:,.2f}")

                # Export
                csv_buf = io.StringIO()
                payroll_display.to_csv(csv_buf, index=False)
                st.download_button(
                    "📥 Download Payroll CSV",
                    data=csv_buf.getvalue(),
                    file_name=f"payroll_{pay_start}_{pay_end}.csv",
                    mime="text/csv"
                )


# ════════════════════════════════════════════════════════════
# TAB 7 – MASTER DATA
# ════════════════════════════════════════════════════════════
with tab_master:
    st.markdown('<div class="section-title">⚙️ Master Data Management</div>', unsafe_allow_html=True)

    m_tab1, m_tab2 = st.tabs(["👗 Style-Operation Master", "👷 Karigar Master"])

    with m_tab1:
        st.markdown('<div class="section-title">Style Operations, Targets & Rates</div>', unsafe_allow_html=True)

        with st.expander("➕ Add Operation to Style"):
            with st.form("style_op_form", clear_on_submit=True):
                s1, s2 = st.columns(2)
                with s1:
                    new_style  = st.text_input("Style Code (e.g. 1066YKRED)")
                    new_op     = st.text_input("Operation Name")
                with s2:
                    new_target = st.number_input("Daily Target (pcs)", min_value=1, step=1)
                    new_rate   = st.number_input("Rate per Piece (₹)", min_value=0.0, step=0.25, format="%.2f")
                if st.form_submit_button("Add"):
                    if new_style and new_op:
                        row = {"Style": new_style, "Operation": new_op, "Target": new_target, "Rate_Rs": new_rate}
                        st.session_state.style_master = pd.concat(
                            [st.session_state.style_master, pd.DataFrame([row])], ignore_index=True
                        )
                        st.success(f"✅ Added {new_op} for style {new_style}")

        st.dataframe(st.session_state.style_master, use_container_width=True, hide_index=True)

        # Style Summary
        style_summary = st.session_state.style_master.groupby("Style").agg(
            Total_Operations=("Operation","count"),
            Total_Rate_Per_Garment=("Rate_Rs","sum"),
            Slowest_Operation_Target=("Target","min")
        ).reset_index()
        st.markdown('<div class="section-title">Style Summary (SMV)</div>', unsafe_allow_html=True)
        st.dataframe(style_summary, use_container_width=True, hide_index=True)

    with m_tab2:
        st.markdown('<div class="section-title">Karigar Register</div>', unsafe_allow_html=True)

        with st.expander("➕ Add Karigar"):
            with st.form("karigar_form", clear_on_submit=True):
                k1, k2 = st.columns(2)
                with k1:
                    k_id   = st.text_input("Karigar ID (e.g. K006)")
                    k_name = st.text_input("Full Name")
                with k2:
                    k_skill = st.selectbox("Skill", ["Stitching","Cutting","Finishing","Hemming","Checking","General"])
                    k_rate  = st.number_input("Daily Rate (₹)", min_value=100, step=10)
                if st.form_submit_button("Add Karigar"):
                    if k_id and k_name:
                        new_k = {"Karigar_ID": k_id, "Name": k_name, "Skill": k_skill, "Daily_Rate_Rs": k_rate}
                        st.session_state.karigar_master = pd.concat(
                            [st.session_state.karigar_master, pd.DataFrame([new_k])], ignore_index=True
                        )
                        st.success(f"✅ Karigar {k_name} added!")

        st.dataframe(st.session_state.karigar_master, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#aaa; font-size:0.8rem;'>🧵 Stitching Costing Interface · Textile Garments Karigar Management System</center>",
    unsafe_allow_html=True
)
