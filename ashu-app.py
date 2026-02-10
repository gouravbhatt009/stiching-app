import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Mock Data (Expanded for better visualization)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Style': ['Classic Denim', 'Cotton Tee', 'Silk Scarf', 'Linen Shirt'],
        'Actual Cost': [450, 120, 890, 310],
        'Master Cost': [420, 150, 850, 315],
        'Created': pd.to_datetime(['2026-01-10', '2026-01-15', '2026-01-22', '2026-01-25'])
    })

df = st.session_state.data

# 2. Header & Top Level Metrics
st.title("🧵 Style Costing & Reconciliation")

# Calculate Variance
df['Variance'] = df['Actual Cost'] - df['Master Cost']
total_variance = df['Variance'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Total Actual Cost", f"₹{df['Actual Cost'].sum()}")
m2.metric("Total Master Cost", f"₹{df['Master Cost'].sum()}")
m3.metric("Net Variance", f"₹{total_variance}", delta=float(-total_variance), delta_color="inverse")

st.divider()

# 3. Dynamic Graph
fig = px.bar(df, x="Style", y=["Actual Cost", "Master Cost"], 
             barmode="group", title="Actual vs Master Cost Comparison",
             color_discrete_sequence=["#636EFA", "#EF553B"])
st.plotly_chart(fig, use_container_width=True)

# 4. Reconciliation Table with Conditional Formatting
st.subheader("📊 Cost Comparison Table")

def color_variance(val):
    color = 'red' if val > 0 else 'green' # Red if actual > master (Loss)
    return f'color: {color}'

# Displaying a styled dataframe instead of a static table
st.dataframe(df.style.applymap(color_variance, subset=['Variance']), use_container_width=True)

# 5. Drill-down (Detailed Reconciliation)
st.divider()
selected_style = st.selectbox("🔍 Select a Style for In-depth Reconciliation", df['Style'])

if selected_style:
    style_info = df[df['Style'] == selected_style].iloc[0]
    st.subheader(f"Detailed Analysis: {selected_style}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("👷 **Karigar Salary Sheet (Actuals)**")
        # Mocking detailed breakdown
        worker_data = pd.DataFrame({
            'Operation': ['Stitching', 'Overlock', 'Trimming'],
            'Worker': ['Ahmed', 'Suresh', 'Rahul'],
            'Rate': [style_info['Actual Cost'] * 0.6, style_info['Actual Cost'] * 0.3, style_info['Actual Cost'] * 0.1]
        })
        st.table(worker_data)
        st.write(f"**Total Paid:** ₹{worker_data['Rate'].sum()}")

    with col2:
        st.success("📝 **Master Data Sheet (Planned)**")
        master_breakdown = pd.DataFrame({
            'Component': ['Labor Target', 'Thread/Consumables', 'Buffer'],
            'Planned Cost': [style_info['Master Cost'] * 0.7, style_info['Master Cost'] * 0.2, style_info['Master Cost'] * 0.1]
        })
        st.table(master_breakdown)
        st.write(f"**Budgeted:** ₹{master_breakdown['Planned Cost'].sum()}")

    # Summary of Selection
    if style_info['Variance'] > 0:
        st.error(f"⚠️ This style is **₹{style_info['Variance']} over budget**. Check Stitching rates.")
    else:
        st.balloons()
        st.success(f"✅ This style is **₹{abs(style_info['Variance'])} under budget**.")
