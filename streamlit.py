import streamlit as st
import pandas as pd
import numpy as np  # To use np.nan

# Load the datasets
@st.cache_data
def load_main_data():
    file_path = 'Matched_Data_Final2.csv'  # Original file 
    return pd.read_csv(file_path).drop_duplicates()

@st.cache_data
def load_ndc_data():
    file_path = 'NDC_Details_RxNav.csv'  # Updated file for NDC search
    return pd.read_csv(file_path).drop_duplicates()

# Load the data
df = load_main_data()
ndc_df = load_ndc_data()

# Display logo and title
logo_path = "image (1).png"  # Path to the uploaded logo

# Use columns for better alignment
col1, col2 = st.columns([1, 4])  # Adjust column widths
with col1:
    st.image(logo_path, use_column_width=True)
with col2:
    st.title("CDI Medication Guiding Tool 💊")

# Search criteria
st.markdown("### Search Options")
st.info("Search using Drug Name, Rxcui, or NDC, and Insurance.")

# Fetch unique values for dropdowns
drug_names = df['Cleaned Up Drug Name'].dropna().unique()
insurance_names = df['Insurance'].dropna().unique()
rxcui_codes = df['Rxcui'].dropna().unique()
ndc_codes = ndc_df['NDC'].dropna().unique()

# Search fields with auto-complete
search_type = st.radio("Select Search Type:", ["Drug Name", "Rxcui", "NDC"])
if search_type == "Drug Name":
    drug_name_input = st.selectbox("Search for a Drug Name:", options=[""] + list(drug_names), format_func=lambda x: x if x else "Type to search...")
    search_value = drug_name_input
elif search_type == "Rxcui":
    rxcui_input = st.selectbox("Search for an Rxcui:", options=[""] + list(rxcui_codes), format_func=lambda x: str(x) if x else "Type to search...")
    search_value = rxcui_input
elif search_type == "NDC":
    ndc_input = st.selectbox("Search for an NDC:", options=[""] + list(ndc_codes), format_func=lambda x: str(x) if x else "Type to search...")
    search_value = ndc_input

insurance_input = st.selectbox("Search for an Insurance:", options=[""] + list(insurance_names), format_func=lambda x: x if x else "Type to search...")

# Filter data based on the selected criteria
if search_value and insurance_input:
    if search_type == "Drug Name":
        filtered_df = df[(df['Cleaned Up Drug Name'].str.contains(search_value, na=False, case=False)) & 
                         (df['Insurance'].str.contains(insurance_input, na=False, case=False))]
    elif search_type == "Rxcui":
        filtered_df = df[(df['Rxcui'] == int(search_value)) & 
                         (df['Insurance'].str.contains(insurance_input, na=False, case=False))]
        if not filtered_df.empty:
            ndc_list = filtered_df['NDC'].dropna().unique()
            st.markdown(f"### Found {len(ndc_list)} NDC(s) associated with Rxcui {search_value}:")
            for ndc in ndc_list:
                st.markdown(f"- **NDC**: {ndc}")
    elif search_type == "NDC":
        # Search in NDC_Details_RxNav.csv
        ndc_details = ndc_df[ndc_df['NDC'] == search_value]

        # Search in Matched_Data_Final2.csv
        filtered_df = df[(df['NDC'] == search_value) & 
                         (df['Insurance'].str.contains(insurance_input, na=False, case=False))]
        
        if not filtered_df.empty:
            filtered_df = filtered_df[['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates().replace("Not Available", np.nan)
            st.subheader(f"Results for NDC: {search_value} with Insurance: {insurance_input}")
            for _, row in filtered_df.iterrows():
                st.markdown("---")
                st.markdown(f"### Drug Name: **{row['Cleaned Up Drug Name']}**")
                st.markdown(f"- **Quantity**: {row['Quantity']}")
                st.markdown(f"- **Net**: {row['Net']}")
                st.markdown(f"- **Copay**: {row['Copay']}")
                st.markdown(f"- **Covered**: {row['Covered']}")
                st.markdown(f"- **ClassDb**: {row['ClassDb']}")
                st.markdown("---")

            # Alternatives in the same class and insurance
            st.subheader("Alternative Drugs in the Same Class and Insurance")
            class_name = filtered_df.iloc[0]['ClassDb']
            alternatives = df[(df['ClassDb'] == class_name) & (df['Insurance'] == insurance_input)][['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates()
            if not alternatives.empty:
                st.markdown(f"**Found {len(alternatives)} alternatives in the same class and insurance.**")
                for _, alt_row in alternatives.iterrows():
                    st.markdown("---")
                    st.markdown(f"### Alternative Drug Name: **{alt_row['Cleaned Up Drug Name']}**")
                    st.markdown(f"- **Class Name**: {alt_row['ClassDb']}")
                    st.markdown(f"- **Details**: Quantity: {alt_row['Quantity']}, Net: {alt_row['Net']}, Copay: {alt_row['Copay']}, Covered: {alt_row['Covered']}")

        if not ndc_details.empty:
            st.subheader("Additional NDC Details")
            for _, row in ndc_details.iterrows():
                st.markdown("---")
                st.markdown(f"- **NDC**: {row['NDC']}")
                st.markdown(f"- **ANDA**: {row['ANDA']}")
                st.markdown(f"- **Color Text**: {row['COLORTEXT']}")
                st.markdown(f"- **Color**: {row['COLOR']}")
                st.markdown(f"- **DM SPL ID**: {row['DM_SPL_ID']}")
                st.markdown(f"- **Imprint Code**: {row['IMPRINT_CODE']}")
                st.markdown(f"- **Labeler**: {row['LABELER']}")
                st.markdown(f"- **Label Type**: {row['LABEL_TYPE']}")
                st.markdown(f"- **Marketing Category**: {row['MARKETING_CATEGORY']}")
                st.markdown(f"- **Marketing Effective Time Low**: {row['MARKETING_EFFECTIVE_TIME_LOW']}")
                st.markdown(f"- **Marketing Status**: {row['MARKETING_STATUS']}")
                st.markdown(f"- **Score**: {row['SCORE']}")
                st.markdown(f"- **Shape Text**: {row['SHAPETEXT']}")
                st.markdown(f"- **Shape**: {row['SHAPE']}")
                st.markdown(f"- **Size**: {row['SIZE']}")
                st.markdown(f"- **NDA Authorized Generic**: {row['NDA_AUTHORIZED_GENERIC']}")
                st.markdown(f"- **Marketing Effective Time High**: {row['MARKETING_EFFECTIVE_TIME_HIGH']}")
                st.markdown(f"- **NDA**: {row['NDA']}")
                st.markdown(f"- **Unapproved Drug Other**: {row['UNAPPROVED_DRUG_OTHER']}")
                st.markdown(f"- **OTC Monograph Drug**: {row['OTC_MONOGRAPH_DRUG']}")
                st.markdown(f"- **OTC Monograph Final**: {row['OTC_MONOGRAPH_FINAL']}")
                st.markdown("---")

    if filtered_df.empty and ndc_details.empty:
        st.warning(f"No results found for NDC: {search_value} with Insurance: {insurance_input}.")
else:
    st.info("Please enter both search criteria and insurance to get results.")
