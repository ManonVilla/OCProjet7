from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from typing import Dict, Any
import uvicorn

app = FastAPI()

with open('modele_final_complet.pkl', 'rb') as f: #'rb' pour préciser qu'il doit le lire sans rien modifier, et pas en mode texte
    model = joblib.load(f)

#Pour définir ce que le modèle attend en entrée, on crée une classe qui hérite de BaseModel de Pydantic
class ClientData(BaseModel):
    data: Dict[str, Any]

#Il faut créer l'endpoint des prédictions
@app.post("/predict")
def predict(client_data: ClientData):
    # Convertir les données d'entrée en DataFrame
    input_data = pd.DataFrame([client_data.data])
    colonnes_inutiles = ['Unnamed: 0', 'SK_ID_CURR', 'TARGET']
    
    for col in colonnes_inutiles:
        if col in input_data.columns:
            input_data = input_data.drop(columns=[col])


    # Faire la prédiction avec le modèle chargé
    prediction = model.predict(input_data)
    
    proba = model.predict_proba(input_data)  # Obtenir les probabilités de chaque classe
    
    # Renvoyer le résultat au format JSON
    return {
        "prediction": int(prediction[0]),
        "probabilite_remboursement": float(proba[0][0]),
        "probabilite_defaut": float(proba[0][1])
    }

#à mettre dans le terminal : uvicorn app:app --reload OU python app.py avec ça : 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)