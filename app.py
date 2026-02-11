import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stitching Cost Pro", layout="wide", page_icon="🧵")

# --- DATA INITIALIZATION ---
# This ensures the app has data to show even before you upload a file
def get_mock_data():
    emp_data = pd.DataFrame({
        'Employee Name': ['Gourav', 'Amit', 'Suresh', 'Priya'],
        'Hourly Rate ($)': [15.0, 12.0, 14.0, 13.5],
        'Assigned SKU': ['SKU-001', 'SKU-002', 'SKU-001', 'SKU-003']
    })
    
    prod_data = pd.DataFrame({
        'SKU': ['SKU-001', 'SKU-002', 'SKU-003'],
        'Actual_Produced': [1200, 850, 600],
        'Target_Goal': [1300, 800, 700],
        'Material_Cost_Fixed': [2.50, 3.10, 2.80]
    })
    
    bom_data = {
        'SKU-001': [
            {'Step': 1, 'Process': 'Front Panel', 'Machine': 'Single Needle', 'Time(s)': 45},
            {'Step': 2, 'Process': 'Back Panel', 'Machine': 'Single Needle', 'Time(s)': 40},
            {'Step': 3, 'Process': 'Overlock Seam', 'Machine': '4-Thread Overlock', 'Time(s)': 90}
        ],
        'SKU-002': [
            {'Step': 1, 'Process': 'Collar Prep', 'Machine': 'Fusing M/c', 'Time(s)': 30},
            {'Step': 2, 'Process': 'Collar Attach', 'Machine': 'Single Needle', 'Time(s)': 120}
        ],
        'SKU-003': [
            {'Step': 1, 'Process': 'Pocket Stitch', 'Machine': 'Pattern Tacker', 'Time(s)': 60}
        ]
    }
    return emp_data, prod_data, bom_data

emp_df, prod_df, bom_dict = get_mock_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Factory Control Panel")
menu = st.sidebar.radio("Navigate to:", ["Dashboard", "Costing & Variance", "Style BOM (Process)", "Employee Wages"])

# --- 1. DASHBOARD (Productivity & Demand) ---
if menu == "Dashboard":
    st.title("📈 Production Productivity & Demand")
    
    # Identify High Demand (Based on Actual Production Volume)
    high_demand_sku = prod_df.loc[prod_df['Actual_Produced'].idxmax(), 'SKU']
    
    # Calculate Overall Productivity
    total_actual = prod_df['Actual_Produced'].sum()
    total_target = prod_df['Target_Goal'].sum()
    overall_efficiency = (total_actual / total_target) * 100 if total_target != 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Top Demand SKU", high_demand_sku)
    col2.metric("Overall Efficiency", f"{overall_efficiency:.1f}%")
    col3.metric("Total Monthly Units", f"{total_actual:,}")

    st.subheader("Monthly Production vs Target by Style")
    fig = px.bar(prod_df, x='SKU', y=['Actual_Produced', 'Target_Goal'], barmode='group', 
                 color_discrete_sequence=['#00CC96', '#EF553B'])
    st.plotly_chart(fig, use_container_width=True)

# --- 2. COSTING & VARIANCE ---
elif menu == "Costing & Variance":
    st.title("💸 Actual Cost vs Accrued Cost")
    
    # Logic: Merge Employee rates with Production to find costs
    # We calculate Labor Cost + Material Cost
    cost_summary = prod_df.copy()
    
    # Simplified calculation for the demo:
    # Accrued Cost = Target Costing | Actual Cost = Real spend based on efficiency
    cost_summary['Accrued_Cost_Unit'] = cost_summary['Material_Cost_Fixed'] + 1.50 # Adding base labor estimate
    cost_summary['Actual_Cost_Unit'] = cost_summary['Accrued_Cost_Unit'] * (cost_summary['Target_Goal'] / cost_summary['Actual_Produced'])

    st.write("### Variance Analysis Table")
    st.dataframe(cost_summary[['SKU', 'Actual_Produced', 'Accrued_Cost_Unit', 'Actual_Cost_Unit']].style.highlight_max(subset=['Actual_Cost_Unit'], color='#ffcccc'))

    st.subheader("Cost Deviation Analysis")
    fig2 = px.line(cost_summary, x='SKU', y=['Accrued_Cost_Unit', 'Actual_Cost_Unit'], markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# --- 3. STYLE BOM (PROCESS) ---
elif menu == "Style BOM (Process)":
    st.title("📋 SKU Bill of Materials & Process Flow")
    
    selected_sku = st.selectbox("Select SKU to view detailed process:", list(bom_dict.keys()))
    
    st.info(f"Manufacturing Workflow for **{selected_sku}**")
    
    df_bom = pd.DataFrame(bom_dict[selected_sku])
    st.table(df_bom)
    
    # Visualizing the workflow logic
    st.write("### Workflow Diagram")
    

# --- 4. EMPLOYEE WAGES ---
elif menu == "Employee Wages":
    st.title("👥 Employee Wages & SKU Assignment")
    
    # Calculate Monthly Wage (assuming 200 hours a month)
    emp_df['Est. Monthly Wage'] = emp_df['Hourly Rate ($)'] * 200
    
    st.dataframe(emp_df, use_container_width=True)
    
    st.write("### Wage Distribution per Hour")
    fig3 = px.pie(emp_df, values='Hourly Rate ($)', names='Employee Name', hole=0.4)
    st.plotly_chart(fig3, use_container_width=True)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("System Status: Online")
st.sidebar.caption("Author: Gourav Bhatt")
