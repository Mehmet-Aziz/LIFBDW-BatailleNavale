# controleurs/jeu.py
from model.model_pg import get_connection, initialiser_flottille, get_cases_flottille

id_partie_list = GET.get('id_partie')

if id_partie_list:
    id_partie = int(id_partie_list[0])
    # TODO: Remplacer par l'ID réel via SESSION
    id_joueur = 1 
    
    conn = get_connection()
    if conn:
        # 1. On s'assure que les navires sont créés
        initialiser_flottille(id_partie, id_joueur, conn=conn)
        
        # 2. On récupère la liste des cases occupées par ces navires (ex: ["1-2", "1-3", "1-4"])
        cases_flotte = get_cases_flottille(id_partie, id_joueur, conn=conn)
        
        conn.close()
    
    # 3. On envoie les données au template (HTML)
    REQUEST_VARS['id_partie'] = id_partie
    REQUEST_VARS['cases_flotte'] = cases_flotte
else:
    REQUEST_VARS['erreur'] = "ID de partie manquant"