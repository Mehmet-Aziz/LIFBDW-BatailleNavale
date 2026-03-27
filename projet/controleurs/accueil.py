# On simule des données pour tester le template
# Plus tard, on interrogera le modèle ici [cite: 1713]

REQUEST_VARS['message_bienvenue'] = "Bienvenue sur la Bataille Navale UCBL 2026 !"
REQUEST_VARS['pseudo_joueur'] = SESSION.get('pseudo', 'Invité') # Utilisation de la session [cite: 1827, 1841]