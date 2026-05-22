from services.dhis_api import api_get

def extract_value_from_metadata(meta):
    attr_vals = meta.get("attributeValues", [])
    for av in attr_vals:
        if av.get("value"):
            return av["value"]

    option_set = meta.get("optionSet")
    if option_set:
        options = option_set.get("options", [])
        if options:
            return ", ".join(o.get("code") or o.get("name") for o in options)

    if meta.get("displayFormName"):
        return meta["displayFormName"]

    if meta.get("formName"):
        return meta["formName"]

    if meta.get("description"):
        return meta["description"]

    return None

def fetch_de_groups():
    res = api_get("dataElementGroups?fields=id,name&paging=false")
    return res.get("dataElementGroups", [])