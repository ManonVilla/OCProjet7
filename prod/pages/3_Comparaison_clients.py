import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data, FEATURES_COMPARAISON, to_years

st.set_page_config(page_title="Comparaison clients", layout="wide")
st.title("📊 Comparaison avec d'autres clients")

# ── Récupération du client sélectionné ───────────────────────────────────────
df = st.session_state.get("df", load_data())
client_id = st.session_state.get("client_id", df['SK_ID_CURR'].iloc[0])

st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox(
    "Sélectionnez un client",
    df['SK_ID_CURR'].unique().astype(int).tolist(),
    index=int((df['SK_ID_CURR'] == client_id).argmax())
)
st.session_state["client_id"] = client_id
client_row = df[df['SK_ID_CURR'] == client_id].iloc[0]

# ── Filtres ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Filtres comparaison")

feats_dispo = {k: v for k, v in FEATURES_COMPARAISON.items() if k in df.columns}

feature_sel = st.sidebar.selectbox(
    "Variable à comparer",
    options=list(feats_dispo.keys()),
    format_func=lambda x: feats_dispo[x]
)

groupe = st.sidebar.radio(
    "Comparer le client à :",
    # options=["Tous les clients", "Clients acceptés (TARGET=0)", "Clients refusés (TARGET=1)"]
    options=["Tous les clients"]
)

# ── Construction du groupe ────────────────────────────────────────────────────
if groupe == "Tous les clients":
    df_groupe    = df.copy()
    label_groupe = "tous les clients"
elif "TARGET" not in df.columns:
    st.warning("⚠️ La colonne TARGET n'est pas disponible dans X_test. La comparaison porte sur tous les clients.")
    df_groupe    = df.copy()
    label_groupe = "tous les clients"
else:
    target_val   = 0 if "acceptés" in groupe else 1
    df_groupe    = df[df["TARGET"] == target_val].copy()
    label_groupe = "clients acceptés" if target_val == 0 else "clients refusés"

st.info(f"👥 Groupe sélectionné : **{label_groupe}** — {len(df_groupe):,} clients")

# ── Histogramme ───────────────────────────────────────────────────────────────
st.markdown(f"### Distribution de **{feats_dispo[feature_sel]}**")

serie      = to_years(df_groupe, feature_sel).dropna()
val_client = to_years(pd.DataFrame([client_row]), feature_sel).iloc[0]

fig_hist = px.histogram(
    serie,
    nbins=50,
    labels={"value": feats_dispo[feature_sel], "count": "Nb clients"},
    opacity=0.75,
    color_discrete_sequence=["#33885E"],
    title=f"Distribution — {label_groupe}"
)
fig_hist.add_vline(
    x=val_client,
    line_dash="dash",
    line_color="red",
    line_width=2,
    annotation_text=f"  Client {client_id}",
    annotation_position="top right"
)
fig_hist.update_layout(
    xaxis_title=feats_dispo[feature_sel],
    yaxis_title="Nombre de clients",
    showlegend=False,
    height=420
)
st.plotly_chart(fig_hist, use_container_width=True)

# ── Statistiques ──────────────────────────────────────────────────────────────
st.markdown("### 📈 Statistiques du groupe")
col_a, col_b, col_c, col_d, col_e = st.columns(5)
col_a.metric("Moyenne",           f"{serie.mean():,.2f}")
col_b.metric("Médiane",           f"{serie.median():,.2f}")
col_c.metric("Min",               f"{serie.min():,.2f}")
col_d.metric("Max",               f"{serie.max():,.2f}")
percentile = (serie < val_client).mean() * 100
col_e.metric("Percentile client", f"{percentile:.1f}e")