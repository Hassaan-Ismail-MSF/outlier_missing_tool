from .dhis_api import api_get
from utils.metadata import extract_value_from_metadata

def fetch_data_elements_in_group(deg_id):
    res = api_get(
        f"dataElementGroups/{deg_id}?fields=dataElements[id,name]&paging=false"
    )
    return res.get("dataElements", [])

def fetch_de_metadata(de_id):
    fields = (
        "id,name,code,displayFormName,formName,description,valueType,"
        "attributeValues[value,attribute[id,name]],"
        "optionSet[options[id,name,code]]"
    )
    return api_get(f"dataElements/{de_id}?fields={fields}")


def fetch_metadata_values(de_ids):
    values = {}
    names = {}

    for de_id in de_ids:
        meta = fetch_de_metadata(de_id)

        # Always return a valid name
        names[de_id] = (
            meta.get("name")
            or meta.get("displayFormName")
            or meta.get("formName")
            or de_id
        )

        values[de_id] = extract_value_from_metadata(meta)

    return names, values
