import psycopg
import tomllib
from logzero import logger
import random
import math

# =====================================================================
# CONFIGURATION DU SCHÉMA (Modifie "public" par "batnav" si besoin)
# =====================================================================
SCHEMA_NAME = "public" 

def get_connection():
    try:
        with open("config-bd.toml", "rb") as f:
            config = tomllib.load(f)
        
        conn = psycopg.connect(
            host=config["POSTGRESQL_SERVER"],
            user=config["POSTGRESQL_USER"],
            password=config["POSTGRESQL_PASSWORD"],
            dbname=config["POSTGRESQL_DATABASE"],
            autocommit=True
        )
        # On définit le schéma dès la connexion
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {SCHEMA_NAME};")
        return conn
    except Exception as e:
        logger.error(f"Impossible de se connecter : {e}")
        return None

def execute_query(query, params=None, fetch="all", conn=None):
    close_after = False
    if not conn:
        conn = get_connection()
        close_after = True
    if not conn: return None
    try:
        with conn.cursor() as cur:
            # Sécurité supplémentaire : on force le schéma avant chaque requête
            cur.execute(f"SET search_path TO {SCHEMA_NAME};")
            cur.execute(query, params)
            res = None
            if fetch == "one":
                res = cur.fetchone()
            elif fetch == "all":
                res = cur.fetchall()
        if close_after:
            conn.close()
        return res
    except Exception as e:
        logger.error(f"Erreur SQL : {e}\nRequête: {query}")
        if close_after and conn:
            conn.close()
        return None

# =====================================================================
# STATISTIQUES ET ACCUEIL
# =====================================================================
def get_statistiques_accueil(conn=None):
    stats = {'nb_joueurs': 0, 'nb_parties': 0, 'top_joueurs': []}
    res_j = execute_query("SELECT COUNT(*) FROM Joueur", fetch="one", conn=conn)
    if res_j: stats['nb_joueurs'] = res_j[0]
    res_p = execute_query("SELECT COUNT(*) FROM Partie", fetch="one", conn=conn)
    if res_p: stats['nb_parties'] = res_p[0]
    query_top = """
        SELECT j.pseudo, COUNT(p.id_partie) as victoires
        FROM Joueur j
        JOIN Partie p ON j.id_joueur = p.id_vainqueur
        GROUP BY j.pseudo 
        ORDER BY victoires DESC LIMIT 3
    """
    res_top = execute_query(query_top, conn=conn)
    if res_top: stats['top_joueurs'] = res_top
    return stats

