import numpy as np
import pandas as pd

def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["value_score"] = out["health_score"] / out["cost_proxy"].replace(0, np.nan)
    return out

def quadrant_labels(df: pd.DataFrame, x_col: str, y_col: str):
    return float(df[x_col].median()), float(df[y_col].median())
