import json
import random
import model.model_pg as db

def calculer_nouveau_score(id_partie, id_joueur_score, conn):
    """Calcul précis du score : 100 * (17 / Total)"""
    import model.model_pg as db # Sécurisation du scope due au exec() de server.py
    query = """
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN t.resultat IN ('Touché', 'Coulé') THEN 1 ELSE 0 END) as touches 
        FROM Tir t 
        JOIN Tour tour ON t.id_tour = tour.id_tour 
        WHERE tour.id_partie = %s AND tour.id_joueur = %s
    """
    res = db.execute_query(query, (id_partie, id_joueur_score), fetch="one", conn=conn)
    if not res or res[0] == 0: return 0
    total = res[0]
    touches = res[1] or 0
    return int(100 * (touches / total))

def appliquer_oups(id_partie, id_tireur, id_tour, conn):
    """Effet de Mauvaise Manip (C_OUPS) : Touche un de ses propres navires au hasard."""
    import random
    import model.model_pg as db # Sécurisation du scope
    query = """
        SELECT cf.x, cf.y 
        FROM Composition_Flottille cf
        JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'
    """
    cases_propres = db.execute_query(query, (id_partie, id_tireur), conn=conn)
    if cases_propres:
        case = random.choice(cases_propres)
        cx, cy = case[0], case[1]
        
        id_navire, _ = db.verifier_impact(id_partie, id_tireur, cx, cy, conn=conn)
        res_tir = "Touché"
        if id_navire and db.est_navire_coule(id_partie, id_tireur, id_navire, conn=conn):
            res_tir = "Coulé"
            db.couler_navire(id_partie, id_tireur, id_navire, conn=conn)
        db.enregistrer_tir_db(id_tour, cx, cy, res_tir, conn=conn)
        return {"x": cx, "y": cy, "resultat": res_tir}
    return None

