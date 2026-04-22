# controleurs/tirer.py
import json
from model.model_pg import (
    verifier_impact, creer_tour, enregistrer_tir_db, piocher_carte_partie,
    execute_query, est_navire_coule, calculer_score, ia_jouer_tour
)

id_partie = POST.get('id_partie', [None])[0]
x_val = POST.get('x', [None])[0]
y_val = POST.get('y', [None])[0]
id_joueur = SESSION.get('id_joueur')
conn = SESSION.get('CONNEXION')

if not id_partie or not x_val or not y_val or not id_joueur:
    REQUEST_VARS['json_data'] = json.dumps({"status": "error", "message": "Données manquantes"})
else:
    x, y = int(x_val), int(y_val)
    id_partie = int(id_partie)

    # Identifier l'adversaire (joueur virtuel)
    res_adv = execute_query(
        "SELECT id_joueur FROM Participer WHERE id_partie = %s AND id_joueur != %s",
        (id_partie, id_joueur), fetch="one", conn=conn
    )
    id_adversaire = res_adv[0] if res_adv else None

    if not id_adversaire:
        REQUEST_VARS['json_data'] = json.dumps({"status": "error", "message": "Adversaire introuvable"})
    else:
        # --- TOUR HUMAIN ---
        id_tour_humain = creer_tour(id_partie, id_joueur, conn=conn)
        if not id_tour_humain:
            REQUEST_VARS['json_data'] = json.dumps({"status": "error", "message": "Erreur création tour"})
        else:
            carte_humain = piocher_carte_partie(id_partie, id_joueur, id_tour_humain, conn=conn)
            id_navire, nom_navire = verifier_impact(id_partie, id_adversaire, x, y, conn=conn)
            resultat_humain = "Touché" if id_navire else "Eau"

            if id_navire and est_navire_coule(id_partie, id_adversaire, id_navire, conn=conn):
                resultat_humain = "Coulé"
                execute_query(
                    "UPDATE Composition_Flottille SET etat = 'Coulé' WHERE id_navire = %s AND id_flottille IN "
                    "(SELECT id_flottille FROM Utiliser_Flottille WHERE id_partie = %s AND id_joueur = %s)",
                    (id_navire, id_partie, id_adversaire), conn=conn
                )

            enregistrer_tir_db(id_tour_humain, x, y, resultat_humain, conn=conn)

            # Vérifier si l'humain a gagné
            restants = execute_query(
                "SELECT COUNT(*) FROM Composition_Flottille cf "
                "JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille "
                "WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'",
                (id_partie, id_adversaire), fetch="one", conn=conn
            )
            fin_partie = (restants and restants[0] == 0)

            if fin_partie:
                nb_tirs = execute_query(
                    "SELECT COUNT(*) FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour WHERE tour.id_partie = %s",
                    (id_partie,), fetch="one", conn=conn
                )
                score = calculer_score(nb_tirs[0]) if nb_tirs else 0
                execute_query(
                    "UPDATE Partie SET etat = 'Gagnée', id_vainqueur = %s, score_vainqueur = %s WHERE id_partie = %s",
                    (id_joueur, score, id_partie), conn=conn
                )
                REQUEST_VARS['json_data'] = json.dumps({
                    "status": "success", "resultat": resultat_humain, "carte": carte_humain,
                    "fin_partie": True, "vainqueur": "humain"
                })
            else:
                # --- TOUR DE L'IA ---
                id_tour_ia = creer_tour(id_partie, id_adversaire, conn=conn)
                carte_ia = piocher_carte_partie(id_partie, id_adversaire, id_tour_ia, conn=conn)
                
                # Appel direct à notre fonction IA !
                cible = ia_jouer_tour(id_partie, conn=conn)
                
                if cible:
                    x_ia, y_ia = cible
                    id_navire_ia, _ = verifier_impact(id_partie, id_joueur, x_ia, y_ia, conn=conn)
                    resultat_ia = "Touché" if id_navire_ia else "Eau"

                    if id_navire_ia and est_navire_coule(id_partie, id_joueur, id_navire_ia, conn=conn):
                        resultat_ia = "Coulé"
                        execute_query(
                            "UPDATE Composition_Flottille SET etat = 'Coulé' WHERE id_navire = %s AND id_flottille IN "
                            "(SELECT id_flottille FROM Utiliser_Flottille WHERE id_partie = %s AND id_joueur = %s)",
                            (id_navire_ia, id_partie, id_joueur), conn=conn
                        )

                    enregistrer_tir_db(id_tour_ia, x_ia, y_ia, resultat_ia, conn=conn)

                    # Vérifier si l'IA a gagné
                    restants_humain = execute_query(
                        "SELECT COUNT(*) FROM Composition_Flottille cf "
                        "JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille "
                        "WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'",
                        (id_partie, id_joueur), fetch="one", conn=conn
                    )
                    
                    if restants_humain and restants_humain[0] == 0:
                        nb_tirs_ia = execute_query(
                            "SELECT COUNT(*) FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour "
                            "WHERE tour.id_partie = %s AND tour.id_joueur = %s",
                            (id_partie, id_adversaire), fetch="one", conn=conn
                        )
                        score_ia = calculer_score(nb_tirs_ia[0]) if nb_tirs_ia else 0
                        execute_query(
                            "UPDATE Partie SET etat = 'Perdue', id_vainqueur = %s, score_vainqueur = %s WHERE id_partie = %s",
                            (id_adversaire, score_ia, id_partie), conn=conn
                        )
                        REQUEST_VARS['json_data'] = json.dumps({
                            "status": "success", "resultat": resultat_humain, "carte": carte_humain,
                            "fin_partie": True, "vainqueur": "ia",
                            "tir_ia": {"x": x_ia, "y": y_ia, "resultat": resultat_ia}
                        })
                    else:
                        # La partie continue
                        REQUEST_VARS['json_data'] = json.dumps({
                            "status": "success", "resultat": resultat_humain, "carte": carte_humain,
                            "fin_partie": False,
                            "tir_ia": {"x": x_ia, "y": y_ia, "resultat": resultat_ia}
                        })
                else:
                    # Sécurité si la grille est pleine
                    REQUEST_VARS['json_data'] = json.dumps({
                        "status": "success", "resultat": resultat_humain, "carte": carte_humain,
                        "fin_partie": False
                    })