def get_stats_joueur(id_joueur, conn=None):
    stats = {'parties_finies_3m': 0, 'stats_contre_ia': {'victoires': 0, 'defaites': 0}, 'moyenne_tours': 0, 'points_2026': 0, 'cartes_tirees': []}
    q1 = "SELECT COUNT(*) FROM Partie p JOIN Participer pa ON p.id_partie = pa.id_partie WHERE pa.id_joueur = %s AND p.etat IN ('Gagnée', 'Perdue', 'Terminé') AND p.date_heure >= CURRENT_DATE - INTERVAL '3 months'"
    res1 = execute_query(q1, (id_joueur,), fetch="one", conn=conn)
    if res1: stats['parties_finies_3m'] = res1[0]
    q2 = """
        SELECT COUNT(CASE WHEN p.id_vainqueur = %s THEN 1 END) as victoires, COUNT(CASE WHEN p.id_vainqueur != %s AND p.id_vainqueur IS NOT NULL THEN 1 END) as defaites
        FROM Partie p JOIN Participer pa_joueur ON p.id_partie = pa_joueur.id_partie JOIN Participer pa_adv ON p.id_partie = pa_adv.id_partie JOIN Virtuel v ON pa_adv.id_joueur = v.id_joueur
        WHERE pa_joueur.id_joueur = %s AND p.etat IN ('Gagnée', 'Perdue', 'Terminé')
    """
    res2 = execute_query(q2, (id_joueur, id_joueur, id_joueur), fetch="one", conn=conn)
    if res2: stats['stats_contre_ia'] = {'victoires': res2[0] or 0, 'defaites': res2[1] or 0}
    q3 = "SELECT COALESCE(ROUND(AVG(nb_tours), 1), 0) FROM (SELECT id_partie, COUNT(*) as nb_tours FROM Tour WHERE id_joueur = %s GROUP BY id_partie) sub"
    res3 = execute_query(q3, (id_joueur,), fetch="one", conn=conn)
    if res3: stats['moyenne_tours'] = float(res3[0])
    q4 = "SELECT COALESCE(SUM(CASE WHEN p.id_vainqueur = %s THEN p.score_vainqueur ELSE p.score_perdant END), 0) FROM Partie p JOIN Participer pa ON p.id_partie = pa.id_partie WHERE pa.id_joueur = %s AND EXTRACT(YEAR FROM p.date_heure) = 2026 AND p.etat IN ('Gagnée', 'Perdue', 'Terminé')"
    res4 = execute_query(q4, (id_joueur, id_joueur), fetch="one", conn=conn)
    if res4: stats['points_2026'] = int(res4[0])
    q5 = "SELECT tc.nom, COUNT(c.id_carte) as nb_tirees FROM Carte c JOIN Type_Carte tc ON c.code_type_carte = tc.code WHERE c.id_joueur_piocheur = %s GROUP BY tc.nom ORDER BY nb_tirees DESC"
    res5 = execute_query(q5, (id_joueur,), conn=conn)
    if res5: stats['cartes_tirees'] = res5
    return stats

def get_classements(type_classement, duree_mois=0, conn=None):
    """
    Calcule le classement en temps réel à partir de la table Partie.
    type_classement: 'IJH' (Joueurs) ou 'CPP' (Pavillons)
    duree_mois: 0 pour tout, sinon filtre sur les X derniers mois.
    """
    
    # Clause de filtrage temporel
    interval_clause = ""
    if duree_mois > 0:
        interval_clause = f"AND p.date_heure >= CURRENT_DATE - INTERVAL '{duree_mois} month'"

    if type_classement == 'IJH':
        # On additionne les scores vainqueurs et perdants par joueur
        query = f"""
            SELECT 
                RANK() OVER (ORDER BY SUM(score) DESC) as rang,
                pseudo,
                SUM(score) as score_total
            FROM (
                -- Points gagnés en tant que vainqueur
                SELECT j.pseudo, COALESCE(p.score_vainqueur, 0) as score
                FROM Partie p
                JOIN Joueur j ON p.id_vainqueur = j.id_joueur
                WHERE p.etat IN ('Terminé', 'Gagnée', 'Perdue') {interval_clause}
                
                UNION ALL
                
                -- Points gagnés en tant que perdant
                SELECT j.pseudo, COALESCE(p.score_perdant, 0) as score
                FROM Partie p
                JOIN Participer pa ON p.id_partie = pa.id_partie
                JOIN Joueur j ON pa.id_joueur = j.id_joueur
                WHERE p.etat IN ('Terminé', 'Gagnée', 'Perdue') 
                  AND (p.id_vainqueur IS NULL OR pa.id_joueur != p.id_vainqueur)
                  {interval_clause}
            ) sub
            GROUP BY pseudo
            ORDER BY score_total DESC
            LIMIT 50
        """
    elif type_classement == 'CPP':
        # On additionne les scores par pays (Pavillon)
        query = f"""
            SELECT 
                RANK() OVER (ORDER BY SUM(score) DESC) as rang,
                nom_pays,
                SUM(score) as score_total
            FROM (
                -- Score du vainqueur associé à son pavillon dans la partie
                SELECT pv.nom_pays, COALESCE(p.score_vainqueur, 0) as score
                FROM Partie p
                JOIN Utiliser_Flottille uf ON p.id_partie = uf.id_partie AND uf.id_joueur = p.id_vainqueur
                JOIN Flottille_Nationale fn ON uf.id_flottille = fn.id_flottille
                JOIN Pavillon pv ON fn.code_pays = pv.code_pays
                WHERE p.etat IN ('Terminé', 'Gagnée', 'Perdue') {interval_clause}
                
                UNION ALL
                
                -- Score du perdant associé à son pavillon dans la partie
                SELECT pv.nom_pays, COALESCE(p.score_perdant, 0) as score
                FROM Partie p
                JOIN Participer pa ON p.id_partie = pa.id_partie
                JOIN Utiliser_Flottille uf ON p.id_partie = uf.id_partie AND uf.id_joueur = pa.id_joueur
                JOIN Flottille_Nationale fn ON uf.id_flottille = fn.id_flottille
                JOIN Pavillon pv ON fn.code_pays = pv.code_pays
                WHERE p.etat IN ('Terminé', 'Gagnée', 'Perdue') 
                  AND (p.id_vainqueur IS NULL OR pa.id_joueur != p.id_vainqueur)
                  {interval_clause}
            ) sub
            GROUP BY nom_pays
            ORDER BY score_total DESC
        """
    else:
        return []

    return execute_query(query, conn=conn)

