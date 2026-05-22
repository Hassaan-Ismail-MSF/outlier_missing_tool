import io
import pandas as pd

def df_to_xlsx_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=True, sheet_name="DataQuality")
    return output.getvalue()
