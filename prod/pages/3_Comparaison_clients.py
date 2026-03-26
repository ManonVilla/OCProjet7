import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
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

# ── Filtres sidebar ───────────────────────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Histogramme (code original conservé, couleurs accessibles)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"### Distribution de **{feats_dispo[feature_sel]}**")

serie      = to_years(df_groupe, feature_sel).dropna()
val_client = to_years(pd.DataFrame([client_row]), feature_sel).iloc[0]

fig_hist = px.histogram(
    serie,
    nbins=50,
    labels={"value": feats_dispo[feature_sel], "count": "Nb clients"},
    opacity=0.75,
    color_discrete_sequence=["#2166AC"],
    title=f"Distribution — {label_groupe}"
)
fig_hist.add_vline(
    x=val_client,
    line_dash="dash",
    line_color="black",
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

# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 2 — Boxplot par tranche d'âge ou de revenu
# # ═══════════════════════════════════════════════════════════════════════════════
# st.markdown("---")
# st.markdown("### 🎻 Boxplot par tranche")

# col1, col2 = st.columns(2)
# with col1:
#     feat_box = st.selectbox(
#         "Variable à analyser",
#         options=list(feats_dispo.keys()),
#         format_func=lambda x: feats_dispo[x],
#         key="feat_box"
#     )
# with col2:
#     tranche_par = st.selectbox(
#         "Découper par tranche de",
#         options=["Âge", "Revenu"],
#         key="tranche_par"
#     )

# try:
#     df_box = df_groupe.copy()
#     df_box["valeur"] = to_years(df_box, feat_box)

#     if tranche_par == "Âge" and "DAYS_BIRTH" in df_box.columns:
#         df_box["Tranche"] = pd.cut(
#             df_box["DAYS_BIRTH"].abs() / 365,
#             bins=[18, 30, 45, 60, 100],
#             labels=["18-30 ans", "30-45 ans", "45-60 ans", "60+ ans"]
#         )
#         age_client = abs(client_row["DAYS_BIRTH"]) / 365
#         if age_client < 30:       tranche_client = "18-30 ans"
#         elif age_client < 45:     tranche_client = "30-45 ans"
#         elif age_client < 60:     tranche_client = "45-60 ans"
#         else:                     tranche_client = "60+ ans"

#     else:  # Revenu
#         quantiles = df_box["AMT_INCOME_TOTAL"].quantile([0, 0.25, 0.5, 0.75, 1.0]).values
#         df_box["Tranche"] = pd.cut(
#             df_box["AMT_INCOME_TOTAL"],
#             bins=quantiles,
#             labels=["Q1 (bas)", "Q2", "Q3", "Q4 (haut)"],
#             duplicates="drop"
#         )
#         revenu_client = client_row["AMT_INCOME_TOTAL"]
#         if revenu_client <= quantiles[1]:     tranche_client = "Q1 (bas)"
#         elif revenu_client <= quantiles[2]:   tranche_client = "Q2"
#         elif revenu_client <= quantiles[3]:   tranche_client = "Q3"
#         else:                                 tranche_client = "Q4 (haut)"

#     val_client_box = to_years(pd.DataFrame([client_row]), feat_box).iloc[0]
#     df_box = df_box.dropna(subset=["Tranche", "valeur"])

#     fig_box = px.box(
#         df_box, x="Tranche", y="valeur",
#         color="Tranche",
#         color_discrete_sequence=["#2166AC", "#5DA8D1", "#D95F02", "#F4A55A"],
#         labels={"valeur": feats_dispo[feat_box], "Tranche": tranche_par},
#         title=f"{feats_dispo[feat_box]} par tranche de {tranche_par.lower()}"
#     )
#     fig_box.add_scatter(
#         x=[tranche_client], y=[val_client_box],
#         mode="markers",
#         marker=dict(color="black", size=12, symbol="diamond"),
#         name=f"Client {client_id}"
#     )
#     fig_box.update_layout(height=450, showlegend=True)
#     st.plotly_chart(fig_box, use_container_width=True)

# except Exception as e:
#     st.error(f"Erreur boxplot : {type(e).__name__} — {e}")

# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 3 — Scatter plot (2 variables numériques)
# # ═══════════════════════════════════════════════════════════════════════════════
# st.markdown("---")
# st.markdown("### 🔵 Scatter plot — 2 variables numériques")

# col1, col2 = st.columns(2)
# with col1:
#     feat_x = st.selectbox(
#         "Variable X",
#         options=list(feats_dispo.keys()),
#         format_func=lambda x: feats_dispo[x],
#         key="feat_x"
#     )
# with col2:
#     feat_y = st.selectbox(
#         "Variable Y",
#         options=list(feats_dispo.keys()),
#         index=1,
#         format_func=lambda x: feats_dispo[x],
#         key="feat_y"
#     )

# df_scatter = df_groupe.sample(min(2000, len(df_groupe)), random_state=42).copy()
# df_scatter["x"] = to_years(df_scatter, feat_x)
# df_scatter["y"] = to_years(df_scatter, feat_y)

# val_x_client = to_years(pd.DataFrame([client_row]), feat_x).iloc[0]
# val_y_client = to_years(pd.DataFrame([client_row]), feat_y).iloc[0]

# fig_scatter = px.scatter(
#     df_scatter, x="x", y="y",
#     opacity=0.3,
#     color_discrete_sequence=["#2166AC"],
#     labels={"x": feats_dispo[feat_x], "y": feats_dispo[feat_y]},
#     title=f"{feats_dispo[feat_x]} vs {feats_dispo[feat_y]} — {label_groupe}"
# )
# fig_scatter.add_scatter(
#     x=[val_x_client], y=[val_y_client],
#     mode="markers",
#     marker=dict(color="black", size=14, symbol="diamond"),
#     name=f"Client {client_id}"
# )
# fig_scatter.update_layout(height=500)
# st.plotly_chart(fig_scatter, use_container_width=True)