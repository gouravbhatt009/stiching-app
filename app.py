import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stitching Cost Pro", layout="wide", page_icon="🧵")

# --- APP STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #e0e0e0; padding: 10px; border-radius: 8px; background-color: white; }
    </style>
    """, unsafe_base64=True)

# --- CALCULATIONS ENGINE ---
def calculate_costing(hourly_rate, target_per_hour, overhead_pc):
    # Cost per minute = Hourly Wage / 60
    cpm = hourly_rate / 60
    # Actual Labor Cost per Piece
    labor_cost_pc = hourly_rate / target_per_hour
    # Total Cost including Overhead
    total_cost_pc = labor_cost_pc * (1 + (overhead_pc / 100))
    return round(labor_cost_pc, 2), round(total_cost_pc, 2)

# --- NAVIGATION ---
st.sidebar.title("🧵 Stitching Ops")
tab = st.sidebar.radio("Select Module", ["Costing Calculator", "Production & SKU Analytics", "Style BOM & Processes"])

# --- TAB 1: COSTING CALCULATOR ---
if tab == "Costing Calculator":
    st.title("💰 Unit Costing Engine")
    st.info("Calculate the accrued cost per SKU based on labor rates and overheads.")
    
    col1, col2 = st.columns(2)
    with col1:
        sku_name = st.text_input("Style / SKU Name", "SKU-99")
        emp_rate = st.number_input("Employee Hourly Wage ($)", value=15.0)
        target_hr = st.number_input("Target Units per Hour", value=10)
    
    with col2:
        overhead = st.slider("Factory Overhead %", 0, 100, 20)
        sam = st.number_input("SAM (Standard Allowed Minutes)", value=6.0)

    l_cost, t_cost = calculate_costing(emp_rate, target_hr, overhead)
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Labor Cost / Piece", f"${l_cost}")
    m2.metric("Total Accrued Cost / Piece", f"${t_cost}")
    m3.metric("Cost per Minute (CPM)", f"${round(emp_rate/60, 3)}")

# --- TAB 2: SKU ANALYTICS & PRODUCTIVITY ---
elif tab == "Production & SKU Analytics":
    st.title("📊 Monthly Productivity & Demand")
    
    # Mock Data for Productivity
    data = {
        'SKU': ['SKU-001', 'SKU-002', 'SKU-003', 'SKU-001', 'SKU-002'],
        'Actual_Units': [450, 300, 150, 500, 280],
        'Target_Units': [500, 350, 200, 500, 350],
        'Actual_Cost': [1200, 900, 500, 1300, 850],
        'Accrued_Cost': [1100, 950, 550, 1100, 950]
    }
    df = pd.DataFrame(data)
    
    # Productivity Identify
    df['Efficiency_%'] = (df['Actual_Units'] / df['Target_Units']) * 100
    high_demand_sku = df.groupby('SKU')['Actual_Units'].sum().idxmax()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Key Findings")
        st.success(f"🔥 **Highest Demand SKU:** {high_demand_sku}")
        st.warning(f"📉 **Avg Productivity:** {round(df['Efficiency_%'].mean(), 1)}%")
    
    with col2:
        fig = px.bar(df, x='SKU', y='Actual_Units', title="Units Produced by SKU", color='SKU')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Cost Variance (Actual vs Accrued)")
    fig_cost = px.line(df, y=['Actual_Cost', 'Accrued_Cost'], markers=True, title="Cost Deviation Trend")
    st.plotly_chart(fig_cost, use_container_width=True)

# --- TAB 3: STYLE BOM & PROCESS ---
elif tab == "Style BOM & Processes":
    st.title("📋 Process Bill of Materials (BOM)")
    
    sku_select = st.selectbox("Select Style to view Process Flow", ["SKU-001 (Shirt)", "SKU-002 (Pants)"])
    
    if "Shirt" in sku_select:
        processes = [
            {"Step": 1, "Operation": "Collar Stitching", "Machine": "Single Needle", "Time (Sec)": 45},
            {"Step": 2, "Operation": "Cuff Attachment", "Machine": "Single Needle", "Time (Sec)": 60},
            {"Step": 3, "Operation": "Side Seam", "Machine": "Overlock", "Time (Sec)": 120},
            {"Step": 4, "Operation": "Button Hole", "Machine": "Button Hole M/C", "Time (Sec)": 30}
        ]
    else:
        processes = [
            {"Step": 1, "Operation": "Pocket Attachment", "Machine": "Single Needle", "Time (Sec)": 90},
            {"Step": 2, "Operation": "Inseam", "Machine": "Feed-off-the-arm", "Time (Sec)": 150},
            {"Step": 3, "Operation": "Waistband", "Machine": "Kansai Special", "Time (Sec)": 80}
        ]
    
    st.table(pd.DataFrame(processes))
    
    
    
    st.markdown("---")
    st.caption("Author: Gourav Bhatt | Stitching Costing Playbook v2.0")
