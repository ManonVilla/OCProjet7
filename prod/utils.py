import os
import pandas as pd
import streamlit as st

SEUIL_OPTIMAL = 0.48

API_URL = "https://ocprojet7.onrender.com/predict"

FEATURES_LISIBLES = {
    "DAYS_BIRTH":                 ("Âge",                   lambda x: f"{abs(int(x)) // 365} ans"),
    "DAYS_EMPLOYED":              ("Ancienneté emploi",      lambda x: f"{abs(int(x)) // 365} ans" if x < 0 else "Sans emploi"),
    "AMT_INCOME_TOTAL":           ("Revenu total",           lambda x: f"{x:,.0f} €"),
    "AMT_CREDIT":                 ("Montant du crédit",      lambda x: f"{x:,.0f} €"),
    "AMT_ANNUITY":                ("Annuité",                lambda x: f"{x:,.0f} €"),
    "AMT_GOODS_PRICE":            ("Prix du bien",           lambda x: f"{x:,.0f} €"),
    "EXT_SOURCE_1":               ("Score externe 1",        lambda x: f"{x:.3f}"),
    "EXT_SOURCE_2":               ("Score externe 2",        lambda x: f"{x:.3f}"),
    "EXT_SOURCE_3":               ("Score externe 3",        lambda x: f"{x:.3f}"),
    "CNT_CHILDREN":               ("Nb enfants",             lambda x: str(int(x))),
    "CNT_FAM_MEMBERS":            ("Nb membres famille",     lambda x: str(int(x))),
    "REGION_POPULATION_RELATIVE": ("Pop. région",            lambda x: f"{x:.5f}"),
}

FEATURES_COMPARAISON = {
    "DAYS_BIRTH":       "Âge (années)",
    "DAYS_EMPLOYED":    "Ancienneté emploi (années)",
    "AMT_INCOME_TOTAL": "Revenu total (€)",
    "AMT_CREDIT":       "Montant crédit (€)",
    "AMT_ANNUITY":      "Annuité (€)",
    "AMT_GOODS_PRICE":  "Prix du bien (€)",
    "EXT_SOURCE_1":     "Score externe 1",
    "EXT_SOURCE_2":     "Score externe 2",
    "EXT_SOURCE_3":     "Score externe 3",
    "CNT_CHILDREN":     "Nb enfants",
}

def to_years(df, col):
    """Convertit DAYS_BIRTH / DAYS_EMPLOYED en années positives."""
    s = df[col].copy()
    if col in ("DAYS_BIRTH", "DAYS_EMPLOYED"):
        s = s.abs() / 365
    return s

@st.cache_data
def load_data():
    import pyarrow.parquet as pq
    import pyarrow as pa
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'X_test.parquet')
    
    table = pq.read_table(file_path)
    # Convertit large_utf8 → utf8 standard pour Streamlit
    new_fields = [
        field.with_type(pa.string()) if field.type == pa.large_utf8() else field
        for field in table.schema
    ]
    table = table.cast(pa.schema(new_fields))
    return table.to_pandas()