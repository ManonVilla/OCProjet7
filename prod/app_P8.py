from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
import uvicorn
import shap

app = FastAPI()

with open('modele_final_complet.pkl', 'rb') as f: #'rb' pour préciser qu'il doit le lire sans rien modifier, et pas en mode texte
    model = joblib.load(f)

explainer = shap.TreeExplainer(model)  

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

    seuil_optimal = 0.48
    if float(proba[0][1]) > seuil_optimal:
        decision_finale = 1
    else:
        decision_finale = 0
    
    shap_values = explainer.shap_values(input_data)
    if isinstance(shap_values, list):
        shap_list = shap_values[1][0].tolist()
        base_val = explainer.expected_value[1]
    else:
        shap_list = shap_values[0].tolist()
        base_val = explainer.expected_value
 #shap renvoi un obket numpy qu'il faut convertir en float
    if isinstance(base_val, (list, tuple, np.ndarray)):
        base_val = float(base_val[0])
    else:
        base_val = float(base_val)

    # Renvoyer le résultat au format JSON
    return {
        "prediction": decision_finale,
        "probabilite_remboursement": float(proba[0][0]),
        "probabilite_defaut": float(proba[0][1]),
        "shap_values": shap_list,
        "base_value": base_val,
        "feature_names": input_data.columns.tolist()
        }

#à mettre dans le terminal : uvicorn app:app --reload OU python app.py avec ça : 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)