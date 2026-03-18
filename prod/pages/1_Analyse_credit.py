# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import io
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import streamlit as st
# import pandas as pd
# import requests
# import json
# import shap
# import numpy as np

# from utils import load_data, SEUIL_OPTIMAL, API_URL
# from graphs import create_gauge_chart

# st.set_page_config(page_title="Analyse crédit", layout="wide")
# st.title("🔍 Analyse du dossier crédit")

# # ── Récupération du client sélectionné ───────────────────────────────────────
# df = st.session_state.get("df", load_data())
# client_id = st.session_state.get("client_id", df['SK_ID_CURR'].iloc[0])

# # Resélection possible directement sur cette page
# st.sidebar.header("🔍 Recherche Client")
# client_id = st.sidebar.selectbox(
#     "Sélectionnez un client",
#     df['SK_ID_CURR'].unique().astype(int).tolist(),
#     index=int((df['SK_ID_CURR'] == client_id).argmax())
# )
# st.session_state["client_id"] = client_id
# client_row = df[df['SK_ID_CURR'] == client_id].iloc[0]

# # ── Analyse ───────────────────────────────────────────────────────────────────
# st.subheader(f"Dossier client {client_id}")

# if st.button(f"Lancer l'analyse du dossier {client_id}", type="primary"):
#     data_dict = json.loads(client_row.to_json())
#     with st.spinner("Analyse en cours..."):
#         response = requests.post(API_URL, json={"data": data_dict})

#     if response.status_code == 200:
#         result = response.json()
#         st.success("Analyse terminée !")
#         proba = result['probabilite_defaut']

#         fig = create_gauge_chart(proba, SEUIL_OPTIMAL)
#         if proba > SEUIL_OPTIMAL:
#             st.warning("🍂 Crédit refusé : le client présente un risque de défaut élevé.")
#         else:
#             st.success("🍃 Crédit accordé : le client présente un risque de défaut faible.")
#         st.plotly_chart(fig)

#         st.markdown("---")

#         try:
#             shap_values_array  = np.array(result['shap_values'])
#             base_value         = result['base_value']
#             feature_names      = result['feature_names']
#             client_data_values = client_row[feature_names].values.astype(float)

#             explanation = shap.Explanation(
#                 values=shap_values_array,
#                 base_values=base_value,
#                 data=client_data_values,
#                 feature_names=feature_names
#             )
#             plt.close('all')
#             shap.plots.waterfall(explanation, show=False, max_display=10)
#             fig_shap = plt.gcf()
#             fig_shap.set_size_inches(10, 6)
#             fig_shap.tight_layout()
#             buf = io.BytesIO()
#             fig_shap.savefig(buf, format='png', bbox_inches='tight', dpi=150)
#             buf.seek(0)
#             st.subheader("📌 Facteurs influençant la décision (SHAP)")
#             st.image(buf)
#             plt.close('all')
#         except Exception as e:
#             st.error(f"Erreur SHAP : {e}")
#     else:
#         st.error(f"Erreur lors de l'analyse. Code : {response.status_code}")

# st.caption(f"Seuil de décision : {SEUIL_OPTIMAL}. Au-delà, le risque de défaut est considéré élevé.")

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
    "AMT_INCOME_TOTAL": {"label": "Revenu total (€)",      "min": 10_000,  "max": 1_000_000, "step": 5_000},
    "AMT_CREDIT":       {"label": "Montant du crédit (€)", "min": 10_000,  "max": 2_000_000, "step": 10_000},
    "AMT_ANNUITY":      {"label": "Annuité (€)",           "min": 1_000,   "max": 200_000,   "step": 1_000},
    "DAYS_BIRTH":       {"label": "Âge (années)",          "min": 18,      "max": 70,        "step": 1},
    "EXT_SOURCE_2":     {"label": "Score externe 2",       "min": 0.0,     "max": 1.0,       "step": 0.01},
    "EXT_SOURCE_3":     {"label": "Score externe 3",       "min": 0.0,     "max": 1.0,       "step": 0.01},
}

def get_slider_value(val, params):
    """Retourne une valeur clampée et valide pour le slider, avec fallback si NaN."""
    v = float(np.clip(val, params["min"], params["max"]))
    return float(params["min"]) if np.isnan(v) else v

client_modifie = client_row.copy()

for col, params in VARIABLES_WIF.items():
    if col not in df.columns:
        continue

    if col == "DAYS_BIRTH":
        age_original = int(abs(client_row[col]) / 365)
        age_original = int(np.clip(age_original, params["min"], params["max"]))
        age_slider = st.sidebar.slider(params["label"], params["min"], params["max"], age_original, params["step"])
        client_modifie[col] = -age_slider * 365
    elif col in ("EXT_SOURCE_2", "EXT_SOURCE_3"):
        val = get_slider_value(client_row[col], params)
        client_modifie[col] = st.sidebar.slider(params["label"], float(params["min"]), float(params["max"]), val, float(params["step"]))
    else:
        val = get_slider_value(client_row[col], params)
        client_modifie[col] = st.sidebar.slider(params["label"], float(params["min"]), float(params["max"]), val, float(params["step"]))

# Détection des modifications
cols_existantes = [c for c in VARIABLES_WIF.keys() if c in df.columns]
modifie = not client_row[cols_existantes].equals(client_modifie[cols_existantes])
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
            shap_values_array  = np.array(result['shap_values'])
            base_value         = result['base_value']
            feature_names      = result['feature_names']
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