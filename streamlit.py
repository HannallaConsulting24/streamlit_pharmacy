import streamlit as st
import pandas as pd

# Load the dataset
@st.cache_data
def load_data():
    file_path = 'Matched_Data_Final2.csv'  # Updated file name
    return pd.read_csv(file_path).drop_duplicates()

# Load the data
df = load_data()

# Display logo and title
logo_path = "image (1).png"  # Path to the uploaded logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo_path, use_column_width=True)
with col2:
    st.title("CDI Medication Guiding Tool 💊")

# Search options
st.markdown("### Search Options")
st.info("Search using Drug Name, Rxcui, or NDC, and Insurance.")

# Unique dropdown values
drug_names = df['Cleaned Up Drug Name'].dropna().unique()
insurance_names = df['Insurance'].dropna().unique()
rxcui_codes = df['Rxcui'].dropna().unique()
ndc_codes = df['NDC'].dropna().unique()

# Search filters
search_type = st.radio("Select Search Type:", ["Drug Name", "Rxcui", "NDC"])
if search_type == "Drug Name":
    search_value = st.selectbox("Search for a Drug Name:", [""] + list(drug_names))
elif search_type == "Rxcui":
    search_value = st.selectbox("Search for an Rxcui:", [""] + [str(x) for x in rxcui_codes])
elif search_type == "NDC":
    search_value = st.selectbox("Search for an NDC:", [""] + [str(x) for x in ndc_codes])

insurance_input = st.selectbox("Select Insurance:", [""] + list(insurance_names))

# Filter the data
if search_value and insurance_input:
    if search_type == "Drug Name":
        filtered_df = df[(df['Cleaned Up Drug Name'].str.contains(search_value, case=False)) & 
                         (df['Insurance'] == insurance_input)]
    elif search_type == "Rxcui":
        filtered_df = df[(df['Rxcui'] == int(search_value)) & (df['Insurance'] == insurance_input)]
    elif search_type == "NDC":
        filtered_df = df[(df['NDC'] == search_value) & (df['Insurance'] == insurance_input)]
    
    filtered_df = filtered_df[['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates().fillna("Not Available")
else:
    filtered_df = pd.DataFrame()

# Display results
if not filtered_df.empty:
    st.subheader(f"Results for your search:")
    for _, row in filtered_df.iterrows():
        st.markdown("---")
        st.markdown(f"### Drug Name: **{row['Cleaned Up Drug Name']}**")
        st.markdown(f"- **Quantity**: {row['Quantity']}")
        st.markdown(f"- **Net**: {row['Net']}")
        st.markdown(f"- **Copay**: {row['Copay']}")
        st.markdown(f"- **Covered**: {row['Covered']}")
        st.markdown(f"- **ClassDb**: {row['ClassDb']}")

    # Display alternative drugs
    st.subheader("Alternative Drugs in the Same Class and Insurance")
    class_name = filtered_df.iloc[0]['ClassDb']
    alternatives = df[(df['ClassDb'] == class_name) & (df['Insurance'] == insurance_input)][['Cleaned Up Drug Name', 'Quantity', 'Net', 'Copay', 'Covered', 'ClassDb']].drop_duplicates()

    # Replace missing values for display
    alternatives['Net'] = pd.to_numeric(alternatives['Net'], errors='coerce').fillna(-1e9)
    alternatives['Copay'] = pd.to_numeric(alternatives['Copay'], errors='coerce').fillna(1e9)
    alternatives['Net'] = alternatives['Net'].replace(-1e9, "Not Available")
    alternatives['Copay'] = alternatives['Copay'].replace(1e9, "Not Available")
    alternatives['Covered'] = alternatives['Covered'].fillna("Not Available")

    # Filtering options
    st.markdown(f"**Found {len(alternatives)} alternatives in the same class and insurance.**")
    filter_option = st.selectbox("Filter Alternatives By:", ["None", "Highest Net", "Lowest Copay"])

    # Apply filter
    if filter_option == "Highest Net":
        alternatives = alternatives.sort_values(by="Net", ascending=False)
    elif filter_option == "Lowest Copay":
        alternatives = alternatives.sort_values(by="Copay", ascending=True)

    # Display alternatives
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
