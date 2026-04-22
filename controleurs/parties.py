# controleurs/parties.py
from model.model_pg import get_mes_parties

id_joueur = SESSION.get('id_joueur')

if not id_joueur:
    self.redirect('/connexion')
else:
    # Récupère les parties 'Créée' et 'En cours'
    REQUEST_VARS['mes_parties'] = get_mes_parties(id_joueur)