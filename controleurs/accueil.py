from model.model_pg import get_statistiques_accueil, get_stats_joueur, execute_query, get_adversaires_virtuels, get_distributions, creer_partie_complete

# ---> Connexion globale du serveur <---
conn = SESSION.get('CONNEXION')

# --- 1. STATISTIQUES GLOBALES ---
REQUEST_VARS['stats'] = {
    'nb_joueurs': 0,
    'nb_parties': 0,
    'top_joueurs': []
}

try:
    data = get_statistiques_accueil(conn=conn)
    if data:
        REQUEST_VARS['stats'] = data
except Exception as e:
    print(f"Erreur stats globales : {e}")

# --- 2. GESTION DE L'UTILISATEUR CONNECTÉ ---
pseudo = SESSION.get('pseudo')
id_joueur = SESSION.get('id_joueur')

if pseudo and not id_joueur:
    res_id = execute_query("SELECT id_joueur FROM Joueur WHERE pseudo = %s", (pseudo,), fetch="one", conn=conn)
    if res_id:
        id_joueur = res_id[0]
        SESSION['id_joueur'] = id_joueur

REQUEST_VARS['message_bienvenue'] = f"Commandant {pseudo}" if pseudo else "jeune recrue"

# --- 3. STATISTIQUES PERSONNELLES ---
REQUEST_VARS['stats_joueur'] = None

if id_joueur:
    try:
        data_perso = get_stats_joueur(id_joueur, conn=conn)
        if data_perso:
            REQUEST_VARS['stats_joueur'] = data_perso
    except Exception as e:
        print(f"Erreur stats joueur : {e}")


# ====================================================================
# --- 4. NOUVEAU : LOGIQUE DE CRÉATION DE PARTIE (Étape 2) ---
# ====================================================================
REQUEST_VARS['adversaires'] = []
REQUEST_VARS['distributions'] = []
REQUEST_VARS['message_succes'] = None
REQUEST_VARS['message_erreur_partie'] = None

if id_joueur:
    # Récupération des données pour les listes déroulantes
    REQUEST_VARS['adversaires'] = get_adversaires_virtuels(conn=conn)
    REQUEST_VARS['distributions'] = get_distributions(conn=conn)

    # Si le formulaire de création de partie a été soumis
    if 'POST' in globals() and POST:
        id_adversaire = POST.get('id_adversaire')
        nom_distribution = POST.get('nom_distribution')

        # --- CORRECTION ICI : Gestion des listes ---
        # Si le serveur renvoie une liste (ex: ['1']), on extrait le premier élément
        if isinstance(id_adversaire, list):
            id_adversaire = id_adversaire[0]
        if isinstance(nom_distribution, list):
            nom_distribution = nom_distribution[0]
        # -------------------------------------------

        if id_adversaire and nom_distribution:
            try:
                # Création de la partie, de la pioche et des 100 cartes
                id_partie = creer_partie_complete(
                    id_joueur=int(id_joueur),
                    id_adversaire=int(id_adversaire),
                    nom_distribution=nom_distribution,
                    conn=conn
                )

                if id_partie:
                    REQUEST_VARS['message_succes'] = f"Ordre de bataille validé ! La partie n°{id_partie} a été créée et 100 cartes ont été générées."
                else:
                    REQUEST_VARS['message_erreur_partie'] = "Échec lors de l'enregistrement en base de données."
            
            except Exception as e:
                REQUEST_VARS['message_erreur_partie'] = f"Une anomalie est survenue : {e}"