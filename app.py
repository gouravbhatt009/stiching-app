import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import json
import io

# Page configuration
st.set_page_config(
    page_title="Stitching Costing Interface",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .cost-summary {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'activities_data' not in st.session_state:
    st.session_state.activities_data = []
if 'sku_data' not in st.session_state:
    st.session_state.sku_data = []
if 'style_data' not in st.session_state:
    st.session_state.style_data = []
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = []

# Main title
st.markdown('<h1 class="main-header">🧵 Stitching Costing Interface</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", [
    "Dashboard",
    "Activity Management",
    "SKU Management", 
    "Style Management",
    "Workflow Analysis",
    "Cost Calculator",
    "Reports & Analytics"
])

# Sample data initialization
def initialize_sample_data():
    if not st.session_state.activities_data:
        st.session_state.activities_data = [
            {"Activity": "Cutting", "Labor_Cost_Per_Hour": 15.0, "Machine_Cost_Per_Hour": 8.0, "Time_Minutes": 45, "Skill_Level": "Medium"},
            {"Activity": "Sewing", "Labor_Cost_Per_Hour": 18.0, "Machine_Cost_Per_Hour": 12.0, "Time_Minutes": 90, "Skill_Level": "High"},
            {"Activity": "Pressing", "Labor_Cost_Per_Hour": 12.0, "Machine_Cost_Per_Hour": 5.0, "Time_Minutes": 15, "Skill_Level": "Low"},
            {"Activity": "Quality Check", "Labor_Cost_Per_Hour": 20.0, "Machine_Cost_Per_Hour": 3.0, "Time_Minutes": 10, "Skill_Level": "High"},
            {"Activity": "Packaging", "Labor_Cost_Per_Hour": 10.0, "Machine_Cost_Per_Hour": 2.0, "Time_Minutes": 20, "Skill_Level": "Low"},
        ]
    
    if not st.session_state.sku_data:
        st.session_state.sku_data = [
            {"SKU": "SKU001", "Product_Name": "Cotton T-Shirt", "Size": "M", "Color": "Blue", "Material_Cost": 8.50, "Target_Margin": 0.40},
            {"SKU": "SKU002", "Product_Name": "Polo Shirt", "Size": "L", "Color": "White", "Material_Cost": 12.00, "Target_Margin": 0.45},
            {"SKU": "SKU003", "Product_Name": "Hoodie", "Size": "XL", "Color": "Black", "Material_Cost": 18.00, "Target_Margin": 0.50},
            {"SKU": "SKU004", "Product_Name": "Jeans", "Size": "32", "Color": "Blue", "Material_Cost": 22.00, "Target_Margin": 0.55},
            {"SKU": "SKU005", "Product_Name": "Dress Shirt", "Size": "M", "Color": "White", "Material_Cost": 15.00, "Target_Margin": 0.48},
        ]
    
    if not st.session_state.style_data:
        st.session_state.style_data = [
            {"Style": "CASUAL001", "Style_Name": "Basic Casual", "Complexity": "Low", "Activities": ["Cutting", "Sewing", "Pressing", "Packaging"]},
            {"Style": "FORMAL001", "Style_Name": "Business Formal", "Complexity": "High", "Activities": ["Cutting", "Sewing", "Pressing", "Quality Check", "Packaging"]},
            {"Style": "SPORT001", "Style_Name": "Athletic Wear", "Complexity": "Medium", "Activities": ["Cutting", "Sewing", "Quality Check", "Packaging"]},
        ]

initialize_sample_data()

# Dashboard Page
if page == "Dashboard":
    st.markdown('<h2 class="sub-header">Dashboard Overview</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_activities = len(st.session_state.activities_data)
        st.metric("Total Activities", total_activities, "2 new this week")
    
    with col2:
        total_skus = len(st.session_state.sku_data)
        st.metric("Active SKUs", total_skus, "5 updated")
    
    with col3:
        total_styles = len(st.session_state.style_data)
        st.metric("Style Categories", total_styles, "1 new")
    
    with col4:
        if st.session_state.activities_data:
            avg_labor_cost = np.mean([item['Labor_Cost_Per_Hour'] for item in st.session_state.activities_data])
            st.metric("Avg Labor Cost/Hr", f"${avg_labor_cost:.2f}", "-2.5%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.activities_data:
            df_activities = pd.DataFrame(st.session_state.activities_data)
            fig = px.bar(df_activities, x='Activity', y='Labor_Cost_Per_Hour', 
                        title='Labor Cost by Activity', color='Skill_Level')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.session_state.sku_data:
            df_sku = pd.DataFrame(st.session_state.sku_data)
            fig = px.pie(df_sku, values='Material_Cost', names='Product_Name', 
                        title='Material Cost Distribution')
            st.plotly_chart(fig, use_container_width=True)

# Activity Management Page
elif page == "Activity Management":
    st.markdown('<h2 class="sub-header">Activity Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View Activities", "Add/Edit Activity"])
    
    with tab1:
        if st.session_state.activities_data:
            df = pd.DataFrame(st.session_state.activities_data)
            st.dataframe(df, use_container_width=True)
            
            # Activity analysis
            st.subheader("Activity Analysis")
            df['Total_Cost_Per_Hour'] = df['Labor_Cost_Per_Hour'] + df['Machine_Cost_Per_Hour']
            df['Cost_Per_Minute'] = df['Total_Cost_Per_Hour'] / 60
            df['Activity_Total_Cost'] = df['Cost_Per_Minute'] * df['Time_Minutes']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.scatter(df, x='Time_Minutes', y='Activity_Total_Cost', 
                               color='Skill_Level', size='Total_Cost_Per_Hour',
                               title='Time vs Cost Analysis')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df, x='Activity', y='Activity_Total_Cost', 
                           title='Total Cost by Activity', color='Skill_Level')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Add New Activity")
        with st.form("activity_form"):
            col1, col2 = st.columns(2)
            with col1:
                activity_name = st.text_input("Activity Name")
                labor_cost = st.number_input("Labor Cost per Hour ($)", min_value=0.0, step=0.5)
                machine_cost = st.number_input("Machine Cost per Hour ($)", min_value=0.0, step=0.5)
            
            with col2:
                time_minutes = st.number_input("Time Required (minutes)", min_value=1, step=1)
                skill_level = st.selectbox("Skill Level", ["Low", "Medium", "High"])
            
            if st.form_submit_button("Add Activity"):
                new_activity = {
                    "Activity": activity_name,
                    "Labor_Cost_Per_Hour": labor_cost,
                    "Machine_Cost_Per_Hour": machine_cost,
                    "Time_Minutes": time_minutes,
                    "Skill_Level": skill_level
                }
                st.session_state.activities_data.append(new_activity)
                st.success("Activity added successfully!")
                st.rerun()

# SKU Management Page
elif page == "SKU Management":
    st.markdown('<h2 class="sub-header">SKU Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View SKUs", "Add/Edit SKU"])
    
    with tab1:
        if st.session_state.sku_data:
            df = pd.DataFrame(st.session_state.sku_data)
            st.dataframe(df, use_container_width=True)
            
            # SKU analysis
            st.subheader("SKU Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(df, x='Material_Cost', nbins=10, 
                                 title='Material Cost Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(df, x='Material_Cost', y='Target_Margin', 
                               color='Product_Name', size='Material_Cost',
                               title='Material Cost vs Target Margin')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Add New SKU")
        with st.form("sku_form"):
            col1, col2 = st.columns(2)
            with col1:
                sku_code = st.text_input("SKU Code")
                product_name = st.text_input("Product Name")
                size = st.text_input("Size")
            
            with col2:
                color = st.text_input("Color")
                material_cost = st.number_input("Material Cost ($)", min_value=0.0, step=0.1)
                target_margin = st.number_input("Target Margin (%)", min_value=0.0, max_value=1.0, step=0.05)
            
            if st.form_submit_button("Add SKU"):
                new_sku = {
                    "SKU": sku_code,
                    "Product_Name": product_name,
                    "Size": size,
                    "Color": color,
                    "Material_Cost": material_cost,
                    "Target_Margin": target_margin
                }
                st.session_state.sku_data.append(new_sku)
                st.success("SKU added successfully!")
                st.rerun()

# Style Management Page
elif page == "Style Management":
    st.markdown('<h2 class="sub-header">Style Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View Styles", "Add/Edit Style"])
    
    with tab1:
        if st.session_state.style_data:
            for style in st.session_state.style_data:
                with st.expander(f"{style['Style']} - {style['Style_Name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Complexity:** {style['Complexity']}")
                    with col2:
                        st.write(f"**Activities:** {', '.join(style['Activities'])}")
    
    with tab2:
        st.subheader("Add New Style")
        with st.form("style_form"):
            style_code = st.text_input("Style Code")
            style_name = st.text_input("Style Name")
            complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])
            
            available_activities = [item['Activity'] for item in st.session_state.activities_data]
            selected_activities = st.multiselect("Select Activities", available_activities)
            
            if st.form_submit_button("Add Style"):
                new_style = {
                    "Style": style_code,
                    "Style_Name": style_name,
                    "Complexity": complexity,
                    "Activities": selected_activities
                }
                st.session_state.style_data.append(new_style)
                st.success("Style added successfully!")
                st.rerun()

# Workflow Analysis Page
elif page == "Workflow Analysis":
    st.markdown('<h2 class="sub-header">Workflow Analysis</h2>', unsafe_allow_html=True)
    
    if st.session_state.style_data and st.session_state.activities_data:
        # Select style for workflow analysis
        style_options = [f"{s['Style']} - {s['Style_Name']}" for s in st.session_state.style_data]
        selected_style = st.selectbox("Select Style for Analysis", style_options)
        
        if selected_style:
            style_code = selected_style.split(" - ")[0]
            style_info = next(s for s in st.session_state.style_data if s['Style'] == style_code)
            
            st.subheader(f"Workflow for {style_info['Style_Name']}")
            
            # Create workflow dataframe
            workflow_activities = []
            total_time = 0
            total_cost = 0
            
            for activity_name in style_info['Activities']:
                activity_info = next((a for a in st.session_state.activities_data if a['Activity'] == activity_name), None)
                if activity_info:
                    cost_per_minute = (activity_info['Labor_Cost_Per_Hour'] + activity_info['Machine_Cost_Per_Hour']) / 60
                    activity_cost = cost_per_minute * activity_info['Time_Minutes']
                    total_time += activity_info['Time_Minutes']
                    total_cost += activity_cost
                    
                    workflow_activities.append({
                        'Activity': activity_name,
                        'Time (min)': activity_info['Time_Minutes'],
                        'Cost per Hour': activity_info['Labor_Cost_Per_Hour'] + activity_info['Machine_Cost_Per_Hour'],
                        'Activity Cost': activity_cost,
                        'Skill Level': activity_info['Skill_Level'],
                        'Cumulative Time': total_time,
                        'Cumulative Cost': total_cost
                    })
            
            if workflow_activities:
                df_workflow = pd.DataFrame(workflow_activities)
                
                # Display workflow table
                st.dataframe(df_workflow, use_container_width=True)
                
                # Workflow metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Time", f"{total_time} min")
                with col2:
                    st.metric("Total Cost", f"${total_cost:.2f}")
                with col3:
                    st.metric("Avg Cost/Min", f"${total_cost/total_time:.2f}")
                with col4:
                    efficiency = 100 - (total_time * 0.1)  # Example efficiency calculation
                    st.metric("Efficiency", f"{efficiency:.1f}%")
                
                # Workflow visualization
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(df_workflow, x='Activity', y='Time (min)', 
                               color='Skill Level', title='Time per Activity')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.line(df_workflow, x='Activity', y='Cumulative Cost', 
                                title='Cumulative Cost Progression')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Process flow chart
                st.subheader("Process Flow")
                flow_chart_data = []
                for i, activity in enumerate(workflow_activities):
                    flow_chart_data.append(f"{i+1}. {activity['Activity']} ({activity['Time (min)']} min)")
                
                st.text(" → ".join([act.split('.')[1].strip() for act in flow_chart_data]))

# Cost Calculator Page
elif page == "Cost Calculator":
    st.markdown('<h2 class="sub-header">Cost Calculator</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Select Configuration")
        
        # Select SKU
        sku_options = [f"{s['SKU']} - {s['Product_Name']}" for s in st.session_state.sku_data]
        selected_sku = st.selectbox("Select SKU", sku_options)
        
        # Select Style
        style_options = [f"{s['Style']} - {s['Style_Name']}" for s in st.session_state.style_data]
        selected_style = st.selectbox("Select Style", style_options)
        
        # Production quantity
        quantity = st.number_input("Production Quantity", min_value=1, value=100, step=10)
        
        # Additional costs
        overhead_rate = st.slider("Overhead Rate (%)", 0, 50, 15) / 100
        waste_factor = st.slider("Waste Factor (%)", 0, 20, 5) / 100
    
    with col2:
        st.subheader("Cost Breakdown")
        
        if selected_sku and selected_style:
            # Get SKU and Style info
            sku_code = selected_sku.split(" - ")[0]
            style_code = selected_style.split(" - ")[0]
            
            sku_info = next(s for s in st.session_state.sku_data if s['SKU'] == sku_code)
            style_info = next(s for s in st.session_state.style_data if s['Style'] == style_code)
            
            # Calculate costs
            material_cost = sku_info['Material_Cost']
            
            # Calculate stitching cost
            stitching_cost = 0
            for activity_name in style_info['Activities']:
                activity_info = next((a for a in st.session_state.activities_data if a['Activity'] == activity_name), None)
                if activity_info:
                    cost_per_minute = (activity_info['Labor_Cost_Per_Hour'] + activity_info['Machine_Cost_Per_Hour']) / 60
                    activity_cost = cost_per_minute * activity_info['Time_Minutes']
                    stitching_cost += activity_cost
            
            # Apply waste factor
            adjusted_material_cost = material_cost * (1 + waste_factor)
            
            # Calculate overhead
            direct_cost = adjusted_material_cost + stitching_cost
            overhead_cost = direct_cost * overhead_rate
            
            # Total unit cost
            total_unit_cost = direct_cost + overhead_cost
            
            # Target selling price
            target_margin = sku_info['Target_Margin']
            target_selling_price = total_unit_cost / (1 - target_margin)
            
            # Display costs
            st.markdown('<div class="cost-summary">', unsafe_allow_html=True)
            st.write(f"**Material Cost:** ${adjusted_material_cost:.2f}")
            st.write(f"**Stitching Cost:** ${stitching_cost:.2f}")
            st.write(f"**Overhead Cost:** ${overhead_cost:.2f}")
            st.write(f"**Total Unit Cost:** ${total_unit_cost:.2f}")
            st.write(f"**Target Selling Price:** ${target_selling_price:.2f}")
            st.write(f"**Profit Margin:** ${target_selling_price - total_unit_cost:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Batch calculations
            st.subheader(f"Batch Analysis (Quantity: {quantity})")
            total_batch_cost = total_unit_cost * quantity
            total_revenue = target_selling_price * quantity
            total_profit = total_revenue - total_batch_cost
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Cost", f"${total_batch_cost:,.2f}")
            with col_b:
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col_c:
                st.metric("Total Profit", f"${total_profit:,.2f}")
            
            # Cost breakdown chart
            cost_breakdown = {
                'Material': adjusted_material_cost,
                'Stitching': stitching_cost,
                'Overhead': overhead_cost
            }
            
            fig = px.pie(values=list(cost_breakdown.values()), 
                        names=list(cost_breakdown.keys()),
                        title='Cost Breakdown')
            st.plotly_chart(fig, use_container_width=True)

# Reports & Analytics Page
elif page == "Reports & Analytics":
    st.markdown('<h2 class="sub-header">Reports & Analytics</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Activity Report", "Profitability Analysis", "Efficiency Metrics"])
    
    with tab1:
        st.subheader("Activity Performance Report")
        if st.session_state.activities_data:
            df_activities = pd.DataFrame(st.session_state.activities_data)
            
            # Calculate efficiency metrics
            df_activities['Cost_Per_Minute'] = (df_activities['Labor_Cost_Per_Hour'] + df_activities['Machine_Cost_Per_Hour']) / 60
            df_activities['Total_Activity_Cost'] = df_activities['Cost_Per_Minute'] * df_activities['Time_Minutes']
            df_activities['Efficiency_Score'] = 100 / df_activities['Time_Minutes']  # Inverse relationship
            
            # Display enhanced table
            display_df = df_activities[['Activity', 'Time_Minutes', 'Total_Activity_Cost', 'Skill_Level', 'Efficiency_Score']]
            st.dataframe(display_df, use_container_width=True)
            
            # Activity comparison charts
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df_activities, x='Activity', y='Efficiency_Score', 
                           color='Skill_Level', title='Activity Efficiency Scores')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(df_activities, x='Time_Minutes', y='Total_Activity_Cost',
                               color='Skill_Level', size='Efficiency_Score',
                               title='Time vs Cost Analysis')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Profitability Analysis")
        if st.session_state.sku_data:
            df_sku = pd.DataFrame(st.session_state.sku_data)
            
            # Calculate profitability metrics
            df_sku['Break_Even_Price'] = df_sku['Material_Cost'] / (1 - df_sku['Target_Margin'])
            df_sku['Profit_Per_Unit'] = df_sku['Break_Even_Price'] - df_sku['Material_Cost']
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df_sku, x='Product_Name', y='Profit_Per_Unit',
                           color='Target_Margin', title='Profit per Unit by Product')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(df_sku, x='Material_Cost', y='Target_Margin',
                               size='Profit_Per_Unit', color='Product_Name',
                               title='Material Cost vs Margin Analysis')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Efficiency Metrics")
        
        # Overall efficiency metrics
        if st.session_state.activities_data and st.session_state.style_data:
            
            # Calculate style efficiency
            style_efficiency = []
            for style in st.session_state.style_data:
                total_time = 0
                total_cost = 0
                activity_count = len(style['Activities'])
                
                for activity_name in style['Activities']:
                    activity = next((a for a in st.session_state.activities_data if a['Activity'] == activity_name), None)
                    if activity:
                        total_time += activity['Time_Minutes']
                        cost_per_minute = (activity['Labor_Cost_Per_Hour'] + activity['Machine_Cost_Per_Hour']) / 60
                        total_cost += cost_per_minute * activity['Time_Minutes']
                
                efficiency_score = (activity_count * 100) / total_time if total_time > 0 else 0
                
                style_efficiency.append({
                    'Style': style['Style_Name'],
                    'Total_Time': total_time,
                    'Total_Cost': total_cost,
                    'Activity_Count': activity_count,
                    'Efficiency_Score': efficiency_score,
                    'Complexity': style['Complexity']
                })
            
            if style_efficiency:
                df_efficiency = pd.DataFrame(style_efficiency)
                st.dataframe(df_efficiency, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(df_efficiency, x='Style', y='Efficiency_Score',
                               color='Complexity', title='Style Efficiency Comparison')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.scatter(df_efficiency, x='Total_Time', y='Total_Cost',
                                   size='Efficiency_Score', color='Complexity',
                                   title='Time vs Cost Efficiency Analysis')
                    st.plotly_chart(fig, use_container_width=True)

# Export functionality
st.sidebar.markdown("---")
st.sidebar.subheader("Data Export")

if st.sidebar.button("Export All Data"):
    # Prepare data for export
    export_data = {
        'activities': st.session_state.activities_data,
        'skus': st.session_state.sku_data,
        'styles': st.session_state.style_data,
        'export_timestamp': datetime.datetime.now().isoformat()
    }
    
    # Convert to JSON
    json_string = json.dumps(export_data, indent=2)
    
    # Create download
    st.sidebar.download_button(
        label="Download JSON",
        data=json_string,
        file_name=f"stitching_costing_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>Stitching Costing Interface v1.0 | Built with Streamlit | © 2024 Textile Solutions</p>
</div>
""", unsafe_allow_html=True)
