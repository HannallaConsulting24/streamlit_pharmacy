import streamlit as st
import pandas as pd

# Load the datasets
@st.cache_data
def load_matched_data():
    file_path = 'Matched_Data_Final2.csv'  # Original file
    return pd.read_csv(file_path).drop_duplicates()

@st.cache_data
def load_ndc_data():
    file_path = 'NDC_data2 (2).csv'  # New file for NDC data
    return pd.read_csv(file_path).drop_duplicates()

# Load the data
df = load_matched_data()
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
st.info("Search using Drug Name, Rxcui, or NDC.")

# Fetch unique values for dropdowns
drug_names = df['Cleaned Up Drug Name'].dropna().unique()
rxcui_codes = df['Rxcui'].dropna().unique()
ndc_codes = ndc_df['RxNorm NDC'].dropna().unique()  # Use NDC from the new file

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

# Filter data based on the selected criteria
if search_value:
    if search_type == "Rxcui":
        filtered_df = df[df['Rxcui'] == int(search_value)]
    elif search_type == "NDC":
        filtered_ndc_df = ndc_df[ndc_df['RxNorm NDC'] == search_value]
    else:
        filtered_df = pd.DataFrame()
        filtered_ndc_df = pd.DataFrame()
else:
    filtered_df = pd.DataFrame()
    filtered_ndc_df = pd.DataFrame()

# Display results
if search_type == "Rxcui" and not filtered_df.empty:
    st.subheader(f"Results for Rxcui: {search_value}")
    for _, row in filtered_df[['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].iterrows():
        st.markdown("---")
        st.markdown(f"### Drug Name: **{row['Cleaned Up Drug Name']}**")
        st.markdown(f"- **Quantity**: {row['Quantity']}")
        st.markdown(f"- **Net**: {row['Net']}")
        st.markdown(f"- **Copay**: {row['Copay']}")
        st.markdown(f"- **Covered**: {row['Covered']}")
        st.markdown(f"- **ClassDb**: {row['ClassDb']}")

elif search_type == "NDC" and not filtered_ndc_df.empty:
    st.subheader(f"Details for NDC: {search_value}")
    for _, row in filtered_ndc_df.iterrows():
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
    if search_value:
        st.warning(f"No results found for {search_type}: {search_value}.")
    else:
        st.info("Please enter search criteria to get results.")
