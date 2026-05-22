from services.dhis_api import api_get

def validate_orgunit_id(ou_id):
    # Check if org unit exists
    res = api_get(f"organisationUnits/{ou_id}?fields=id")
    return "id" in res

def fetch_child_level(ou_id):
    # Fetch the immediate children of an org unit and returns a list of {id, name}.
    res = api_get(
        f"organisationUnits?fields=id,name,level&filter=parent.id:eq:{ou_id}&paging=false"
    )
    return res.get("organisationUnits", [])
