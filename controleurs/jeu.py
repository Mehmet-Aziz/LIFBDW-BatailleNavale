# controleurs/jeu.py
from model.model_pg import get_cases_flottille, initialiser_flottille, execute_query

conn = SESSION.get('CONNEXION')
id_joueur = SESSION.get('id_joueur')

# On récupère l'ID de la partie depuis l'URL (?id_partie=...)
id_partie_get = GET.get('id_partie')
if id_partie_get:
    id_partie = int(id_partie_get[0])
    SESSION['id_partie_courante'] = id_partie
else:
    id_partie = SESSION.get('id_partie_courante')

if not id_joueur or not id_partie:
    self.redirect('/connexion')
else:
    # 1. Vérifier si la flotte du joueur est déjà placée
    cases_occupees = get_cases_flottille(id_partie, id_joueur, conn=conn)
    
    # 2. Si c'est vide (premier chargement de la page pour cette partie)
    if not cases_occupees:
        # Initialiser la flotte du joueur humain
        initialiser_flottille(id_partie, id_joueur, conn=conn)
        
        # Initialiser la flotte de l'IA adverse
        res_adv = execute_query(
            "SELECT id_joueur FROM Participer WHERE id_partie = %s AND id_joueur != %s",
            (id_partie, id_joueur), fetch="one", conn=conn
        )
        if res_adv:
            id_adversaire = res_adv[0]
            initialiser_flottille(id_partie, id_adversaire, conn=conn)
            
        # Mettre la partie "En cours" car les bateaux sont placés
        execute_query("UPDATE Partie SET etat = 'En cours' WHERE id_partie = %s", (id_partie,), fetch=None, conn=conn)
        
        # Recharger les cases maintenant qu'elles existent
        cases_occupees = get_cases_flottille(id_partie, id_joueur, conn=conn)
    
    # 3. Transmettre les données au template
    REQUEST_VARS['id_partie'] = id_partie
    REQUEST_VARS['cases_flotte'] = cases_occupees