# =====================================================================
# CRÉATION ET LOGIQUE DE JEU
# =====================================================================
def get_adversaires_virtuels(conn=None):
    query = "SELECT j.id_joueur, j.pseudo, v.niveau FROM Virtuel v JOIN Joueur j ON v.id_joueur = j.id_joueur ORDER BY CASE v.niveau WHEN 'Faible' THEN 1 WHEN 'Intermédiaire' THEN 2 WHEN 'Expert' THEN 3 END;"
    return execute_query(query, conn=conn)

def get_distributions(conn=None):
    res = execute_query("SELECT nom FROM Distribution ORDER BY nom", conn=conn)
    return [row[0] for row in res] if res else []

def get_mes_parties(id_joueur):
    query = "SELECT p.id_partie, p.etat, p.date_heure FROM Partie p JOIN Participer pa ON p.id_partie = pa.id_partie WHERE pa.id_joueur = %s AND p.etat IN ('Créée', 'En cours') ORDER BY p.date_heure DESC"
    return execute_query(query, (id_joueur,)) or []

def creer_partie_complete(id_joueur, id_adversaire, nom_distribution, conn=None):
    close_after = False
    if not conn:
        conn = get_connection()
        close_after = True
    if not conn: return None
    original_autocommit = conn.autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {SCHEMA_NAME};")
            cur.execute("INSERT INTO Partie (etat) VALUES ('Créée') RETURNING id_partie")
            id_partie = cur.fetchone()[0]

            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_joueur))
            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_adversaire))

            for j_id in [id_joueur, id_adversaire]:
                for _ in range(2):
                    cur.execute("INSERT INTO Grille (nb_lignes, nb_colonnes) VALUES (10, 10) RETURNING id_grille")
                    id_g = cur.fetchone()[0]
                    cur.execute("INSERT INTO Grille_Partie (id_partie, id_joueur, id_grille) VALUES (%s, %s, %s)", (id_partie, j_id, id_g))

            cur.execute("INSERT INTO Pioche (nom_distribution, id_partie) VALUES (%s, %s) RETURNING id_pioche", (nom_distribution, id_partie))
            id_pioche = cur.fetchone()[0]
            cur.execute("UPDATE Partie SET id_pioche = %s WHERE id_partie = %s", (id_pioche, id_partie))

            cur.execute("SELECT pourcentage_missile, pourcentage_rejoue, pourcentage_vide, pourcentage_mpm, pourcentage_leurre, pourcentage_willy, pourcentage_mega, pourcentage_etoile, pourcentage_passe, pourcentage_oups FROM Distribution WHERE nom = %s", (nom_distribution,))
            dist = cur.fetchone()
            
            codes_types = ['C_MISSILE', 'C_REJOUE', 'C_VIDE', 'C_MPM', 'C_LEURRE', 'C_WILLY', 'C_MEGA', 'C_ETOILE', 'C_PASSE', 'C_OUPS']
            deck = []
            for i in range(10):
                deck.extend([codes_types[i]] * dist[i])

            random.shuffle(deck)
            cartes_data = [(code, id_pioche, rang) for rang, code in enumerate(deck, start=1)]
            cur.executemany("INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition) VALUES (%s, %s, %s)", cartes_data)
            conn.commit()
            return id_partie
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur création partie : {e}")
        return None
    finally:
        conn.autocommit = original_autocommit
        if close_after: conn.close()

