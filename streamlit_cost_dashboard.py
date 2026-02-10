# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# 1️⃣ Load Data
# --------------------------
# Example CSV files
# styles.csv: style_id, style_name, created_date, style_cost
# salary.csv: style_id, worker_name, hours_worked, pay_rate
# master.csv: style_id, material_cost, process_cost, operation_cost

@st.cache_data
def load_data():
    styles = pd.read_csv("styles.csv", parse_dates=['created_date'])
    salary = pd.read_csv("salary.csv")
    master = pd.read_csv("master.csv")
    return styles, salary, master

styles, salary, master = load_data()

# --------------------------
# 2️⃣ Sidebar Filters
# --------------------------
st.sidebar.header("Filters")

# Date filter
min_date = styles['created_date'].min()
max_date = styles['created_date'].max()
date_range = st.sidebar.date_input("Select Creation Date Range", [min_date, max_date])

# Cost filter
min_cost = float(styles['style_cost'].min())
max_cost = float(styles['style_cost'].max())
cost_range = st.sidebar.slider("Style Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))

# Apply filters
filtered_styles = styles[
    (styles['created_date'] >= pd.to_datetime(date_range[0])) &
    (styles['created_date'] <= pd.to_datetime(date_range[1])) &
    (styles['style_cost'] >= cost_range[0]) &
    (styles['style_cost'] <= cost_range[1])
]

st.title("🧵 Style Costing Dashboard")

# --------------------------
# 3️⃣ Graphical Overview
# --------------------------
st.subheader("Style Cost Overview")

# Scatter plot: Creation Date vs Cost
fig = px.scatter(
    filtered_styles,
    x='created_date',
    y='style_cost',
    color='style_cost',
    hover_data=['style_name', 'style_cost'],
    color_continuous_scale='Viridis',
    title="Styles Over Time with Costs"
)
st.plotly_chart(fig, use_container_width=True)

# Low-cost highlight
low_cost_threshold = st.sidebar.number_input("Highlight Low-Cost Styles Below", min_value=min_cost, max_value=max_cost, value=min_cost + (max_cost-min_cost)/3)
low_cost_styles = filtered_styles[filtered_styles['style_cost'] < low_cost_threshold]

st.markdown(f"### 🔹 Low-Cost Styles (< {low_cost_threshold})")
st.dataframe(low_cost_styles[['style_name', 'style_cost', 'created_date']])

# --------------------------
# 4️⃣ Drill-down per Style
# --------------------------
st.subheader("Drill-Down Per Style")

style_select = st.selectbox("Select Style", filtered_styles['style_name'])

if style_select:
    style_row = filtered_styles[filtered_styles['style_name'] == style_select].iloc[0]
    style_id = style_row['style_id']

    st.markdown(f"### Style: {style_select} | Cost: {style_row['style_cost']} | Created: {style_row['created_date'].date()}")

    # Worker Salary Sheet
    st.markdown("#### 👷 Worker Salary Sheet")
    style_salary = salary[salary['style_id'] == style_id]
    style_salary['total_pay'] = style_salary['hours_worked'] * style_salary['pay_rate']
    st.dataframe(style_salary[['worker_name', 'hours_worked', 'pay_rate', 'total_pay']])

    # Master Sheet
    st.markdown("#### 📋 Master Sheet Entries")
    style_master = master[master['style_id'] == style_id]
    st.dataframe(style_master)

    # Cost breakdown chart
    st.markdown("#### 📊 Cost Breakdown")
    if not style_master.empty:
        cost_components = style_master[['material_cost', 'process_cost', 'operation_cost']].sum()
        fig2 = px.pie(
            names=cost_components.index,
            values=cost_components.values,
            title=f"Cost Breakdown for {style_select}"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Time monitoring
    st.markdown("#### ⏱ Time Per Step")
    if 'hours_worked' in style_salary.columns:
        fig3 = px.bar(style_salary, x='worker_name', y='hours_worked', title="Hours Worked by Each Worker")
        st.plotly_chart(fig3, use_container_width=True)

# --------------------------
# 5️⃣ Export / Download
# --------------------------
st.subheader("Export / Print Options")
st.markdown("You can download filtered style data as CSV for audit purposes.")
csv = filtered_styles.to_csv(index=False)
st.download_button(label="Download Filtered Data", data=csv, file_name='filtered_styles.csv', mime='text/csv')