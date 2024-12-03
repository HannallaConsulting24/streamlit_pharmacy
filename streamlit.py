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
    file_path = 'NDC_data2 (2).csv'  # File for NDC search
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
            # Extract unique NDCs associated with the selected Rxcui
            ndc_list = filtered_df['NDC'].dropna().unique()
            st.markdown(f"### Found {len(ndc_list)} NDC(s) associated with Rxcui {search_value}:")
            for ndc in ndc_list:
                st.markdown(f"- **NDC**: {ndc}")
    elif search_type == "NDC":
        filtered_df = ndc_df[(ndc_df['NDC'] == search_value)]
    
    if not filtered_df.empty:
        if search_type == "NDC":
            filtered_df = filtered_df[['NDC', 'Status', 'Active', 'RxNorm NDC', 'RxCUI', 'Concept Name', 'Concept Status', 'Sources', 'Alt NDC', 'Comment', 'History']].drop_duplicates()
        else:
            filtered_df = filtered_df[['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates().replace("Not Available", np.nan)
    else:
        filtered_df = pd.DataFrame()
else:
    filtered_df = pd.DataFrame()

# Display results
if not filtered_df.empty:
    if search_type == "NDC":
        st.subheader(f"Results for your NDC search:")
        for _, row in filtered_df.iterrows():
            st.markdown("---")
            st.markdown(f"- **NDC**: {row['NDC']}")
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
            st.markdown("---")
    else:
        st.subheader(f"Results for your search:")
        for _, row in filtered_df.iterrows():
            st.markdown("---")
            st.markdown(f"### Drug Name: **{row['Cleaned Up Drug Name']}**")
            st.markdown(f"- **Quantity**: {row['Quantity']}")
            st.markdown(f"- **Net**: {row['Net']}")
            st.markdown(f"- **Copay**: {row['Copay']}")
            st.markdown(f"- **Covered**: {row['Covered']}")
            st.markdown(f"- **ClassDb**: {row['ClassDb']}")
            st.markdown("---")
                # Display alternative drugs from the same class and same insurance
    st.subheader("Alternative Drugs in the Same Class and Insurance")
    class_name = filtered_df.iloc[0]['ClassDb']  # Get the class of the first drug
    alternatives = df[(df['ClassDb'] == class_name) & (df['Insurance'] == insurance_input)][['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates()

    # Handle missing values and sorting
    alternatives['Net'] = pd.to_numeric(alternatives['Net'], errors='coerce')  # Keep nan for lowest
    alternatives['Copay'] = pd.to_numeric(alternatives['Copay'], errors='coerce')  # Keep nan for lowest

    # Filtering options
    st.markdown(f"**Found {len(alternatives)} alternatives in the same class and insurance.**")
    filter_option = st.selectbox("Filter Alternatives By:", options=["None", "Highest Net", "Lowest Copay"])
    
    # Apply filter
    if filter_option == "Highest Net":
        alternatives = alternatives.sort_values(by="Net", ascending=False, na_position="last")
    elif filter_option == "Lowest Copay":
        alternatives = alternatives.sort_values(by="Copay", ascending=True, na_position="first")

    # Display filtered alternatives
    for _, alt_row in alternatives.iterrows():
        st.markdown("---")
        st.markdown(f"### Alternative Drug Name: **{alt_row['Cleaned Up Drug Name']}**")
        st.markdown(f"- **Class Name**: {alt_row['ClassDb']}")
        st.markdown(f"- **Details**: Quantity: {alt_row['Quantity']}, Net: {alt_row['Net']}, Copay: {alt_row['Copay']}, Covered: {alt_row['Covered']}")
else:
    if search_value and insurance_input:
        st.warning(f"No results found for {search_type}: {search_value} with Insurance: {insurance_input}.")
    else:
        st.info("Please enter both search criteria and insurance to get results.")
else:
    if search_value and insurance_input:
        st.warning(f"No results found for {search_type}: {search_value} with Insurance: {insurance_input}.")
    else:
        st.info("Please enter both search criteria and insurance to get results.")