def initialiser_flottille(id_partie, id_joueur, conn=None):
    try:
        id_flottille = execute_query("INSERT INTO Flottille (type) VALUES ('Nationale') RETURNING id_flottille", fetch="one", conn=conn)[0]
        execute_query("INSERT INTO Utiliser_Flottille (id_partie, id_joueur, id_flottille) VALUES (%s, %s, %s)", (id_partie, id_joueur, id_flottille), fetch=None, conn=conn)

        tailles_requises = [5, 4, 3, 3, 2]
        navires_a_placer = []
        tous_navires = execute_query("SELECT id_navire, taille FROM Navire", conn=conn)
        
        if not tous_navires or len(tous_navires) < 5:
            return False

        navs_dispos = list(tous_navires)
        for t in tailles_requises:
            for nav in navs_dispos:
                if nav[1] == t:
                    navires_a_placer.append({'id_navire': nav[0], 'taille': nav[1]})
                    navs_dispos.remove(nav) 
                    break

        cases_occupees = set()
        for navire in navires_a_placer:
            taille = navire['taille']
            place = False
            while not place:
                sens = random.choice(['H', 'V'])
                if sens == 'H':
                    x, y = random.randint(1, 11 - taille), random.randint(1, 10)
                    cases_testees = [(x + i, y) for i in range(taille)]
                else:
                    x, y = random.randint(1, 10), random.randint(1, 11 - taille)
                    cases_testees = [(x, y + i) for i in range(taille)]
                
                if all(case not in cases_occupees for case in cases_testees):
                    cases_occupees.update(cases_testees)
                    execute_query("INSERT INTO Composition_Flottille (id_flottille, id_navire, x, y, sens, etat) VALUES (%s, %s, %s, %s, %s, %s)", (id_flottille, navire['id_navire'], x, y, sens, 'Opérationnel'), fetch=None, conn=conn)
                    place = True
        return True
    except Exception as e:
        logger.error(f"Erreur init flottille : {e}")
        return False

def get_cases_flottille(id_partie, id_joueur, conn=None):
    cases_occupees = []
    query = """
        SELECT cf.x, cf.y, cf.sens, n.taille
        FROM Composition_Flottille cf JOIN Navire n ON cf.id_navire = n.id_navire JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        WHERE uf.id_partie = %s AND uf.id_joueur = %s
    """
    res = execute_query(query, (id_partie, id_joueur), conn=conn)
    if res:
        for x_start, y_start, sens, taille in res:
            for i in range(taille):
                if sens == 'H': cases_occupees.append(f"{x_start + i}-{y_start}")
                else: cases_occupees.append(f"{x_start}-{y_start + i}")
    return cases_occupees

def creer_tour(id_partie, id_joueur, conn=None):
    res = execute_query("SELECT COALESCE(MAX(numero_ordre), 0) + 1 FROM Tour WHERE id_partie = %s AND id_joueur = %s", (id_partie, id_joueur), fetch="one", conn=conn)
    numero_ordre = res[0] if res else 1
    res_insert = execute_query("INSERT INTO Tour (id_partie, id_joueur, numero_ordre) VALUES (%s, %s, %s) RETURNING id_tour", (id_partie, id_joueur, numero_ordre), fetch="one", conn=conn)
    return res_insert[0] if res_insert else None

