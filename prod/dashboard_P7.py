import streamlit as st
import pandas as pd
import requests
import json

import plotly.graph_objects as go

from graphs import create_gauge_chart

st.set_page_config(
    page_title="Dashboard Projet Scoring",
    layout="wide"
)

SEUIL_OPTIMAL = 0.48

st.title("👩‍💻 Dashboard d'aide à la prise de décision pour les prêts bancaires")

@st.cache_data #pour garder les données en cache et éviter de les recharger à chaque interaction
def load_data():
    # Charger les données depuis le fichier CSV
    df = pd.read_parquet('X_test.parquet')
    return df

df = load_data()

if df is None:
    st.stop()

#Sélection du client dans la barre latérale
st.sidebar.header("🔍 Recherche Client")
client_id = st.sidebar.selectbox("Sélectionnez un client grâce à son identifiant", df['SK_ID_CURR'].unique())

client_row = df[df['SK_ID_CURR'] == client_id].iloc[0]

#Ajouter des infos sur le client si possible
st.subheader(f"Informations sur le client {client_id}")
if st.button(f"Lancer l'analyse du dossier {client_id}", type="primary"):
    data_json_str = client_row.to_json()
    data_dict = json.loads(data_json_str)
    api_url = os.getenv("API_URL", "https://ton-api-p7.onrender.com/predict")
    with st.spinner("Analyse en cours..."):
        response = requests.post(api_url, json={"data": data_dict})
    if response.status_code == 200:
        result = response.json()
        st.success("Analyse terminée !")
        proba = result['probabilite_defaut']
        prediction = result['prediction']
        fig = create_gauge_chart(proba, SEUIL_OPTIMAL)
        if proba > SEUIL_OPTIMAL:
            st.warning("🍂 Crédit refusée : le client présente un risque de défaut élevé.")
        else:
            st.success("🍃 Crédit accordé : le client présente un risque de défaut faible.")
        st.plotly_chart(fig)
    else:
        st.error(f"Erreur lors de l'analyse du dossier. Veuillez réessayer. Code d'erreur : {response.status_code}")

st.write(f"Le seuil de décision est {SEUIL_OPTIMAL}. Les clients avec une probabilité de défaut supérieure à ce seuil sont considérés comme présentant un risque élevé.")

#Attention pour que ça fonctionne, il faut que le serveur FastAPI soit lancé (uvicorn app:app --reload) et que le modèle soit chargé correctement.