import io
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# ── Récupération du client ────────────────────────────────────────────────────
df = st.session_state.get("df", load_data())
client_id = st.session_state.get("client_id", df['SK_ID_CURR'].iloc[0])

st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox(
    "Sélectionnez un client",
    df['SK_ID_CURR'].astype(int).tolist(),
    index=int((df['SK_ID_CURR'] == client_id).argmax())
)
st.session_state["client_id"] = client_id
client_row = df[df['SK_ID_CURR'] == client_id].iloc[0].copy()

# ── Sliders what-if dans la sidebar ──────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("🎛️ Simulation what-if")
st.sidebar.caption("Modifiez les valeurs pour simuler un autre profil.")

VARIABLES_WIF = {
    "AMT_INCOME_TOTAL": {"label": "Revenu total (€)",      "min": 10_000, "max": 1_000_000, "step": 5_000},
    "DAYS_EMPLOYED": {"label": "Ancienneté emploi (années)", "min": 0, "max": 50, "step": 1},
    "AMT_CREDIT":       {"label": "Montant du crédit (€)", "min": 10_000, "max": 2_000_000, "step": 10_000},
    "AMT_ANNUITY":      {"label": "Annuité (€)",           "min": 1_000,  "max": 200_000,   "step": 1_000},
    "DAYS_BIRTH":       {"label": "Âge (années)",          "min": 18,     "max": 70,        "step": 1},
    "EXT_SOURCE_1":     {"label": "Score externe 1",       "min": 0.0,    "max": 1.0,       "step": 0.01},
    "EXT_SOURCE_2":     {"label": "Score externe 2",       "min": 0.0,    "max": 1.0,       "step": 0.01},
    "EXT_SOURCE_3":     {"label": "Score externe 3",       "min": 0.0,    "max": 1.0,       "step": 0.01},
}

def valeur_initiale(col, row, params):
    """Retourne la valeur initiale du slider pour un client donné."""
    if col in ("DAYS_BIRTH", "DAYS_EMPLOYED"):
        return int(np.clip(abs(row[col]) / 365, params["min"], params["max"]))
    v = float(np.clip(row[col], params["min"], params["max"]))
    return float(params["min"]) if np.isnan(v) else round(v, 4)

def reset_sliders(row):
    """Réinitialise les sliders aux valeurs du client."""
    for col, params in VARIABLES_WIF.items():
        if col in df.columns:
            st.session_state[col] = valeur_initiale(col, row, params)

# Réinitialise si premier chargement ou changement de client
if st.session_state.get("client_id_precedent") != client_id:
    st.session_state["client_id_precedent"] = client_id
    reset_sliders(client_row)

# Bouton reset
if st.sidebar.button("↺ Réinitialiser les valeurs", use_container_width=True):
    reset_sliders(client_row)

# Génération des sliders (sans paramètre value= : Streamlit lit session_state[key])
client_modifie = client_row.copy()

for col, params in VARIABLES_WIF.items():
    if col not in df.columns:
        continue
    if col in ("DAYS_BIRTH", "DAYS_EMPLOYED"):
        val_slider = st.sidebar.slider(
            params["label"], params["min"], params["max"], step=params["step"], key=col
        )
        client_modifie[col] = -val_slider * 365
    else:
        client_modifie[col] = st.sidebar.slider(
            params["label"], float(params["min"]), float(params["max"]),
            step=float(params["step"]), key=col
        )

# Détection des modifications — comparaison sur les valeurs clampées
cols_existantes = [c for c in VARIABLES_WIF.keys() if c in df.columns]
modifie = False
for col in cols_existantes:
    v_init = valeur_initiale(col, client_row, VARIABLES_WIF[col])
    v_act  = st.session_state.get(col, v_init)
    if col == "DAYS_BIRTH":
        if int(v_init) != int(v_act):
            modifie = True
            break
    else:
        if not np.isclose(float(v_init), float(v_act), atol=1e-3):
            modifie = True
            break

if modifie:
    st.info("⚠️ Les valeurs ont été modifiées par rapport au dossier original.")

# ── Analyse ───────────────────────────────────────────────────────────────────
st.subheader(f"Dossier client {client_id}")

if st.button(f"Lancer l'analyse du dossier {client_id}", type="primary"):
    data_dict = json.loads(client_modifie.to_json())
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
            shap_values_array = np.array(result['shap_values'])
            base_value        = result['base_value']
            feature_names     = result['feature_names']

            # Exclure CODE_GENDER du graphique SHAP
            if 'CODE_GENDER' in feature_names:
                idx = feature_names.index('CODE_GENDER')
                shap_values_array = np.delete(shap_values_array, idx)
                feature_names.pop(idx)

            client_data_values = client_modifie[feature_names].values.astype(float)

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