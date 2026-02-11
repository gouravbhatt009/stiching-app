import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stitching Costing Analytics", layout="wide")

# --- CUSTOM CSS FOR ATTRACTION ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_base64=True)

# --- MOCK DATA GENERATION (Replace with your Excel upload logic later) ---
def load_data():
    employees = pd.DataFrame({
        'Employee': ['John D.', 'Sarah K.', 'Ahmed V.', 'Maria L.'],
        'Hourly_Rate': [15.0, 18.0, 14.5, 16.0],
        'Style_Assigned': ['SKU-001', 'SKU-002', 'SKU-001', 'SKU-003']
    })
    
    production = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'SKU': ['SKU-001', 'SKU-002', 'SKU-001', 'SKU-003', 'SKU-001', 'SKU-002', 'SKU-003', 'SKU-001', 'SKU-001', 'SKU-002'],
        'Actual_Units': [50, 40, 55, 30, 48, 42, 35, 60, 52, 38],
        'Target_Units': [60, 45, 60, 35, 60, 45, 35, 60, 60, 45],
        'Hours_Worked': [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
    })
    
    bom = {
        'SKU-001': ['Front Panel Stitching', 'Back Panel Attachment', 'Sleeve Hemming', 'Button Hole'],
        'SKU-002': ['Collar Prep', 'Cuff Stitching', 'Main Body Assembly', 'Final Inspection'],
        'SKU-003': ['Pocket Attachment', 'Side Seam', 'Elastic Waistband', 'Overlock']
    }
    return employees, production, bom

emp_df, prod_df, bom_data = load_data()

# --- SIDEBAR ---
st.sidebar.title("🧵 Factory Control")
menu = st.sidebar.radio("Dashboard Modules", ["Performance Overview", "Cost Variance Analysis", "Style BOM (Process)", "Employee Directory"])

# --- MODULE 1: PERFORMANCE OVERVIEW ---
if menu == "Performance Overview":
    st.title("📈 Production Productivity")
    
    # KPIs
    total_units = prod_df['Actual_Units'].sum()
    avg_efficiency = (prod_df['Actual_Units'].sum() / prod_df['Target_Units'].sum()) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Units (Monthly)", f"{total_units} pcs")
    col2.metric("Avg. Efficiency", f"{avg_efficiency:.1f}%")
    col3.metric("Top Demand SKU", prod_df.groupby('SKU')['Actual_Units'].sum().idxmax())

    # Productivity Chart
    st.subheader("Daily Production vs Target")
    fig = px.line(prod_df, x='Date', y=['Actual_Units', 'Target_Units'], color_discrete_map={"Actual_Units": "#1f77b4", "Target_Units": "#ff7f0e"})
    st.plotly_chart(fig, use_container_width=True)

# --- MODULE 2: COST VARIANCE ---
elif menu == "Cost Variance Analysis":
    st.title("💸 Actual vs. Accrued Cost")
    
    # Calculation Logic
    # Accrued = Hours * Rate
    # Let's merge employee rates with production SKU mapping
    cost_df = prod_df.merge(emp_df[['Style_Assigned', 'Hourly_Rate']], left_on='SKU', right_on='Style_Assigned')
    cost_df['Actual_Cost'] = cost_df['Hours_Worked'] * cost_df['Hourly_Rate']
    cost_df['Standard_Cost'] = (cost_df['Target_Units'] / cost_df['Actual_Units']) * cost_df['Actual_Cost'] # Simplified logic
    
    st.dataframe(cost_df[['Date', 'SKU', 'Actual_Cost', 'Standard_Cost']].style.highlight_max(axis=0))
    
    st.subheader("Cost Variance by Style")
    fig2 = px.bar(cost_df, x='SKU', y=['Actual_Cost', 'Standard_Cost'], barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

# --- MODULE 3: STYLE BOM (NEW TAB) ---
elif menu == "Style BOM (Process)":
    st.title("📋 Style Bill of Materials & Process")
    selected_sku = st.selectbox("Select SKU Style", list(bom_data.keys()))
    
    st.info(f"Showing manufacturing sequence for **{selected_sku}**")
    
    processes = bom_data[selected_sku]
    for i, step in enumerate(processes):
        st.write(f"**Step {i+1}:** {step}")
    
    st.image("https://via.placeholder.com/800x200.png?text=Process+Flow+Visual+Placeholder") # You can replace with real process diagrams

# --- MODULE 4: EMPLOYEE DIRECTORY ---
else:
    st.title("👥 Employee & Wages")
    st.table(emp_df)
