import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils import load_data

st.set_page_config(
    page_title="Dashboard Scoring Crédit",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Dashboard d'aide à la prise de décision pour les prêts bancaires")
st.markdown("Utilisez la **barre latérale** pour sélectionner un client et naviguer entre les pages.")

# ── Chargement des données ────────────────────────────────────────────────────
df = load_data()
if df is None:
    st.stop()

# ── Sélection du client (partagée via session_state) ─────────────────────────
st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox(
    "Sélectionnez un client",
    df['SK_ID_CURR'].unique()
)

# Stockage dans session_state pour que toutes les pages y aient accès
st.session_state["client_id"] = client_id

st.info("👈 Sélectionnez un client dans la barre latérale, puis naviguez vers une page.")