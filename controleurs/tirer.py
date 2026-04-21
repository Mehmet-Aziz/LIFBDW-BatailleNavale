# controleurs/tirer.py
import json
import random

# Ton serveur lit le POST et met les valeurs dans le dictionnaire global POST.
# Ce sont des listes, on prend donc le premier élément [0].
x_val = POST.get('x', ['0'])[0]
y_val = POST.get('y', ['0'])[0]
id_partie_val = POST.get('id_partie', ['0'])[0]

x = int(x_val)
y = int(y_val)
id_partie = int(id_partie_val)

# ---------------------------------------------------------------
# ÉTAPE SUIVANTE : Mettre la vraie logique SQL ici.
# Pour l'instant on simule le résultat.
# ---------------------------------------------------------------
resultat = random.choice(["Eau", "Touché", "Eau", "Coulé"]) 

# On prépare la réponse
reponse = {
    "status": "success",
    "resultat": resultat,
    "x": x,
    "y": y
}

# On place le JSON dans REQUEST_VARS pour que api_reponse.html l'affiche
REQUEST_VARS['json_data'] = json.dumps(reponse)