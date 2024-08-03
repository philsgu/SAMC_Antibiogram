import streamlit as st
import pandas as pd
import re

st.header("SAMC 2024 ANTIBIOTIC SUSCEPTIBILITY REPORT (2023 Data)")
st.write("Please select the organisms and antibiotics you wish to search. Table results can be downloaded as a CSV, sorted alphabetically, and be further searched within the table. If you wish to download 2024 SAMC Antibiogram, please click here: [Download SAMC 2024 antibiogram](https://github.com/philsgu/SAMC_Antibiogram/blob/655d461e3a2c97fd7d9dce5dbc7e46393427623c/2024_antibiogram_data.pdf)", unsafe_allow_html=True)
# Load the data
df = pd.read_csv('merged_df.csv')
antibiotics_df = pd.read_csv('antibiotics_samc.csv')

# Filter out columns with '-' values
df_filtered = df.loc[:, (df != '-').any(axis=0)]

# Convert sensitivity values to numeric, errors='coerce' will convert '-' to NaN
sensitivity_columns = df_filtered.columns[3:]

# Remove 'No. Isolates (Tot. 1130)' column from sensitivity columns if present
sensitivity_columns = sensitivity_columns[sensitivity_columns != 'No. Isolates (Tot. 1130)']

df_filtered[sensitivity_columns] = df_filtered[sensitivity_columns].apply(pd.to_numeric, errors='coerce')

tab1, tab2, = st.tabs(["Organisms", "Antibiotics",])

# Streamlit app
with tab1:
    st.title("Organism Search")

    # Get unique organisms and sort them alphabetically
    organisms = sorted(df_filtered['Organism'].unique())

    # Multi-select for organisms
    selected_organisms = st.multiselect("Please Select Organism(s)", options=organisms)

    # Display the relevant data sorted by sensitivity values
    if selected_organisms:
        for organism in selected_organisms:
            st.write(f"**Organism:** *{organism}*")
            st.write(f"**Gram Stain Type:** {df_filtered[df_filtered['Organism'] == organism]['Gram Stain Type'].iloc[0]}")
            if df_filtered[df_filtered['Organism'] == organism]['Gram Stain Type'].iloc[0] == 'Pos.':
                st.write(f"**No. Isolates (Tot. 1130):** {int(df_filtered[df_filtered['Organism'] == organism]['No. Isolates (Tot. 1130)'].iloc[0])}")
            else:
                st.write(f"**No. Isolates (Tot. 5196):** {int(df_filtered[df_filtered['Organism'] == organism]['No. Isolates (Tot. 5196)'].iloc[0])}")

            organism_data = df_filtered[df_filtered['Organism'] == organism]
            
            sensitivities = organism_data[sensitivity_columns].dropna(axis=1).T
            sensitivities.columns = ['Sensitivity %']
            sensitivities_sorted = sensitivities.sort_values(by='Sensitivity %', ascending=False)
            sensitivities_sorted.index.name = 'Antibiotics'
            st.dataframe(sensitivities_sorted)
            
            # Check if Rifampin is in the sensitivities and add a note
            if 'Rifampin**' in sensitivities_sorted.index:
                st.write('** **Rifampin should not be used alone for antimicrobial therapy**')
            
            st.write("---")

with tab2:
    st.title("Antibiotics Search")

    # Extract the agent names and class names for multi-select
    agents = sorted(antibiotics_df['Agent'].unique())
    classes = sorted(antibiotics_df['Class'].unique())

    # Multi-select for agents (antibiotics) and classes
    selected_agents_classes = st.multiselect("Please Select Antibiotic(s) or Class(es)", options=agents + classes)

    if selected_agents_classes:
         # Escape special characters for regex search
        escaped_selected_agents_classes = [re.escape(item) for item in selected_agents_classes]
        
        
        # Create masks for filtering
        m1 = antibiotics_df['Agent'].isin(selected_agents_classes)
        m2 = antibiotics_df['Class'].isin(selected_agents_classes)
        # Filter the dataframe
        df_search = antibiotics_df[m1 | m2]

        st.dataframe(df_search, hide_index=True)




