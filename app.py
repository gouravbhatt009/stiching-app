import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Stitching Tool", layout="wide")

st.title("🧵 Professional Data Stitching App")

# --- STEP 1: UPLOAD TWO FILES ---
col1, col2 = st.columns(2)
with col1:
    file_a = st.file_uploader("Upload First File (Base)", type=['csv', 'xlsx'])
with col2:
    file_b = st.file_uploader("Upload Second File (To Join)", type=['csv', 'xlsx'])

if file_a and file_b:
    # Load files
    df1 = pd.read_csv(file_a) if file_a.name.endswith('.csv') else pd.read_excel(file_a)
    df2 = pd.read_csv(file_b) if file_b.name.endswith('.csv') else pd.read_excel(file_b)

    # --- STEP 2: SELECT THE JOIN KEY ---
    common_columns = list(set(df1.columns) & set(df2.columns))
    
    if common_columns:
        join_key = st.selectbox("Select the common column to stitch on:", common_columns)
        
        if st.button("Stitch Data Now"):
            # --- STEP 3: THE STITCHING (Merging) ---
            combined_df = pd.merge(df1, df2, on=join_key, how='left')

            # --- STEP 4: THE ERROR FIX (Line 306 Solution) ---
            # We loop through columns to force numeric types before rounding
            for col in combined_df.columns:
                # We try to convert everything to numeric. 
                # Strings like "Apple" stay as strings because of 'ignore' or check
                if combined_df[col].dtype == 'object':
                    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

            # Now we round only the numeric columns to 2 decimal places
            # This is exactly where your line 306 was failing
            final_df = combined_df.round(2)

            st.success("Stitched and Rounded Successfully!")
            st.dataframe(final_df)

            # --- STEP 5: DOWNLOAD ---
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Result", data=csv, file_name="stitched_output.csv")
    else:
        st.error("No common columns found between the two files to stitch them together.")

else:
    st.info("Please upload two files to begin the stitching process.")
