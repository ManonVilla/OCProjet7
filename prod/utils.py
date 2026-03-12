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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_parquet(os.path.join(current_dir, 'X_test.parquet'))
    return df