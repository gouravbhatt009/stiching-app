"""
Stitching Costing Interface - Streamlit App
Textile Garments Company - Karigar Time Tracking & Costing System
With Excel/CSV Import & Template Downloads for all sections
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
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
        padding: 20px 30px; border-radius: 12px;
        margin-bottom: 20px; color: white; text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2rem; letter-spacing: 1px; }
    .main-header p  { margin: 5px 0 0; opacity: 0.75; font-size: 0.95rem; }
    .metric-card {
        background: white; border-radius: 10px; padding: 18px 20px;
        border-left: 5px solid #0f3460;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 10px;
    }
    .metric-card .label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
    .metric-card .sub   { font-size: 0.85rem; color: #0f3460; }
    .efficiency-high { color: #28a745 !important; }
    .efficiency-mid  { color: #ffc107 !important; }
    .efficiency-low  { color: #dc3545 !important; }
    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #0f3460;
        border-bottom: 2px solid #e0e0e0; padding-bottom: 6px; margin-bottom: 16px;
    }
    .info-box {
        background: #f0f4ff; border-radius: 8px; padding: 12px 16px;
        border: 1px solid #c5d5ff; font-size: 0.9rem;
        color: #2c3e6e; margin-bottom: 12px;
    }
    .import-box {
        background: #fff8e1; border-radius: 8px; padding: 14px 18px;
        border: 1px solid #ffe082; margin-bottom: 14px;
    }
    div[data-testid="stTabs"] button { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Helper: read uploaded file (CSV or Excel)
# ─────────────────────────────────────────────
def read_upload(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload .csv or .xlsx")
        return None

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# ─────────────────────────────────────────────
# Reusable Import Widget
# ─────────────────────────────────────────────
def import_section(key, required_cols, session_key, template_df, label):
    with st.expander(f"📥 Import {label} from Excel / CSV", expanded=False):
        st.markdown(
            f'<div class="import-box">'
            f'<b>Step 1:</b> Download the template &rarr; fill your data &rarr; upload it back.<br>'
            f'<b>Required columns:</b> <code>{", ".join(required_cols)}</code>'
            f'</div>', unsafe_allow_html=True
        )
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download Excel Template",
                data=df_to_excel_bytes(template_df),
                file_name=f"{key}_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xlsx_{key}"
            )
        with dl2:
            st.download_button(
                "⬇️ Download CSV Template",
                data=df_to_csv_bytes(template_df),
                file_name=f"{key}_template.csv",
                mime="text/csv",
                key=f"dl_csv_{key}"
            )

        uploaded = st.file_uploader(
            "📂 Upload your filled file (.csv or .xlsx)",
            type=["csv", "xlsx", "xls"],
            key=f"uploader_{key}"
        )
        mode = st.radio(
            "Import mode",
            ["➕ Append to existing data", "🔄 Replace all existing data"],
            key=f"mode_{key}"
        )

        if uploaded is not None:
            df_new = read_upload(uploaded)
            if df_new is not None:
                missing = [c for c in required_cols if c not in df_new.columns]
                if missing:
                    st.error(f"❌ Missing columns: {missing}. Check your file headers.")
                    return
                st.markdown("**Preview (first 5 rows):**")
                st.dataframe(df_new.head(), use_container_width=True, hide_index=True)
                st.info(f"✅ {len(df_new)} rows | {len(df_new.columns)} columns detected")

                if st.button(f"✅ Confirm Import into {label}", key=f"confirm_{key}"):
                    if "Replace" in mode:
                        st.session_state[session_key] = df_new.reset_index(drop=True)
                        st.success(f"🔄 Replaced! {len(df_new)} rows loaded.")
                    else:
                        st.session_state[session_key] = pd.concat(
                            [st.session_state[session_key], df_new], ignore_index=True
                        )
                        st.success(f"➕ Appended! {len(df_new)} new rows added.")
                    st.rerun()

# ─────────────────────────────────────────────
# Templates (sample rows for download)
# ─────────────────────────────────────────────
TEMPLATES = {
    "style_master": pd.DataFrame([
        {"Style": "1065YKBLUE", "Operation": "Cutting",        "Target": 120, "Rate_Rs": 2.50},
        {"Style": "1065YKBLUE", "Operation": "Stitching Front","Target": 80,  "Rate_Rs": 4.00},
        {"Style": "NEWSTYLE",   "Operation": "Hemming",        "Target": 100, "Rate_Rs": 3.00},
    ]),
    "karigar_master": pd.DataFrame([
        {"Karigar_ID": "K001", "Name": "Ramesh Kumar", "Skill": "Stitching", "Daily_Rate_Rs": 450},
        {"Karigar_ID": "K002", "Name": "Suresh Singh", "Skill": "Cutting",   "Daily_Rate_Rs": 420},
    ]),
    "challan_master": pd.DataFrame([
        {"Challan_No": "CH-001", "Style": "1065YKBLUE", "SKU": "YK-BLU-M", "Qty": 200, "Date": "2025-01-15"},
        {"Challan_No": "CH-002", "Style": "1065YKBLUE", "SKU": "YK-BLU-L", "Qty": 150, "Date": "2025-01-16"},
    ]),
    "time_log": pd.DataFrame([
        {"Date": "2025-01-15", "Karigar_ID": "K001", "Karigar_Name": "Ramesh Kumar",
         "Hour_Slot": "08:00-09:00", "Style": "1065YKBLUE", "Challan_No": "CH-001",
         "Operation": "Cutting", "Pieces_Done": 12},
        {"Date": "2025-01-15", "Karigar_ID": "K002", "Karigar_Name": "Suresh Singh",
         "Hour_Slot": "09:00-10:00", "Style": "1065YKBLUE", "Challan_No": "CH-001",
         "Operation": "Stitching Front", "Pieces_Done": 8},
    ]),
    "daily_sheet": pd.DataFrame([
        {"Date": "2025-01-15", "Karigar_ID": "K001", "Karigar_Name": "Ramesh Kumar",
         "Style": "1065YKBLUE", "Challan_No": "CH-001",
         "Operation": "Cutting", "Target": 120, "Achieved": 110, "Rate_Rs": 2.50},
        {"Date": "2025-01-15", "Karigar_ID": "K002", "Karigar_Name": "Suresh Singh",
         "Style": "1065YKBLUE", "Challan_No": "CH-001",
         "Operation": "Stitching Front", "Target": 80, "Achieved": 85, "Rate_Rs": 4.00},
    ]),
}

# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
def init_state():
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
    if "karigar_master" not in st.session_state:
        st.session_state.karigar_master = pd.DataFrame([
            {"Karigar_ID": "K001", "Name": "Ramesh Kumar",  "Skill": "Stitching", "Daily_Rate_Rs": 450},
            {"Karigar_ID": "K002", "Name": "Suresh Singh",  "Skill": "Cutting",   "Daily_Rate_Rs": 420},
            {"Karigar_ID": "K003", "Name": "Priya Devi",    "Skill": "Finishing",  "Daily_Rate_Rs": 400},
            {"Karigar_ID": "K004", "Name": "Mohan Lal",     "Skill": "Stitching", "Daily_Rate_Rs": 460},
            {"Karigar_ID": "K005", "Name": "Sunita Sharma", "Skill": "Hemming",   "Daily_Rate_Rs": 410},
        ])
    if "challan_master" not in st.session_state:
        st.session_state.challan_master = pd.DataFrame([
            {"Challan_No": "CH-001", "Style": "1065YKBLUE", "SKU": "YK-BLU-M",  "Qty": 200, "Date": "2025-01-15"},
            {"Challan_No": "CH-002", "Style": "1065YKBLUE", "SKU": "YK-BLU-L",  "Qty": 150, "Date": "2025-01-16"},
            {"Challan_No": "CH-003", "Style": "1065YKBLUE", "SKU": "YK-BLU-XL", "Qty": 100, "Date": "2025-01-17"},
        ])
    if "time_log" not in st.session_state:
        st.session_state.time_log = pd.DataFrame(columns=[
            "Date","Karigar_ID","Karigar_Name","Hour_Slot",
            "Style","Challan_No","Operation","Pieces_Done"
        ])
    if "daily_sheet" not in st.session_state:
        st.session_state.daily_sheet = pd.DataFrame(columns=[
            "Date","Karigar_ID","Karigar_Name",
            "Style","Challan_No","Operation",
            "Target","Achieved","Rate_Rs"
        ])

init_state()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧵 Stitching Costing Interface</h1>
    <p>Karigar Time Tracking · Challan-wise Costing · Efficiency Analysis · Payroll · Import/Export</p>
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

    today_str   = str(date.today())
    today_log   = st.session_state.time_log[st.session_state.time_log["Date"] == today_str]
    today_daily = st.session_state.daily_sheet[st.session_state.daily_sheet["Date"] == today_str]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        active = today_log["Karigar_ID"].nunique() if not today_log.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Active Karigar Today</div>
            <div class="value">{active}</div>
            <div class="sub">of {len(st.session_state.karigar_master)} total</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        pieces = int(today_log["Pieces_Done"].sum()) if not today_log.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Pieces Done Today</div>
            <div class="value">{pieces}</div>
            <div class="sub">across all operations</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        if not today_daily.empty and "Target" in today_daily and "Achieved" in today_daily:
            avg_eff = (today_daily["Achieved"] / today_daily["Target"] * 100).mean()
            ec = "efficiency-high" if avg_eff >= 90 else ("efficiency-mid" if avg_eff >= 70 else "efficiency-low")
        else:
            avg_eff, ec = 0, "efficiency-low"
        st.markdown(f"""<div class="metric-card">
            <div class="label">Avg Efficiency</div>
            <div class="value {ec}">{avg_eff:.1f}%</div>
            <div class="sub">Target: 100%</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        cost = (today_daily["Achieved"] * today_daily["Rate_Rs"]).sum() if not today_daily.empty else 0
        st.markdown(f"""<div class="metric-card">
            <div class="label">Today's Labour Cost</div>
            <div class="value">&#8377;{cost:,.0f}</div>
            <div class="sub">piece-rate earned</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cola, colb = st.columns(2)
    with cola:
        st.markdown('<div class="section-title">👷 Karigar Status</div>', unsafe_allow_html=True)
        km = st.session_state.karigar_master.copy()
        active_ids = today_log["Karigar_ID"].unique().tolist() if not today_log.empty else []
        km["Status"] = km["Karigar_ID"].apply(lambda x: "🟢 Working" if x in active_ids else "⚪ Idle")
        st.dataframe(km[["Karigar_ID","Name","Skill","Status"]], use_container_width=True, hide_index=True)
    with colb:
        st.markdown('<div class="section-title">🧾 Active Challans</div>', unsafe_allow_html=True)
        st.dataframe(st.session_state.challan_master, use_container_width=True, hide_index=True)

    if not today_daily.empty:
        st.markdown("---")
        st.markdown('<div class="section-title">📋 Today\'s Daily Sheet Summary</div>', unsafe_allow_html=True)
        ds = today_daily.copy()
        if "Achieved" in ds and "Target" in ds:
            ds["Efficiency_%"] = (ds["Achieved"] / ds["Target"] * 100).round(1)
            ds["Earned_Rs"]    = (ds["Achieved"] * ds["Rate_Rs"]).round(2)
        st.dataframe(ds, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
# TAB 2 – HOUR-WISE TIME LOG
# ════════════════════════════════════════════════════════════
with tab_timelog:
    st.markdown('<div class="section-title">⏱️ Hour-wise Time Entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Log which karigar worked on which style/challan each hour of the 11-hour shift (8 AM to 7 PM).</div>', unsafe_allow_html=True)

    import_section(
        key="time_log",
        required_cols=["Date","Karigar_ID","Karigar_Name","Hour_Slot","Style","Challan_No","Operation","Pieces_Done"],
        session_key="time_log",
        template_df=TEMPLATES["time_log"],
        label="Hour-wise Time Log"
    )

    hour_slots   = [f"{h:02d}:00-{h+1:02d}:00" for h in range(8, 19)]
    styles_list  = st.session_state.style_master["Style"].unique().tolist()
    challan_list = st.session_state.challan_master["Challan_No"].tolist()
    karigar_options = {
        f"{r['Karigar_ID']} - {r['Name']}": (r['Karigar_ID'], r['Name'])
        for _, r in st.session_state.karigar_master.iterrows()
    }

    with st.expander("✏️ Manual Entry", expanded=True):
        with st.form("time_log_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                tl_date    = st.date_input("Date", value=date.today())
                tl_karigar = st.selectbox("Karigar", list(karigar_options.keys()))
                tl_hour    = st.selectbox("Hour Slot", hour_slots)
            with c2:
                tl_style   = st.selectbox("Style", styles_list) if styles_list else st.text_input("Style")
                tl_challan = st.selectbox("Challan No", challan_list) if challan_list else st.text_input("Challan No")
            with c3:
                ops = st.session_state.style_master[
                    st.session_state.style_master["Style"] == tl_style
                ]["Operation"].tolist() if styles_list else []
                tl_op     = st.selectbox("Operation", ops) if ops else st.text_input("Operation")
                tl_pieces = st.number_input("Pieces Done", min_value=0, step=1)

            if st.form_submit_button("Save Time Entry", use_container_width=True):
                kid, kname = karigar_options[tl_karigar]
                new_row = {
                    "Date": str(tl_date), "Karigar_ID": kid, "Karigar_Name": kname,
                    "Hour_Slot": tl_hour, "Style": tl_style, "Challan_No": tl_challan,
                    "Operation": tl_op, "Pieces_Done": tl_pieces
                }
                st.session_state.time_log = pd.concat(
                    [st.session_state.time_log, pd.DataFrame([new_row])], ignore_index=True
                )
                st.success(f"Saved: {kname} | {tl_hour} | {tl_op} | {tl_pieces} pcs")

    st.markdown("---")
    st.markdown('<div class="section-title">Time Log Records</div>', unsafe_allow_html=True)
    if not st.session_state.time_log.empty:
        tl_filter = st.date_input("Filter by Date", value=date.today(), key="tl_filter")
        filtered  = st.session_state.time_log[st.session_state.time_log["Date"] == str(tl_filter)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            try:
                pivot = filtered.pivot_table(
                    index="Karigar_Name", columns="Hour_Slot",
                    values="Pieces_Done", aggfunc="sum", fill_value=0
                )
                st.markdown('<div class="section-title">Hour-wise Heatmap</div>', unsafe_allow_html=True)
                st.dataframe(pivot.style.background_gradient(cmap="Blues"), use_container_width=True)
            except Exception:
                pass
            ex1, ex2 = st.columns(2)
            with ex1:
                st.download_button("📥 Export Excel", data=df_to_excel_bytes(filtered),
                    file_name="time_log_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with ex2:
                st.download_button("📥 Export CSV", data=df_to_csv_bytes(filtered),
                    file_name="time_log_export.csv", mime="text/csv")
        else:
            st.info("No entries for selected date.")
    else:
        st.info("No time log entries yet. Use import or manual entry above.")


# ════════════════════════════════════════════════════════════
# TAB 3 – KARIGAR DAILY SHEET
# ════════════════════════════════════════════════════════════
with tab_daily:
    st.markdown('<div class="section-title">📋 Karigar Daily Sheet - Operation-wise</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Enter daily production per karigar per operation. Target and rate are auto-fetched from master data.</div>', unsafe_allow_html=True)

    import_section(
        key="daily_sheet",
        required_cols=["Date","Karigar_ID","Karigar_Name","Style","Challan_No","Operation","Target","Achieved","Rate_Rs"],
        session_key="daily_sheet",
        template_df=TEMPLATES["daily_sheet"],
        label="Karigar Daily Sheet"
    )

    karigar_opts2 = {
        f"{r['Karigar_ID']} - {r['Name']}": (r['Karigar_ID'], r['Name'])
        for _, r in st.session_state.karigar_master.iterrows()
    }
    styles_list2  = st.session_state.style_master["Style"].unique().tolist()
    challan_list2 = st.session_state.challan_master["Challan_No"].tolist()

    with st.expander("✏️ Manual Entry", expanded=True):
        with st.form("daily_sheet_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ds_date    = st.date_input("Date", value=date.today())
                ds_karigar = st.selectbox("Karigar", list(karigar_opts2.keys()))
                ds_style   = st.selectbox("Style", styles_list2) if styles_list2 else st.text_input("Style")
            with c2:
                ds_challan = st.selectbox("Challan No", challan_list2) if challan_list2 else st.text_input("Challan")
                ds_ops = st.session_state.style_master[
                    st.session_state.style_master["Style"] == ds_style
                ][["Operation","Target","Rate_Rs"]] if styles_list2 else pd.DataFrame()
                ds_op = st.selectbox("Operation", ds_ops["Operation"].tolist()) if not ds_ops.empty else st.text_input("Operation")

            op_row   = ds_ops[ds_ops["Operation"] == ds_op] if not ds_ops.empty else pd.DataFrame()
            tgt_val  = int(op_row["Target"].values[0])    if not op_row.empty else 0
            rate_val = float(op_row["Rate_Rs"].values[0]) if not op_row.empty else 0.0
            st.info(f"Target: {tgt_val} pcs | Rate: Rs {rate_val}/pc")
            ds_achieved = st.number_input("Pieces Achieved", min_value=0, step=1)

            if st.form_submit_button("Save Daily Entry", use_container_width=True):
                kid2, kname2 = karigar_opts2[ds_karigar]
                eff = (ds_achieved / tgt_val * 100) if tgt_val > 0 else 0
                new_ds = {
                    "Date": str(ds_date), "Karigar_ID": kid2, "Karigar_Name": kname2,
                    "Style": ds_style, "Challan_No": ds_challan,
                    "Operation": ds_op, "Target": tgt_val,
                    "Achieved": ds_achieved, "Rate_Rs": rate_val
                }
                st.session_state.daily_sheet = pd.concat(
                    [st.session_state.daily_sheet, pd.DataFrame([new_ds])], ignore_index=True
                )
                st.success(f"Saved! Efficiency: {eff:.1f}% | Earned: Rs {ds_achieved * rate_val:.2f}")

    st.markdown("---")
    if not st.session_state.daily_sheet.empty:
        st.markdown('<div class="section-title">Daily Sheet Records</div>', unsafe_allow_html=True)
        ds_filter   = st.date_input("Filter by Date", value=date.today(), key="ds_filter")
        ds_filtered = st.session_state.daily_sheet[
            st.session_state.daily_sheet["Date"] == str(ds_filter)
        ].copy()

        if not ds_filtered.empty:
            ds_filtered["Efficiency_%"] = (ds_filtered["Achieved"] / ds_filtered["Target"] * 100).round(1)
            ds_filtered["Earned_Rs"]   = (ds_filtered["Achieved"] * ds_filtered["Rate_Rs"]).round(2)
            ds_filtered["Status"] = ds_filtered["Efficiency_%"].apply(
                lambda x: "On Target" if x >= 100 else ("Near Target" if x >= 80 else "Below Target")
            )
            st.dataframe(ds_filtered, use_container_width=True, hide_index=True)

            ks = ds_filtered.groupby("Karigar_Name").agg(
                Ops=("Operation","count"),
                Total_Target=("Target","sum"),
                Total_Achieved=("Achieved","sum"),
                Total_Earned_Rs=("Earned_Rs","sum")
            ).reset_index()
            ks["Overall_Eff_%"] = (ks["Total_Achieved"] / ks["Total_Target"] * 100).round(1)
            st.markdown('<div class="section-title">Karigar Summary</div>', unsafe_allow_html=True)
            st.dataframe(ks, use_container_width=True, hide_index=True)

            ex1, ex2 = st.columns(2)
            with ex1:
                st.download_button("📥 Export Excel", data=df_to_excel_bytes(ds_filtered),
                    file_name="daily_sheet_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with ex2:
                st.download_button("📥 Export CSV", data=df_to_csv_bytes(ds_filtered),
                    file_name="daily_sheet_export.csv", mime="text/csv")
        else:
            st.info("No entries for selected date.")
    else:
        st.info("No daily sheet entries yet.")


# ════════════════════════════════════════════════════════════
# TAB 4 – CHALLAN MANAGEMENT
# ════════════════════════════════════════════════════════════
with tab_challan:
    st.markdown('<div class="section-title">🧾 Challan-wise Style Costing</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Each Style can have multiple Challans (batches). Track costing per challan.</div>', unsafe_allow_html=True)

    import_section(
        key="challan_master",
        required_cols=["Challan_No","Style","SKU","Qty","Date"],
        session_key="challan_master",
        template_df=TEMPLATES["challan_master"],
        label="Challan Master"
    )

    with st.expander("➕ Add New Challan Manually"):
        with st.form("challan_form", clear_on_submit=True):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                c_no    = st.text_input("Challan No (e.g. CH-004)")
                c_style = st.selectbox("Style", st.session_state.style_master["Style"].unique().tolist()) \
                          if not st.session_state.style_master.empty else st.text_input("Style")
            with cc2:
                c_sku  = st.text_input("SKU")
                c_qty  = st.number_input("Quantity", min_value=1, step=1)
            with cc3:
                c_date = st.date_input("Challan Date", value=date.today())
            if st.form_submit_button("Add Challan") and c_no:
                new_c = {"Challan_No": c_no, "Style": c_style, "SKU": c_sku, "Qty": int(c_qty), "Date": str(c_date)}
                st.session_state.challan_master = pd.concat(
                    [st.session_state.challan_master, pd.DataFrame([new_c])], ignore_index=True
                )
                st.success(f"Challan {c_no} added!")

    st.markdown("---")
    st.dataframe(st.session_state.challan_master, use_container_width=True, hide_index=True)

    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button("📥 Export Challan List (Excel)",
            data=df_to_excel_bytes(st.session_state.challan_master),
            file_name="challans.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with ex2:
        st.download_button("📥 Export Challan List (CSV)",
            data=df_to_csv_bytes(st.session_state.challan_master),
            file_name="challans.csv", mime="text/csv")

    st.markdown('<div class="section-title">Challan-wise Costing Report</div>', unsafe_allow_html=True)
    if not st.session_state.daily_sheet.empty and not st.session_state.challan_master.empty:
        cc = st.session_state.daily_sheet.copy()
        cc["Earned_Rs"] = cc["Achieved"] * cc["Rate_Rs"]
        ch_summary = cc.groupby(["Style","Challan_No","Operation"]).agg(
            Total_Achieved=("Achieved","sum"),
            Total_Earned_Rs=("Earned_Rs","sum")
        ).reset_index()

        sel_challan = st.selectbox("Select Challan to View Costing",
            st.session_state.challan_master["Challan_No"].tolist())
        ch_view = ch_summary[ch_summary["Challan_No"] == sel_challan]
        if not ch_view.empty:
            st.dataframe(ch_view, use_container_width=True, hide_index=True)
            total_ch = ch_view["Total_Earned_Rs"].sum()
            qty_row  = st.session_state.challan_master[st.session_state.challan_master["Challan_No"] == sel_challan]
            qty      = int(qty_row["Qty"].values[0]) if not qty_row.empty else 1
            col_x, col_y = st.columns(2)
            col_x.metric("Total Labour Cost", f"Rs {total_ch:,.2f}")
            col_y.metric("Cost per Piece",    f"Rs {total_ch / qty:.2f}")
        else:
            st.info("No production data for this challan yet.")
    else:
        st.info("Add daily sheet entries to see challan-wise costing.")


# ════════════════════════════════════════════════════════════
# TAB 5 – EFFICIENCY & COSTING
# ════════════════════════════════════════════════════════════
with tab_efficiency:
    st.markdown('<div class="section-title">📊 Efficiency & Deep Analysis</div>', unsafe_allow_html=True)

    if st.session_state.daily_sheet.empty:
        st.info("No data yet. Fill in the Karigar Daily Sheet to see analysis here.")
    else:
        df = st.session_state.daily_sheet.copy()
        df["Efficiency_%"] = (df["Achieved"] / df["Target"] * 100).round(1)
        df["Earned_Rs"]    = (df["Achieved"] * df["Rate_Rs"]).round(2)
        df["Date"]         = pd.to_datetime(df["Date"])

        f1, f2 = st.columns(2)
        with f1:
            date_range = st.date_input("Date Range",
                value=[date.today() - timedelta(days=7), date.today()])
        with f2:
            style_filter = st.multiselect("Filter Style",
                df["Style"].unique().tolist(), default=df["Style"].unique().tolist())

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
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Efficiency",  f"{df_f['Efficiency_%'].mean():.1f}%")
            c2.metric("Total Earned",    f"Rs {df_f['Earned_Rs'].sum():,.0f}")
            c3.metric("Total Pieces",    f"{int(df_f['Achieved'].sum()):,}")
            st.markdown("---")

            st.markdown('<div class="section-title">Karigar-wise Efficiency</div>', unsafe_allow_html=True)
            karigar_eff = df_f.groupby("Karigar_Name").agg(
                Avg_Efficiency=("Efficiency_%","mean"),
                Total_Achieved=("Achieved","sum"),
                Total_Earned_Rs=("Earned_Rs","sum"),
                Ops_Done=("Operation","count")
            ).round(2).reset_index()
            karigar_eff["Grade"] = karigar_eff["Avg_Efficiency"].apply(
                lambda x: "A - Excellent" if x >= 100 else ("B - Good" if x >= 85 else ("C - Average" if x >= 70 else "D - Below Target"))
            )
            st.dataframe(karigar_eff, use_container_width=True, hide_index=True)

            st.markdown('<div class="section-title">Operation-wise Performance</div>', unsafe_allow_html=True)
            op_eff = df_f.groupby("Operation").agg(
                Avg_Efficiency=("Efficiency_%","mean"),
                Total_Achieved=("Achieved","sum"),
                Total_Cost_Rs=("Earned_Rs","sum")
            ).round(2).reset_index().sort_values("Avg_Efficiency")
            st.dataframe(op_eff, use_container_width=True, hide_index=True)
            bottleneck = op_eff[op_eff["Avg_Efficiency"] < 80]
            if not bottleneck.empty:
                st.warning(f"Bottleneck Operations (below 80%): {', '.join(bottleneck['Operation'].tolist())}")

            st.markdown('<div class="section-title">Style-wise Labour Costing</div>', unsafe_allow_html=True)
            style_cost = df_f.groupby(["Style","Operation"]).agg(
                Total_Pieces=("Achieved","sum"),
                Total_Cost_Rs=("Earned_Rs","sum")
            ).reset_index()
            st.dataframe(style_cost, use_container_width=True, hide_index=True)

            total_by_style = style_cost.groupby("Style")["Total_Cost_Rs"].sum().reset_index()
            total_by_style.columns = ["Style","Total_Labour_Cost_Rs"]
            st.dataframe(total_by_style, use_container_width=True, hide_index=True)

            ex1, ex2 = st.columns(2)
            with ex1:
                st.download_button("📥 Export Efficiency Report (Excel)",
                    data=df_to_excel_bytes(karigar_eff),
                    file_name="efficiency_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with ex2:
                st.download_button("📥 Export Efficiency Report (CSV)",
                    data=df_to_csv_bytes(karigar_eff),
                    file_name="efficiency_report.csv", mime="text/csv")


# ════════════════════════════════════════════════════════════
# TAB 6 – PAYROLL CALCULATOR
# ════════════════════════════════════════════════════════════
with tab_payroll:
    st.markdown('<div class="section-title">💰 Karigar Payroll Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Pays the higher of piece-rate earned vs daily rate guarantee. 5% bonus if karigar earns more than 120% of guaranteed pay.</div>', unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1: pay_start = st.date_input("Pay Period Start", value=date.today() - timedelta(days=6))
    with p2: pay_end   = st.date_input("Pay Period End",   value=date.today())

    if st.button("Calculate Payroll", use_container_width=True):
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
                days = (pay_end - pay_start).days + 1
                payroll = df_pay.groupby("Karigar_ID").agg(
                    Total_Piece_Earned=("Piece_Earned","sum"),
                    Total_Pieces=("Achieved","sum")
                ).reset_index()
                km = st.session_state.karigar_master[["Karigar_ID","Name","Daily_Rate_Rs"]]
                payroll = payroll.merge(km, on="Karigar_ID", how="left")
                payroll["Guaranteed_Pay"]   = payroll["Daily_Rate_Rs"] * days
                payroll["Final_Pay_Rs"]     = payroll[["Total_Piece_Earned","Guaranteed_Pay"]].max(axis=1)
                payroll["Pay_Basis"]        = payroll.apply(
                    lambda r: "Piece-rate" if r["Total_Piece_Earned"] >= r["Guaranteed_Pay"] else "Daily-rate", axis=1
                )
                payroll["Efficiency_Bonus"] = 0.0
                payroll.loc[
                    payroll["Total_Piece_Earned"] > payroll["Guaranteed_Pay"] * 1.2,
                    "Efficiency_Bonus"
                ] = payroll["Final_Pay_Rs"] * 0.05
                payroll["Total_with_Bonus"] = payroll["Final_Pay_Rs"] + payroll["Efficiency_Bonus"]

                disp = payroll[["Name","Total_Pieces","Total_Piece_Earned","Guaranteed_Pay",
                                "Final_Pay_Rs","Efficiency_Bonus","Total_with_Bonus","Pay_Basis"]].round(2)
                st.dataframe(disp, use_container_width=True, hide_index=True)
                st.metric("Total Payroll", f"Rs {disp['Total_with_Bonus'].sum():,.2f}")

                ex1, ex2 = st.columns(2)
                with ex1:
                    st.download_button("📥 Download Payroll (Excel)",
                        data=df_to_excel_bytes(disp),
                        file_name=f"payroll_{pay_start}_{pay_end}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with ex2:
                    st.download_button("📥 Download Payroll (CSV)",
                        data=df_to_csv_bytes(disp),
                        file_name=f"payroll_{pay_start}_{pay_end}.csv", mime="text/csv")


# ════════════════════════════════════════════════════════════
# TAB 7 – MASTER DATA
# ════════════════════════════════════════════════════════════
with tab_master:
    st.markdown('<div class="section-title">⚙️ Master Data Management</div>', unsafe_allow_html=True)
    m1, m2 = st.tabs(["👗 Style-Operation Master", "👷 Karigar Master"])

    with m1:
        st.markdown('<div class="section-title">Style Operations, Targets and Rates</div>', unsafe_allow_html=True)

        import_section(
            key="style_master",
            required_cols=["Style","Operation","Target","Rate_Rs"],
            session_key="style_master",
            template_df=TEMPLATES["style_master"],
            label="Style-Operation Master"
        )

        with st.expander("➕ Add Operation Manually"):
            with st.form("style_op_form", clear_on_submit=True):
                s1, s2 = st.columns(2)
                with s1:
                    new_style  = st.text_input("Style Code")
                    new_op     = st.text_input("Operation Name")
                with s2:
                    new_target = st.number_input("Daily Target (pcs)", min_value=1, step=1)
                    new_rate   = st.number_input("Rate/Piece (Rs)", min_value=0.0, step=0.25, format="%.2f")
                if st.form_submit_button("Add") and new_style and new_op:
                    st.session_state.style_master = pd.concat(
                        [st.session_state.style_master,
                         pd.DataFrame([{"Style": new_style, "Operation": new_op,
                                        "Target": new_target, "Rate_Rs": new_rate}])],
                        ignore_index=True
                    )
                    st.success(f"Added {new_op} for {new_style}")

        st.dataframe(st.session_state.style_master, use_container_width=True, hide_index=True)

        style_summary = st.session_state.style_master.groupby("Style").agg(
            Total_Operations=("Operation","count"),
            Total_Rate_Per_Garment=("Rate_Rs","sum"),
            Slowest_Operation_Target=("Target","min")
        ).reset_index()
        st.markdown('<div class="section-title">Style Summary</div>', unsafe_allow_html=True)
        st.dataframe(style_summary, use_container_width=True, hide_index=True)

        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button("📥 Export Style Master (Excel)",
                data=df_to_excel_bytes(st.session_state.style_master),
                file_name="style_master.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with ex2:
            st.download_button("📥 Export Style Master (CSV)",
                data=df_to_csv_bytes(st.session_state.style_master),
                file_name="style_master.csv", mime="text/csv")

    with m2:
        st.markdown('<div class="section-title">Karigar Register</div>', unsafe_allow_html=True)

        import_section(
            key="karigar_master",
            required_cols=["Karigar_ID","Name","Skill","Daily_Rate_Rs"],
            session_key="karigar_master",
            template_df=TEMPLATES["karigar_master"],
            label="Karigar Master"
        )

        with st.expander("➕ Add Karigar Manually"):
            with st.form("karigar_form", clear_on_submit=True):
                k1, k2 = st.columns(2)
                with k1:
                    k_id   = st.text_input("Karigar ID (e.g. K006)")
                    k_name = st.text_input("Full Name")
                with k2:
                    k_skill = st.selectbox("Skill", ["Stitching","Cutting","Finishing","Hemming","Checking","General"])
                    k_rate  = st.number_input("Daily Rate (Rs)", min_value=100, step=10)
                if st.form_submit_button("Add Karigar") and k_id and k_name:
                    st.session_state.karigar_master = pd.concat(
                        [st.session_state.karigar_master,
                         pd.DataFrame([{"Karigar_ID": k_id, "Name": k_name,
                                        "Skill": k_skill, "Daily_Rate_Rs": k_rate}])],
                        ignore_index=True
                    )
                    st.success(f"{k_name} added!")

        st.dataframe(st.session_state.karigar_master, use_container_width=True, hide_index=True)

        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button("📥 Export Karigar Master (Excel)",
                data=df_to_excel_bytes(st.session_state.karigar_master),
                file_name="karigar_master.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with ex2:
            st.download_button("📥 Export Karigar Master (CSV)",
                data=df_to_csv_bytes(st.session_state.karigar_master),
                file_name="karigar_master.csv", mime="text/csv")

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#aaa; font-size:0.8rem;'>🧵 Stitching Costing Interface - Karigar Management System - Excel/CSV Import and Export</center>",
    unsafe_allow_html=True
)
