import streamlit as st
import pandas as pd
import numpy as np  # To use np.nan

# Load the datasets
@st.cache_data
def load_matched_data():
    file_path = 'Matched_Data_Final2.csv'  # Main file
    return pd.read_csv(file_path).drop_duplicates()

@st.cache_data
def load_ndc_data():
    file_path = '/mnt/data/NDC_data2 (2).csv'  # NDC specific file
    return pd.read_csv(file_path).drop_duplicates()

# Load data
df_matched = load_matched_data()
df_ndc = load_ndc_data()

# Display logo and title
logo_path = "/mnt/data/image.png"  # Path to the uploaded logo

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
drug_names = df_matched['Cleaned Up Drug Name'].dropna().unique()
insurance_names = df_matched['Insurance'].dropna().unique()
rxcui_codes = df_matched['Rxcui'].dropna().unique()
ndc_codes = df_matched['NDC'].dropna().unique()

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
if search_value:
    if search_type == "Drug Name":
        filtered_df = df_matched[(df_matched['Cleaned Up Drug Name'].str.contains(search_value, na=False, case=False)) & 
                                 (df_matched['Insurance'].str.contains(insurance_input, na=False, case=False))]
    elif search_type == "Rxcui":
        filtered_df = df_matched[(df_matched['Rxcui'] == int(search_value)) & 
                                 (df_matched['Insurance'].str.contains(insurance_input, na=False, case=False))]
    elif search_type == "NDC":
        # Use the NDC-specific file
        filtered_df = df_ndc[df_ndc['RxNorm NDC'] == search_value]
        if not filtered_df.empty:
            st.subheader(f"Details for NDC: {search_value}")
            for _, row in filtered_df.iterrows():
                st.markdown("---")
                st.markdown(f"- **Status**: {row['Status']}")
                st.markdown(f"- **Active**: {row['Active']}")
                st.markdown(f"- **RxNorm NDC**: {row['RxNorm NDC']}")
                st.markdown(f"- **RxCUI**: {row['RxCUI']}")
                st.markdown(f"- **Concept Name**: {row['Concept Name']}")
                st.markdown(f"- **Concept Status**: {row['Concept Status']}")
                st.markdown(f"- **Sources**: {row['Sources']}")
                st.markdown(f"- **Alt NDC**: {row['Alt NDC']}")
                st.markdown(f"- **Comment**: {row['Comment']}")
                st.markdown(f"- **History**: {row['History']}")
        else:
            st.warning(f"No results found for NDC: {search_value}.")
        # Exit early for NDC search since data is shown already
        st.stop()
else:
    st.info("Please enter a search value to get results.")
