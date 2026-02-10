import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Mock Data
data = pd.DataFrame({
    'Style': ['Classic Denim', 'Cotton Tee', 'Silk Scarf'],
    'Actual Cost': [450, 120, 890],
    'Master Cost': [420, 150, 850],
    'Created': ['2026-01-10', '2026-01-15', '2026-01-22']
})

# 2. Header
st.title("Style Costing & Reconciliation")

# 3. Dynamic Graph
fig = px.scatter(data, x="Created", y="Actual Cost", size="Actual Cost", color="Style", 
                 hover_name="Style", title="Cost Creation Timeline")
st.plotly_chart(fig, use_container_width=True)

# 4. Reconciliation Table
st.subheader("Cost Comparison")
data['Variance'] = data['Actual Cost'] - data['Master Cost']
st.table(data)

# 5. Drill-down (Simple Selection)
selected_style = st.selectbox("Select a Style for In-depth Reconciliation", data['Style'])

if selected_style:
    st.info(f"Showing details for {selected_style}")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Karigar Salary Sheet**")
        # Add your worker data here
    with col2:
        st.write("**Master Data Sheet**")
        # Add your master component data here
