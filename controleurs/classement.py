# controleurs/classements.py
from model.model_pg import get_classements

# 1. On récupère les filtres passés dans l'URL (GET)
# S'ils n'existent pas, on met 'IJH' et '0' (Général) par défaut
type_c = GET.get('type', ['IJH'])[0]
duree_c = int(GET.get('duree', [0])[0])

# 2. On interroge la base de données
classements_data = get_classements(type_c, duree_c, conn=SESSION.get('CONNEXION'))

# 3. On envoie les données au template HTML
REQUEST_VARS['type'] = type_c
REQUEST_VARS['duree'] = duree_c
REQUEST_VARS['classements'] = classements_data