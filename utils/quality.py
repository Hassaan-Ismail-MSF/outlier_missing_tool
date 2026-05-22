import pandas as pd
import numpy as np

def detect_missing(df):
    #Return a boolean mask where True = missing value
    return df.isna() | (df == "")

def detect_outliers(df):
    # Compute z-score per row
    numeric_df = df.apply(pd.to_numeric, errors="coerce")

    zscores = (numeric_df - numeric_df.mean(axis=1).values[:, None]) / \
              numeric_df.std(axis=1).values[:, None]

    return abs(zscores) > 2  # threshold
