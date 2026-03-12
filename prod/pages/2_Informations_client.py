import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from utils import load_data, FEATURES_LISIBLES

st.set_page_config(page_title="Informations client", layout="wide")
st.title("👤 Informations client")

# ── Récupération du client sélectionné ───────────────────────────────────────
df = st.session_state.get("df", load_data())
client_id = st.session_state.get("client_id", df['SK_ID_CURR'].iloc[0])

st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox(
    "Sélectionnez un client",
    df['SK_ID_CURR'].unique(),
    index=int((df['SK_ID_CURR'] == client_id).argmax())
)
st.session_state["client_id"] = client_id
client_row = df[df['SK_ID_CURR'] == client_id].iloc[0]

# ── Fiche client ──────────────────────────────────────────────────────────────
st.subheader(f"📋 Fiche descriptive — Client {client_id}")

cols_dispo = [c for c in FEATURES_LISIBLES if c in df.columns]

if not cols_dispo:
    st.info("Aucune variable descriptive standard trouvée dans le dataset.")
else:
    rows = [cols_dispo[i:i+3] for i in range(0, len(cols_dispo), 3)]
    for row in rows:
        cols_ui = st.columns(3)
        for j, feat in enumerate(row):
            label, formatter = FEATURES_LISIBLES[feat]
            val = client_row[feat]
            try:
                val_fmt = formatter(val) if not pd.isna(val) else "N/A"
            except Exception:
                val_fmt = str(val)
            with cols_ui[j]:
                st.metric(label=label, value=val_fmt)

st.markdown("---")
with st.expander("🔎 Voir toutes les variables brutes du client"):
    client_df = client_row.to_frame(name="Valeur").reset_index()
    client_df.columns = ["Variable", "Valeur"]
    client_df = client_df.astype(str)
    st.dataframe(client_df, use_container_width=True, height=400)