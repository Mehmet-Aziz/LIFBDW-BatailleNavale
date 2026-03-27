"""
Ficher includes chargé avant chaque requête (ex, fonctions utilisées par différents controleurs)
"""

def add_activity(session_histo, activity):
    """
    Ajoute l'activité activity dans l'historique de session avec la date courante (comme clé)
    """
    from datetime import datetime
    d = datetime.now()
    session_histo[d] = activity

