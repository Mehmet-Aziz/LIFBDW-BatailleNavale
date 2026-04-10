from model.model_pg import get_statistiques_accueil

# On prépare le tiroir 'stats' avec des zéros par défaut
# Comme ça, même si la base de données bug, le HTML ne plante pas
REQUEST_VARS['stats'] = {
    'nb_joueurs': 0,
    'nb_parties': 0,
    'top_joueurs': []
}

# On essaie de remplir avec les vraies statistiques
try:
    data = get_statistiques_accueil()
    if data:
        REQUEST_VARS['stats'] = data
except Exception as e:
    print(f"Erreur stats : {e}")

# Message de bienvenue
pseudo = SESSION.get('pseudo')
REQUEST_VARS['message_bienvenue'] = f"Commandant {pseudo}" if pseudo else "jeune recrue"