def enregistrer_tir_db(id_tour, x, y, resultat, conn=None):
    execute_query("INSERT INTO Tir (id_tour, x, y, resultat) VALUES (%s, %s, %s, %s)", (id_tour, x, y, resultat), fetch=None, conn=conn)

def piocher_carte_partie(id_partie, id_joueur, id_tour, conn=None):
    query = "SELECT c.id_carte, tc.code, tc.nom FROM Carte c JOIN Pioche p ON c.id_pioche = p.id_pioche JOIN Type_Carte tc ON c.code_type_carte = tc.code WHERE p.id_partie = %s AND c.etat = 'Dans la pioche' ORDER BY c.rang_apparition ASC LIMIT 1"
    res = execute_query(query, (id_partie,), fetch="one", conn=conn)
    if res:
        id_carte, code_carte, nom_carte = res
        execute_query("UPDATE Carte SET etat = 'Piochée', id_joueur_piocheur = %s, date_pioche = CURRENT_TIMESTAMP WHERE id_carte = %s", (id_joueur, id_carte), fetch=None, conn=conn)
        execute_query("UPDATE Tour SET id_carte_piochee = %s WHERE id_tour = %s", (id_carte, id_tour), fetch=None, conn=conn)
        restantes = execute_query("SELECT COUNT(*) FROM Carte c JOIN Pioche p ON c.id_pioche = p.id_pioche WHERE p.id_partie = %s AND c.etat = 'Dans la pioche'", (id_partie,), fetch="one", conn=conn)
        if restantes and restantes[0] == 0:
            ids = [row[0] for row in execute_query("SELECT c.id_carte FROM Carte c JOIN Pioche p ON c.id_pioche = p.id_pioche WHERE p.id_partie = %s", (id_partie,), conn=conn) or []]
            random.shuffle(ids)
            for rang, i_c in enumerate(ids, start=1):
                execute_query("UPDATE Carte SET etat = 'Dans la pioche', rang_apparition = %s WHERE id_carte = %s", (rang, i_c), fetch=None, conn=conn)
        return code_carte, nom_carte
    return 'C_MISSILE', 'Tir Classique (Secours)'

def verifier_impact(id_partie, id_joueur_cible, x, y, conn=None):
    query = """
        SELECT n.id_navire, n.nom FROM Composition_Flottille cf JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille JOIN Navire n ON cf.id_navire = n.id_navire
        WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'
          AND ((cf.sens = 'H' AND cf.x <= %s AND %s < cf.x + n.taille AND cf.y = %s) OR (cf.sens = 'V' AND cf.x = %s AND cf.y <= %s AND %s < cf.y + n.taille)) LIMIT 1
    """
    res = execute_query(query, (id_partie, id_joueur_cible, x, x, y, x, y, y), fetch="one", conn=conn)
    return (res[0], res[1]) if res else (None, None)

def est_navire_coule(id_partie, id_joueur_cible, id_navire, conn=None):
    nav_info = execute_query("SELECT n.taille, cf.x, cf.y, cf.sens FROM Composition_Flottille cf JOIN Navire n ON cf.id_navire = n.id_navire JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.id_navire = %s", (id_partie, id_joueur_cible, id_navire), fetch="one", conn=conn)
    if not nav_info: return False
    taille, x0, y0, sens = nav_info
    cases = [(x0 + i, y0) if sens == 'H' else (x0, y0 + i) for i in range(taille)]
    adv = execute_query("SELECT id_joueur FROM Participer WHERE id_partie = %s AND id_joueur != %s", (id_partie, id_joueur_cible), fetch="one", conn=conn)
    if not adv: return False
    id_adversaire = adv[0]
    touches = 0
    for (cx, cy) in cases:
        if execute_query("SELECT 1 FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour WHERE tour.id_partie = %s AND tour.id_joueur = %s AND t.x = %s AND t.y = %s AND t.resultat IN ('Touché', 'Coulé') LIMIT 1", (id_partie, id_adversaire, cx, cy), fetch="one", conn=conn):
            touches += 1
    return touches == taille

