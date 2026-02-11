import streamlit as st
import pandas as pd
import io

# --- 1. UI SETUP (Fixed Line 9 Error) ---
st.set_page_config(page_title="Intelligent Costing AI", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Intelligent Costing & Stitching Demo")

# --- 2. LEARN THE SKILL: DATASET GENERATOR (The Example) ---
st.sidebar.header("Step 1: Generate Demo Data")
if st.sidebar.button("Create Sample Costing Data"):
    # Simulated Bill of Materials
    bom_data = {
        "Component": ["Processor", "Memory", "Chassis", "Display"],
        "Quantity": [1, 2, 1, 1],
        "Unit": ["pcs", "pcs", "pcs", "pcs"]
    }
    # Simulated Price List (with a "string" number to test your error fix)
    price_data = {
        "Component": ["Processor", "Memory", "Chassis", "Display"],
        "Unit_Cost": ["250.50", "80.00", "45.25", "120.00"], # Strings to simulate messy data
        "Currency": ["USD", "USD", "USD", "USD"]
    }
    st.session_state['df_bom'] = pd.DataFrame(bom_data)
    st.session_state['df_price'] = pd.DataFrame(price_data)
    st.sidebar.success("Sample Data Loaded!")

# --- 3. THE "INTELLIGENT" STITCHING LOGIC ---
if 'df_bom' in st.session_state and 'df_price' in st.session_state:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Bill of Materials")
        st.dataframe(st.session_state['df_bom'])
        
    with col2:
        st.subheader("💰 Supplier Price List")
        st.dataframe(st.session_state['df_price'])

    if st.button("Calculate Final Product Cost"):
        # STITCHING: Merging the two datasets on 'Component'
        stitched_df = pd.merge(st.session_state['df_bom'], st.session_state['df_price'], on="Component")

        # --- THE FIX: Converting 'Object' to 'Numeric' before math ---
        for col in ['Quantity', 'Unit_Cost']:
            stitched_df[col] = pd.to_numeric(stitched_df[col], errors='coerce')

        # COSTING CALCULATIONS
        stitched_df['Total_Component_Cost'] = stitched_df['Quantity'] * stitched_df['Unit_Cost']
        
        # Calculate Grand Total
        grand_total = stitched_df['Total_Component_Cost'].sum()
        
        # APPLYING MARGIN (Intelligence)
        margin_percent = 0.30  # 30% Margin
        srp = grand_total / (1 - margin_percent)

        # --- FINAL ROUNDING (Line 306 Fix) ---
        final_report = stitched_df.round(2)

        # --- 4. DISPLAY RESULTS ---
        st.divider()
        st.header("📊 Final Costing Analysis")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Manufacturing Cost", f"${grand_total:,.2f}")
        c2.metric("Target Margin", "30%")
        c3.metric("Suggested Retail (SRP)", f"${srp:,.2f}", delta=f"${srp-grand_total:,.2f} Profit")

        st.table(final_report[['Component', 'Quantity', 'Unit_Cost', 'Total_Component_Cost']])

        # Download Result
        csv = final_report.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Costing Sheet", data=csv, file_name="costing_report.csv")

else:
    st.info("Click the button in the sidebar to generate the demo data and see the intelligence in action!")
