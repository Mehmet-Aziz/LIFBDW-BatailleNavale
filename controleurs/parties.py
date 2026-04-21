from model.model_pg import get_adversaires_virtuels, get_distributions, creer_partie_complete

# Récupération de l'environnement de session
conn = SESSION.get('CONNEXION')
id_joueur = SESSION.get('id_joueur')

# Variables pour le template
REQUEST_VARS['adversaires'] = []
REQUEST_VARS['distributions'] = []
REQUEST_VARS['message_succes'] = None
REQUEST_VARS['message_erreur'] = None

if not id_joueur:
    REQUEST_VARS['message_erreur'] = "Accès refusé. Vous devez être connecté pour créer une partie."
else:
    # 1. Chargement des données pour peupler les listes déroulantes (GET)
    REQUEST_VARS['adversaires'] = get_adversaires_virtuels(conn=conn)
    REQUEST_VARS['distributions'] = get_distributions(conn=conn)

    # 2. Traitement du formulaire (POST)
    # Assurez-vous que votre framework expose bien les variables soumises dans un dictionnaire POST
    if 'POST' in globals() and POST:
        id_adversaire = POST.get('id_adversaire')
        nom_distribution = POST.get('nom_distribution')

        if id_adversaire and nom_distribution:
            try:
                # Appel de la logique de création massive (Partie + Pioche + 100 Cartes)
                id_partie = creer_partie_complete(
                    id_joueur=int(id_joueur),
                    id_adversaire=int(id_adversaire),
                    nom_distribution=nom_distribution,
                    conn=conn
                )

                if id_partie:
                    REQUEST_VARS['message_succes'] = f"Ordre de bataille validé ! La partie n°{id_partie} a été créée et la pioche de 100 cartes est initialisée."
                else:
                    REQUEST_VARS['message_erreur'] = "Échec lors de l'enregistrement de la partie en base de données."
            
            except Exception as e:
                REQUEST_VARS['message_erreur'] = f"Une anomalie système est survenue : {e}"
        else:
            REQUEST_VARS['message_erreur'] = "Veuillez sélectionner un adversaire et une distribution."