def couler_navire(id_partie, id_joueur_cible, id_navire, conn=None):
    execute_query("UPDATE Composition_Flottille SET etat = 'Coulé' WHERE id_navire = %s AND id_flottille IN (SELECT id_flottille FROM Utiliser_Flottille WHERE id_partie = %s AND id_joueur = %s)", (id_navire, id_partie, id_joueur_cible), fetch=None, conn=conn)

def est_flotte_detruite(id_partie, id_joueur_verif, conn=None):
    res = execute_query("SELECT COUNT(*) FROM Composition_Flottille cf JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'", (id_partie, id_joueur_verif), fetch="one", conn=conn)
    return res and res[0] == 0

def calculer_score_final(id_partie, id_joueur, conn=None):
    query = """
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN t.resultat IN ('Touché', 'Coulé') THEN 1 ELSE 0 END) as touches 
        FROM Tir t 
        JOIN Tour tour ON t.id_tour = tour.id_tour 
        WHERE tour.id_partie = %s AND tour.id_joueur = %s
    """
    res = execute_query(query, (id_partie, id_joueur), fetch="one", conn=conn)
    if not res or res[0] == 0: return 0
    return int(100 * (res[1] or 0) / res[0])

def cloturer_partie_db(id_partie, id_vainqueur, id_perdant, conn=None):
    score_v = calculer_score_final(id_partie, id_vainqueur, conn)
    score_p = calculer_score_final(id_partie, id_perdant, conn)
    execute_query(
        "UPDATE Partie SET etat = 'Terminé', id_vainqueur = %s, score_vainqueur = %s, score_perdant = %s WHERE id_partie = %s",
        (id_vainqueur, score_v, score_p, id_partie), fetch=None, conn=conn
    )
    return score_v

# =====================================================================
# GESTION DES PIÈGES ET IA
# =====================================================================
def placer_piege(id_partie, id_joueur, type_piege, conn=None):
    res = execute_query("SELECT id_grille FROM Grille_Partie WHERE id_partie=%s AND id_joueur=%s LIMIT 1", (id_partie, id_joueur), fetch="one", conn=conn)
    if res:
        id_g = res[0]
        x, y = random.randint(1, 8), random.randint(1, 10)
        sens = random.choice(['H', 'V']) if type_piege == 'Leurre' else 'H'
        execute_query("INSERT INTO Contenu_Grille (id_grille, type, x, y, taille, etat) VALUES (%s, %s, %s, %s, %s, 'Actif')", (id_g, type_piege, x, y, 3 if type_piege=='Leurre' else 1), fetch=None, conn=conn)
        return {"x": x, "y": y, "sens": sens, "taille": 3 if type_piege=='Leurre' else 1}
    return None

def verifier_piege(id_partie, id_cible, x, y, conn=None):
    res = execute_query("SELECT id_grille FROM Grille_Partie WHERE id_partie=%s AND id_joueur=%s LIMIT 1", (id_partie, id_cible), fetch="one", conn=conn)
    if res:
        id_g = res[0]
        query = """
            SELECT id_contenu, type FROM Contenu_Grille 
            WHERE id_grille = %s AND etat = 'Actif'
            AND (
                (type = 'Orque' AND x = %s AND y = %s)
                OR
                (type = 'Leurre' AND %s >= x AND %s < x + taille AND y = %s)
            ) LIMIT 1
        """
        piege = execute_query(query, (id_g, x, y, x, x, y), fetch="one", conn=conn)
        if piege: return piege[0], piege[1]
    return None, None