def appliquer_tirs_carte(code_carte, x_centre, y_centre, id_partie, id_tireur, id_cible, id_tour, conn):
    """Génère les multiples impacts en fonction de la carte (Méga-bombe, Etoile...)"""
    import model.model_pg as db # Sécurisation du scope
    cases_a_viser = []
    
    if code_carte == 'C_MEGA': # 9 cases
        cases_a_viser = [(x_centre + dx, y_centre + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
    elif code_carte == 'C_ETOILE': # 25 cases
        cases_a_viser = [(x_centre + dx, y_centre + dy) for dx in [-2, -1, 0, 1, 2] for dy in [-2, -1, 0, 1, 2]]
    else: # 1 case classique
        cases_a_viser = [(x_centre, y_centre)]
        
    impacts = []
    for cx, cy in cases_a_viser:
        if 1 <= cx <= 10 and 1 <= cy <= 10:
            id_piege, type_piege = db.verifier_piege(id_partie, id_cible, cx, cy, conn)
            
            if id_piege:
                db.execute_query("UPDATE Contenu_Grille SET etat = 'Détruit' WHERE id_contenu = %s", (id_piege,), fetch=None, conn=conn)
                if type_piege == 'Orque':
                    res_tir = 'Orque'
                    db.detruire_plus_petits_navires(id_partie, id_tireur, 3, conn)
                else:
                    res_tir = 'Leurre'
            else:
                id_navire, _ = db.verifier_impact(id_partie, id_cible, cx, cy, conn=conn)
                res_tir = "Touché" if id_navire else "Eau"
                
                if id_navire and db.est_navire_coule(id_partie, id_cible, id_navire, conn=conn):
                    res_tir = "Coulé"
                    db.couler_navire(id_partie, id_cible, id_navire, conn=conn)
            
            db.enregistrer_tir_db(id_tour, cx, cy, res_tir, conn=conn)
            impacts.append({"x": cx, "y": cy, "resultat": res_tir})
            
    return impacts

# ==============================================================================
# LOGIQUE PRINCIPALE DU CONTRÔLEUR
# ==============================================================================
id_partie = POST.get('id_partie', [None])[0]
x_val = POST.get('x', [None])[0]
y_val = POST.get('y', [None])[0]
est_rejoue = POST.get('rejoue', [None])[0]
id_joueur = SESSION.get('id_joueur')
conn = SESSION.get('CONNEXION')

# Vérification rigoureuse des paramètres POST pour éviter "Données manquantes"
if not id_partie:
    err = "Paramètre 'id_partie' manquant dans la requête. Le front-end a échoué."
elif not x_val or not y_val:
    err = "Coordonnées de tir (x, y) manquantes."
elif not id_joueur:
    err = "Session expirée. Veuillez vous reconnecter."
else:
    err = None

if err:
    REQUEST_VARS['json_data'] = json.dumps({"status": "error", "message": err})
else:
    x, y = int(x_val), int(y_val)
    id_partie = int(id_partie)

    res_adv = db.execute_query(
        "SELECT id_joueur FROM Participer WHERE id_partie = %s AND id_joueur != %s",
        (id_partie, id_joueur), fetch="one", conn=conn
    )
    id_adversaire = res_adv[0] if res_adv else None

    if not id_adversaire:
        REQUEST_VARS['json_data'] = json.dumps({"status": "error", "message": "Adversaire introuvable"})
    else:
        ia_doit_jouer = True
        impacts_humain = []
        extra_humain = {}
        code_carte_humain = 'C_MISSILE'
        nom_carte_humain = "Tir Classique"
        resultat_humain = "Eau"

        # ==========================================
        # TOUR DU JOUEUR HUMAIN
        # ==========================================
        if est_rejoue:
            nom_carte_humain = "Tir Supplémentaire (Bonus)"
            id_tour_humain = db.creer_tour(id_partie, id_joueur, conn=conn)
            impacts_humain = appliquer_tirs_carte('C_MISSILE', x, y, id_partie, id_joueur, id_adversaire, id_tour_humain, conn)
            
            # Contournement de l'erreur de scope liée à exec() en Python
            res_centre = None
            for imp in impacts_humain:
                if imp['x'] == x and imp['y'] == y:
                    res_centre = imp
                    break
            
            if res_centre: 
                resultat_humain = res_centre['resultat']
        else:
            id_tour_humain = db.creer_tour(id_partie, id_joueur, conn=conn)
            code_carte_humain, nom_carte_humain = db.piocher_carte_partie(id_partie, id_joueur, id_tour_humain, conn=conn)
            
            # Application des cartes
            if code_carte_humain == 'C_PASSE':
                resultat_humain = "Passe"
            elif code_carte_humain == 'C_OUPS':
                resultat_humain = "Mauvaise Manip"
                imp = appliquer_oups(id_partie, id_joueur, id_tour_humain, conn)
                if imp: 
                    impacts_humain.append(imp)
                    extra_humain['oups'] = imp
            elif code_carte_humain == 'C_VIDE':
                id_navire, _ = db.verifier_impact(id_partie, id_adversaire, x, y, conn=conn)
                resultat_humain = "Sonde"
                extra_humain['vide_resultat'] = (id_navire is None)
                ia_doit_jouer = False 
            else:
                if code_carte_humain == 'C_WILLY':
                    extra_humain['willy'] = db.placer_piege(id_partie, id_joueur, 'Orque', conn)
                elif code_carte_humain == 'C_LEURRE':
                    extra_humain['leurre'] = db.placer_piege(id_partie, id_joueur, 'Leurre', conn)
                elif code_carte_humain == 'C_MPM':
                    extra_humain['mpm'] = db.appliquer_mpm(id_partie, id_joueur, id_adversaire, conn)

                impacts_humain = appliquer_tirs_carte(code_carte_humain, x, y, id_partie, id_joueur, id_adversaire, id_tour_humain, conn)
                
                # Contournement de l'erreur de scope liée à exec() en Python
                res_centre = None
                for imp in impacts_humain:
                    if imp['x'] == x and imp['y'] == y:
                        res_centre = imp
                        break

                if res_centre: 
                    resultat_humain = res_centre['resultat']
                
                if code_carte_humain == 'C_REJOUE':
                    extra_humain['rejoue'] = True
                    ia_doit_jouer = False # Le tour s'arrête là, le front-end va refaire un appel AJAX

        fin_partie = db.est_flotte_detruite(id_partie, id_adversaire, conn)
        vainqueur = "humain" if fin_partie else None

        # ==========================================
        # TOUR DE L'IA
        # ==========================================
        tir_ia_data = {"impacts": []}
        if not fin_partie and ia_doit_jouer:
            # Si le joueur a passé son tour, l'IA joue 2 fois
            tours_ia_restants = 2 if code_carte_humain == 'C_PASSE' else 1
            
            while tours_ia_restants > 0 and not fin_partie:
                tours_ia_restants -= 1
                id_tour_ia = db.creer_tour(id_partie, id_adversaire, conn=conn)
                code_carte_ia, nom_carte_ia = db.piocher_carte_partie(id_partie, id_adversaire, id_tour_ia, conn=conn)
                
                tir_ia_data["carte"] = code_carte_ia
                tir_ia_data["nom_carte"] = nom_carte_ia

                if code_carte_ia == 'C_PASSE':
                    tir_ia_data["passe"] = True
                elif code_carte_ia == 'C_OUPS':
                    imp = appliquer_oups(id_partie, id_adversaire, id_tour_ia, conn)
                    if imp: tir_ia_data["oups"] = imp
                elif code_carte_ia == 'C_VIDE':
                    tours_ia_restants += 1
                else:
                    if code_carte_ia == 'C_WILLY':
                        db.placer_piege(id_partie, id_adversaire, 'Orque', conn)
                    elif code_carte_ia == 'C_LEURRE':
                        db.placer_piege(id_partie, id_adversaire, 'Leurre', conn)
                    elif code_carte_ia == 'C_MPM':
                        db.appliquer_mpm(id_partie, id_adversaire, id_joueur, conn)

                    cible = db.ia_jouer_tour(id_partie, conn=conn)
                    if cible:
                        cx, cy = cible
                        impacts_ia = appliquer_tirs_carte(code_carte_ia, cx, cy, id_partie, id_adversaire, id_joueur, id_tour_ia, conn)
                        tir_ia_data["impacts"].extend(impacts_ia)
                        if code_carte_ia == 'C_REJOUE':
                            tours_ia_restants += 1

                fin_partie = db.est_flotte_detruite(id_partie, id_joueur, conn)
                if fin_partie:
                    vainqueur = "ia"

        # Fin de Partie globale
        if fin_partie:
            id_v = id_joueur if vainqueur == "humain" else id_adversaire
            id_p = id_adversaire if vainqueur == "humain" else id_joueur
            score_v = calculer_nouveau_score(id_partie, id_v, conn)
            score_p = calculer_nouveau_score(id_partie, id_p, conn)
            db.execute_query("UPDATE Partie SET etat = 'Terminé', id_vainqueur = %s, score_vainqueur = %s, score_perdant = %s WHERE id_partie = %s", (id_v, score_v, score_p, id_partie), conn=conn)

        # Envoi JSON strictement formaté pour jeu.html
        REQUEST_VARS['json_data'] = json.dumps({
            "status": "success",
            "code_carte": code_carte_humain,
            "carte": nom_carte_humain,
            "resultat": resultat_humain,
            "impacts": impacts_humain,
            "extra": extra_humain,
            "fin_partie": fin_partie,
            "vainqueur": vainqueur,
            "tir_ia": tir_ia_data if (ia_doit_jouer and not (fin_partie and vainqueur == 'humain')) else None
        })