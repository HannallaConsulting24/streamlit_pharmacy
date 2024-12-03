import streamlit as st
import pandas as pd
import numpy as np  # To use np.nan

# Load the dataset
@st.cache_data
def load_data():
    file_path = 'Matched_Data_Final2.csv'  # Updated file name
    return pd.read_csv(file_path).drop_duplicates()

# Load the data
df = load_data()

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
ndc_codes = df['NDC'].dropna().unique()

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
    if search_type == "Rxcui":
        filtered_df = df[(df['Rxcui'] == int(search_value)) & 
                         (df['Insurance'].str.contains(insurance_input, na=False, case=False))]
        
        if not filtered_df.empty:
            unique_ndcs = filtered_df[['NDC', 'Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates()
        else:
            unique_ndcs = pd.DataFrame()
    else:
        filtered_df = pd.DataFrame()
        unique_ndcs = pd.DataFrame()
else:
    filtered_df = pd.DataFrame()
    unique_ndcs = pd.DataFrame()

# Display results
if search_type == "Rxcui" and not filtered_df.empty:
    st.subheader(f"Results for Rxcui: {search_value} with Insurance: {insurance_input}")
    for _, row in filtered_df[['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].iterrows():
        st.markdown("---")
        st.markdown(f"### Drug Name: **{row['Cleaned Up Drug Name']}**")
        st.markdown(f"- **Quantity**: {row['Quantity']}")
        st.markdown(f"- **Net**: {row['Net']}")
        st.markdown(f"- **Copay**: {row['Copay']}")
        st.markdown(f"- **Covered**: {row['Covered']}")
        st.markdown(f"- **ClassDb**: {row['ClassDb']}")
    
    # Display unique NDCs
    if not unique_ndcs.empty:
        st.subheader(f"Unique NDCs for Rxcui {search_value}:")
        for _, ndc_row in unique_ndcs.iterrows():
            st.markdown("---")
            st.markdown(f"### NDC: **{ndc_row['NDC']}**")
            st.markdown(f"- **Drug Name**: {ndc_row['Cleaned Up Drug Name']}")
            st.markdown(f"- **Quantity**: {ndc_row['Quantity']}")
            st.markdown(f"- **Net**: {ndc_row['Net']}")
            st.markdown(f"- **Copay**: {ndc_row['Copay']}")
            st.markdown(f"- **Covered**: {ndc_row['Covered']}")
            st.markdown(f"- **ClassDb**: {ndc_row['ClassDb']}")
else:
    if search_value and insurance_input:
        st.warning(f"No results found for {search_type}: {search_value} with Insurance: {insurance_input}.")
    else:
        st.info("Please enter both search criteria and insurance to get results.")