def detruire_plus_petits_navires(id_partie, id_victime, nb, conn=None):
    query = """
        SELECT cf.id_navire FROM Composition_Flottille cf
        JOIN Navire n ON cf.id_navire = n.id_navire JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'
        ORDER BY n.taille ASC LIMIT %s
    """
    res = execute_query(query, (id_partie, id_victime, nb), conn=conn)
    for row in (res or []):
        couler_navire(id_partie, id_victime, row[0], conn=conn)

def appliquer_mpm(id_partie, id_joueur, id_adversaire, conn=None):
    query = """
        SELECT t.id_tir, t.x, t.y FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour
        WHERE tour.id_partie = %s AND tour.id_joueur = %s AND t.resultat = 'Touché'
        ORDER BY t.id_tir DESC LIMIT 1
    """
    res = execute_query(query, (id_partie, id_adversaire), fetch="one", conn=conn)
    if res:
        id_tir, tx, ty = res
        execute_query("DELETE FROM Tir WHERE id_tir = %s", (id_tir,), fetch=None, conn=conn)
        id_navire, _ = verifier_impact(id_partie, id_joueur, tx, ty, conn=conn)
        if id_navire:
            f_res = execute_query("SELECT id_flottille FROM Utiliser_Flottille WHERE id_partie=%s AND id_joueur=%s", (id_partie, id_joueur), fetch="one", conn=conn)
            if f_res:
                execute_query("UPDATE Composition_Flottille SET x=%s, y=%s, etat='Opérationnel' WHERE id_navire=%s AND id_flottille=%s", (random.randint(1,6), random.randint(1,10), id_navire, f_res[0]), fetch=None, conn=conn)
        return {"annule_tir": {"x": tx, "y": ty}}
    return None

def ia_jouer_tour(id_partie, conn=None):
    players = execute_query("SELECT p.id_joueur, v.niveau FROM Participer p LEFT JOIN Virtuel v ON p.id_joueur = v.id_joueur WHERE p.id_partie = %s", (id_partie,), conn=conn)
    id_joueur_ia = id_humain = niveau_ia = None
    if players:
        for pid, niveau in players:
            if niveau is not None: id_joueur_ia, niveau_ia = pid, niveau
            else: id_humain = pid
    if not id_joueur_ia or not id_humain: return None
    tirs_ia = execute_query("SELECT t.x, t.y, t.resultat FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour WHERE tour.id_partie = %s AND tour.id_joueur = %s", (id_partie, id_joueur_ia), conn=conn) or []
    cases_tirees = set((row[0], row[1]) for row in tirs_ia)
    cases_disponibles = [c for c in [(x, y) for x in range(1, 11) for y in range(1, 11)] if c not in cases_tirees]
    if not cases_disponibles: return None
    if niveau_ia == 'Faible': return random.choice(cases_disponibles)
    cibles_potentielles = []
    for tx, ty in [(row[0], row[1]) for row in tirs_ia if row[2] == 'Touché']:
        id_navire, _ = verifier_impact(id_partie, id_humain, tx, ty, conn=conn)
        if id_navire and not est_navire_coule(id_partie, id_humain, id_navire, conn=conn):
            for ax, ay in [(tx+1, ty), (tx-1, ty), (tx, ty+1), (tx, ty-1)]:
                if 1 <= ax <= 10 and 1 <= ay <= 10 and (ax, ay) not in cases_tirees:
                    cibles_potentielles.append((ax, ay))
    if niveau_ia == 'Expert' and not cibles_potentielles and random.random() < 0.30:
        cibles_expertes = [(int(p.split('-')[0]), int(p.split('-')[1])) for p in get_cases_flottille(id_partie, id_humain, conn=conn)]
        cibles_valides = [c for c in cibles_expertes if c not in cases_tirees]
        if cibles_valides: return random.choice(cibles_valides)
    if cibles_potentielles: return random.choice(cibles_potentielles)
    cases_noires = [(x, y) for (x, y) in cases_disponibles if (x + y) % 2 == 0]
    return random.choice(cases_noires) if cases_noires else random.choice(cases_disponibles)