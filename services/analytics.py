import pandas as pd
from .dhis_api import api_get
from utils.periods import generate_week_range

def fetch_weekly_values(de_ids, org_unit, start_period, end_period):
    weeks = generate_week_range(start_period, end_period)
    period_str = ";".join(weeks)
    dx = ";".join(de_ids)

    url = (
        "analytics.json?"
        f"dimension=dx:{dx}&"
        f"dimension=ou:{org_unit}&"
        f"dimension=pe:{period_str}"
    )

    res = api_get(url)
    rows = res.get("rows", [])

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["dx", "ou", "pe", "value"])
    df = df.drop(columns=["ou"])

    return df.pivot_table(
        index="dx",
        columns="pe",
        values="value",
        aggfunc="first"
    )
