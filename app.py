import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CSS STYLING FIX (Addressing your Line 9 Error) ---
# Changed 'unsafe_base64=True' to 'unsafe_allow_html=True'
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧵 Professional Data Stitching App")
st.write("Upload your files to merge and process them safely.")

# --- 2. FILE UPLOADER ---
uploaded_files = st.file_uploader("Choose CSV or Excel files", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for file in uploaded_files:
        if file.name.endswith('.csv'):
            dfs.append(pd.read_csv(file))
        else:
            dfs.append(pd.read_excel(file))
    
    # Simple Stitching: Concatenate files
    if len(dfs) > 1:
        df = pd.concat(dfs, ignore_index=True)
        st.success(f"Successfully stitched {len(dfs)} files.")
    else:
        df = dfs[0]

    # --- 3. DATA CLEANING & ROUNDING FIX (Addressing your Numeric Error) ---
    st.subheader("Data Processing")
    
    # Create a copy to avoid modifying the original until cleaned
    processed_df = df.copy()

    # Step A: Convert columns to numeric if they contain numbers disguised as strings
    for col in processed_df.columns:
        # Check if the column is an 'object' (text) type
        if processed_df[col].dtype == 'object':
            # errors='coerce' turns non-numeric text into NaN (Null)
            temp_numeric = pd.to_numeric(processed_df[col], errors='coerce')
            
            # If the column actually contains numbers, update it
            if not temp_numeric.isna().all():
                processed_df[col] = temp_numeric

    # Step B: Safe Rounding
    try:
        # Now that dtypes are numeric, .round(2) will work perfectly
        processed_df = processed_df.round(2)
        st.info("💡 All numeric columns have been rounded to 2 decimal places.")
    except TypeError:
        st.warning("Some columns could not be rounded because they contain non-numeric text.")

    # --- 4. DISPLAY & DOWNLOAD ---
    st.dataframe(processed_df, use_container_width=True)

    csv = processed_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Stitched Data",
        data=csv,
        file_name="stitched_output.csv",
        mime="text/csv",
    )

else:
    st.info("Please upload files to see the stitching results.")
