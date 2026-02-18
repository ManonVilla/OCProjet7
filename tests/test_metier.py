import pytest
from sklearn.metrics import confusion_matrix

# 1. On replace ta fonction métier ici pour que pytest puisse la lire 
# (Dans un projet plus avancé, on l'importerait depuis un fichier .py externe)
def calcul_score_metier(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    score = (10 * fn) + fp
    return score

# 2. Le Test Unitaire
def test_calcul_score_metier_logique():
    """
    Test pour vérifier que la fonction de coût métier pénalise bien 
    un Faux Négatif 10 fois plus qu'un Faux Positif.
    """
    # On simule 4 clients :
    # Client 1 : Fait défaut (1)
    # Client 2 : Rembourse (0)
    # Client 3 : Fait défaut (1)
    # Client 4 : Rembourse (0)
    y_true = [1, 0, 1, 0]
    
    # Notre modèle prédit :
    # Client 1 : Prédit 0 -> FAUX NÉGATIF (Coût = 10)
    # Client 2 : Prédit 0 -> Vrai Négatif (Coût = 0)
    # Client 3 : Prédit 1 -> Vrai Positif (Coût = 0)
    # Client 4 : Prédit 1 -> FAUX POSITIF (Coût = 1)
    y_pred = [0, 0, 1, 1]
    
    # Le score total calculé devrait donc être 10 + 0 + 0 + 1 = 11
    score_obtenu = calcul_score_metier(y_true, y_pred)
    
    # On vérifie (assert) que le résultat est bien 11
    assert score_obtenu == 11, f"Erreur: Le score attendu était 11, mais on a obtenu {score_obtenu}"