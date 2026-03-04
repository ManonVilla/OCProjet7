# OCProjet7

L'objectif de ce projet est d'obtenir un outil de prédiction d'accord ou de refus de prêt par une banque. 

L'outil est stocké dans un docker qui permet son utilisation sur n'importe quel ordinateur et déployé en ligne via FASTAPI https://ocprojet7.onrender.com/docs#/

Il est ensuite utilisable via un dashboard créé via Streamlit : https://ocprojet7-rx3n3fjqjn35kcf3monqcz.streamlit.app/

## Découpage des dossiers : 
- MV_P7_DS_1.ipynb : notebook d'exploration des données
- MV_P7_DS_2.ipynb : notebook de développement du modèle
- graphs.py : fichier python contenant les fonction pour la création des graphiques
- app.py : mise en place de l'API
- Dockerfile.api et Dockerfile.dashboard : mise en place du docker
- requirements.txt : libraries nécessaires pour faire tourner le docker