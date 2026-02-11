import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Stitching App", layout="wide")

st.title("📊 Data Stitching & Processing App")

# 1. File Upload
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Original Data Preview")
    st.write(df.head())

    # --- THE FIX FOR YOUR ERROR (Line 306 Area) ---
    st.subheader("Processed Data")
    
    # We create a copy to process
    processed_df = df.copy()

    # Step A: Convert columns to numeric where possible
    # This prevents the "Expected numeric dtype, got object instead" error
    for col in processed_df.columns:
        # errors='coerce' turns strings like "N/A" or " " into NaN (numbers)
        # errors='ignore' ensures actual text columns (like Names) stay as strings
        if processed_df[col].dtype == 'object':
            try:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
            except:
                pass # Keep as object if it's strictly text

    # Step B: Perform the rounding safely
    # This is where your app was previously crashing
    try:
        processed_df = processed_df.round(2)
        st.success("Data rounded successfully!")
    except TypeError as e:
        st.error(f"Rounding failed: {e}")
        st.info("Check if your numeric columns contain hidden text or symbols.")

    # Display Result
    st.write(processed_df)

    # 2. Download Button
    csv = processed_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Processed CSV",
        data=csv,
        file_name="stitched_data_cleaned.csv",
        mime="text/csv",
    )

else:
    st.info("Please upload a file to begin.")
