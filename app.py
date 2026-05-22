import streamlit as st
import pandas as pd
from services.data_elements import fetch_data_elements_in_group, fetch_metadata_values
from services.analytics import fetch_weekly_values
from utils.metadata import fetch_de_groups
from utils.orgunits import validate_orgunit_id, fetch_child_level
from utils.periods import date_to_week
from utils.quality import detect_missing, detect_outliers
from utils.export import df_to_xlsx_bytes


# Page configuration
st.set_page_config(page_title="DHIS2 Data Quality Checker", layout="wide")
st.title("DHIS2 – Data Quality Checker")

# Caching
@st.cache_data(ttl=3600)
def cached_groups():
    return fetch_de_groups()

@st.cache_data(ttl=3600)
def cached_des(group_id):
    return fetch_data_elements_in_group(group_id)

@st.cache_data(ttl=3600)
def cached_validate_orgunit(org_unit):
    return validate_orgunit_id(org_unit)

@st.cache_data(ttl=3600)
def cached_child_level(org_unit):
    return fetch_child_level(org_unit)

@st.cache_data(ttl=3600)
def cached_metadata(de_ids):
    return fetch_metadata_values(de_ids)


# Inputs
st.header("1. Parameters")

groups = cached_groups()
group_map = {g["name"]: g["id"] for g in groups}

# Data element group dropdown
group_name = st.selectbox(
    "Data Element Group",
    list(group_map.keys()),
    key="deg_select"
)
deg_id = group_map[group_name]

# Reset Data Elements when group changes
if "last_group" not in st.session_state:
    st.session_state.last_group = deg_id

if st.session_state.last_group != deg_id:
    st.session_state.selected_des = [] 
    st.session_state.last_group = deg_id

# Data elements
des = cached_des(deg_id)
de_map = {f"{d['name']} ({d['id']})": d["id"] for d in des}

selected_des_labels = st.multiselect(
    "Select Data Elements",
    list(de_map.keys()),
    key="selected_des"
)


# Form for org unit and date range
with st.form("run_form"):
    org_unit = st.text_input("Organisation Unit ID (e.g. Xa3dfgH7)")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date")
    with col2:
        end_date = st.date_input("End date")

    run_button = st.form_submit_button("Run Data Quality Check")


# Process and display results when button is clicked
if run_button:

    if not selected_des_labels:
        st.error("Please select at least one Data Element.")
        st.stop()

    if not org_unit:
        st.error("Please enter an Organisation Unit ID.")
        st.stop()

    with st.spinner("Validating organisation unit..."):
        if not cached_validate_orgunit(org_unit):
            st.error("This organisation unit does not exist.")
            st.stop()

        children = cached_child_level(org_unit)
        display_org_unit_name = children[0]["name"] if children else org_unit

    with st.spinner("Fetching weekly values..."):
        de_ids = [de_map[label] for label in selected_des_labels]
        start_period = date_to_week(start_date)
        end_period = date_to_week(end_date)

        weekly_df = fetch_weekly_values(de_ids, org_unit, start_period, end_period)

        if weekly_df.empty:
            st.warning("No data values found.")
            st.stop()

    with st.spinner("Fetching metadata..."):
        names, metadata_values = cached_metadata(list(weekly_df.index))

        weekly_df.insert(0, "name", weekly_df.index.map(names))
        weekly_df.insert(1, "metadata_value", weekly_df.index.map(metadata_values))
        weekly_df.insert(2, "org_unit", display_org_unit_name)

    with st.spinner("Computing missing values and outliers..."):
        week_cols = [
            c for c in weekly_df.columns
            if len(c) >= 5 and c[:4].isdigit() and "W" in c
        ]

        week_data = weekly_df[week_cols]

        missing_mask = detect_missing(week_data)
        outlier_mask = detect_outliers(week_data)


    # Result display
    st.header("2. Data Quality Results")

    def style_row(row):
        styles = []
        for col in weekly_df.columns:
            if col in week_cols:
                is_missing = missing_mask.loc[row.name, col]
                is_outlier = outlier_mask.loc[row.name, col]
                if is_missing:
                    styles.append("background-color: yellow")
                elif is_outlier:
                    styles.append("background-color: red; color: white")
                else:
                    styles.append("")
            else:
                styles.append("")
        return styles

    styled = weekly_df.style.apply(style_row, axis=1)
    st.dataframe(styled, use_container_width=True, height=700)


    # Result download xlsx format
    st.subheader("Download Results")

    export_df = weekly_df.copy()
    xlsx_bytes = df_to_xlsx_bytes(export_df)

    st.download_button(
        "Download as Excel (.xlsx)",
        data=xlsx_bytes,
        file_name="dhis2_data_quality.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
