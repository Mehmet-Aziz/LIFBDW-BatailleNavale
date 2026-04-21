from model.model_pg import get_statistiques_accueil, get_stats_joueur, execute_query

# ---> LA CLÉ EST ICI : On récupère la connexion globale du serveur <---
conn = SESSION.get('CONNEXION')

# --- STATISTIQUES GLOBALES ---
REQUEST_VARS['stats'] = {
    'nb_joueurs': 0,
    'nb_parties': 0,
    'top_joueurs': []
}

try:
    # On la passe à notre fonction
    data = get_statistiques_accueil(conn=conn)
    if data:
        REQUEST_VARS['stats'] = data
except Exception as e:
    print(f"Erreur stats globales : {e}")

# --- GESTION DE L'UTILISATEUR CONNECTÉ ---
pseudo = SESSION.get('pseudo')
id_joueur = SESSION.get('id_joueur')

# Sécurité : Si on a le pseudo mais pas l'ID en session, on va le chercher
if pseudo and not id_joueur:
    res_id = execute_query("SELECT id_joueur FROM Joueur WHERE pseudo = %s", (pseudo,), fetch="one", conn=conn)
    if res_id:
        id_joueur = res_id[0]
        SESSION['id_joueur'] = id_joueur

REQUEST_VARS['message_bienvenue'] = f"Commandant {pseudo}" if pseudo else "jeune recrue"

# --- STATISTIQUES PERSONNELLES ---
REQUEST_VARS['stats_joueur'] = None

if id_joueur:
    try:
        # On passe la connexion globale ici aussi
        data_perso = get_stats_joueur(id_joueur, conn=conn)
        if data_perso:
            REQUEST_VARS['stats_joueur'] = data_perso
    except Exception as e:
        print(f"Erreur stats joueur : {e}")