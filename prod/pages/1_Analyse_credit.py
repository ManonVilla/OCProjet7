import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import requests
import json
import shap
import numpy as np

from utils import load_data, SEUIL_OPTIMAL, API_URL
from graphs import create_gauge_chart

st.set_page_config(page_title="Analyse crédit", layout="wide")
st.title("🔍 Analyse du dossier crédit")

# ── Récupération du client sélectionné ───────────────────────────────────────
df = st.session_state.get("df", load_data())
client_id = st.session_state.get("client_id", df['SK_ID_CURR'].iloc[0])

# Resélection possible directement sur cette page
st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox(
    "Sélectionnez un client",
    df['SK_ID_CURR'].unique(),
    index=int((df['SK_ID_CURR'] == client_id).argmax())
)
st.session_state["client_id"] = client_id
client_row = df[df['SK_ID_CURR'] == client_id].iloc[0]

# ── Analyse ───────────────────────────────────────────────────────────────────
st.subheader(f"Dossier client {client_id}")

if st.button(f"Lancer l'analyse du dossier {client_id}", type="primary"):
    data_dict = json.loads(client_row.to_json())
    with st.spinner("Analyse en cours..."):
        response = requests.post(API_URL, json={"data": data_dict})

    if response.status_code == 200:
        result = response.json()
        st.success("Analyse terminée !")
        proba = result['probabilite_defaut']

        fig = create_gauge_chart(proba, SEUIL_OPTIMAL)
        if proba > SEUIL_OPTIMAL:
            st.warning("🍂 Crédit refusé : le client présente un risque de défaut élevé.")
        else:
            st.success("🍃 Crédit accordé : le client présente un risque de défaut faible.")
        st.plotly_chart(fig)

        st.markdown("---")

        try:
            shap_values_array  = np.array(result['shap_values'])
            base_value         = result['base_value']
            feature_names      = result['feature_names']
            client_data_values = client_row[feature_names].values.astype(float)

            explanation = shap.Explanation(
                values=shap_values_array,
                base_values=base_value,
                data=client_data_values,
                feature_names=feature_names
            )
            plt.close('all')
            shap.plots.waterfall(explanation, show=False, max_display=10)
            fig_shap = plt.gcf()
            fig_shap.set_size_inches(10, 6)
            fig_shap.tight_layout()
            buf = io.BytesIO()
            fig_shap.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            st.subheader("📌 Facteurs influençant la décision (SHAP)")
            st.image(buf)
            plt.close('all')
        except Exception as e:
            st.error(f"Erreur SHAP : {e}")
    else:
        st.error(f"Erreur lors de l'analyse. Code : {response.status_code}")

st.caption(f"Seuil de décision : {SEUIL_OPTIMAL}. Au-delà, le risque de défaut est considéré élevé.")