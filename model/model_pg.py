import psycopg
import tomllib
from logzero import logger
import random
import math

# =====================================================================
# CONNEXION ET REQUÊTES DE BASE
# =====================================================================

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
        with conn.cursor() as cur:
            # ON CIBLE STRICTEMENT LE SCHÉMA PUBLIC
            cur.execute("SET search_path TO public;")
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
            # SECURITE : On force le schéma public à chaque requête
            cur.execute("SET search_path TO public;")
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
# ÉTAPE 1 : STATISTIQUES ET ACCUEIL
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
        ORDER BY victoires DESC 
        LIMIT 3
    """
    res_top = execute_query(query_top, conn=conn)
    if res_top: stats['top_joueurs'] = res_top

    return stats

def get_stats_joueur(id_joueur, conn=None):
    stats = {
        'parties_finies_3m': 0,
        'stats_contre_ia': {'victoires': 0, 'defaites': 0},
        'moyenne_tours': 0,
        'points_2026': 0,
        'cartes_tirees': []
    }
    
    q1 = """
        SELECT COUNT(*) FROM Partie p
        JOIN Participer pa ON p.id_partie = pa.id_partie
        WHERE pa.id_joueur = %s 
          AND p.etat IN ('Gagnée', 'Perdue', 'Terminé')
          AND p.date_heure >= CURRENT_DATE - INTERVAL '3 months'
    """
    res1 = execute_query(q1, (id_joueur,), fetch="one", conn=conn)
    if res1: stats['parties_finies_3m'] = res1[0]
    
    # Remplacement des niveaux par les victoires/défaites contre l'IA
    q2 = """
        SELECT 
            COUNT(CASE WHEN p.id_vainqueur = %s THEN 1 END) as victoires,
            COUNT(CASE WHEN p.id_vainqueur != %s AND p.id_vainqueur IS NOT NULL THEN 1 END) as defaites
        FROM Partie p
        JOIN Participer pa_joueur ON p.id_partie = pa_joueur.id_partie
        JOIN Participer pa_adv ON p.id_partie = pa_adv.id_partie
        JOIN Virtuel v ON pa_adv.id_joueur = v.id_joueur
        WHERE pa_joueur.id_joueur = %s 
          AND p.etat IN ('Gagnée', 'Perdue', 'Terminé')
    """
    res2 = execute_query(q2, (id_joueur, id_joueur, id_joueur), fetch="one", conn=conn)
    if res2: 
        stats['stats_contre_ia'] = {'victoires': res2[0] or 0, 'defaites': res2[1] or 0}

    q3 = """
        SELECT COALESCE(ROUND(AVG(nb_tours), 1), 0)
        FROM (
            SELECT id_partie, COUNT(*) as nb_tours
            FROM Tour
            WHERE id_joueur = %s
            GROUP BY id_partie
        ) sub
    """
    res3 = execute_query(q3, (id_joueur,), fetch="one", conn=conn)
    if res3: stats['moyenne_tours'] = float(res3[0])

    q4 = """
        SELECT COALESCE(SUM(
            CASE
                WHEN p.id_vainqueur = %s THEN p.score_vainqueur
                ELSE p.score_perdant
            END
        ), 0)
        FROM Partie p
        JOIN Participer pa ON p.id_partie = pa.id_partie
        WHERE pa.id_joueur = %s 
          AND EXTRACT(YEAR FROM p.date_heure) = 2026
          AND p.etat IN ('Gagnée', 'Perdue', 'Terminé')
    """
    res4 = execute_query(q4, (id_joueur, id_joueur), fetch="one", conn=conn)
    if res4: stats['points_2026'] = int(res4[0])

    q5 = """
        SELECT tc.nom, COUNT(c.id_carte) as nb_tirees
        FROM Carte c
        JOIN Type_Carte tc ON c.code_type_carte = tc.code
        WHERE c.id_joueur_piocheur = %s
        GROUP BY tc.nom
        ORDER BY nb_tirees DESC
    """
    res5 = execute_query(q5, (id_joueur,), conn=conn)
    if res5: stats['cartes_tirees'] = res5

    return stats

def get_classements(type_classement, duree_mois=0, conn=None):
    if type_classement == 'IJH':
        query = """
            SELECT c.rang, j.pseudo, c.score_total
            FROM Classement c
            JOIN Joueur j ON c.id_joueur = j.id_joueur
            WHERE c.type = 'IJH' AND c.duree_mois = %s
            ORDER BY c.rang ASC
        """
    elif type_classement == 'CPP':
        query = """
            SELECT c.rang, p.nom_pays, c.score_total
            FROM Classement c
            JOIN Pavillon p ON c.code_pays = p.code_pays
            WHERE c.type = 'CPP' AND c.duree_mois = %s
            ORDER BY c.rang ASC
        """
    else: return []
    res = execute_query(query, (int(duree_mois),), conn=conn)
    return res if res else []

# =====================================================================
# ÉTAPE 2 : CRÉATION ET LISTE DES PARTIES
# =====================================================================

def get_adversaires_virtuels(conn=None):
    query = """
        SELECT j.id_joueur, j.pseudo, v.niveau 
        FROM Virtuel v 
        JOIN Joueur j ON v.id_joueur = j.id_joueur
        ORDER BY 
            CASE v.niveau WHEN 'Faible' THEN 1 WHEN 'Intermédiaire' THEN 2 WHEN 'Expert' THEN 3 END;
    """
    return execute_query(query, conn=conn)

def get_distributions(conn=None):
    res = execute_query("SELECT nom FROM Distribution ORDER BY nom", conn=conn)
    return [row[0] for row in res] if res else []

def get_mes_parties(id_joueur):
    query = """
        SELECT p.id_partie, p.etat, p.date_heure 
        FROM Partie p
        JOIN Participer pa ON p.id_partie = pa.id_partie
        WHERE pa.id_joueur = %s 
          AND p.etat IN ('Créée', 'En cours')
        ORDER BY p.date_heure DESC
    """
    res = execute_query(query, (id_joueur,))
    return res if res else []

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
            cur.execute("SET search_path TO public;")
            cur.execute("INSERT INTO Partie (etat) VALUES ('Créée') RETURNING id_partie")
            id_partie = cur.fetchone()[0]

            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_joueur))
            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_adversaire))

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

# =====================================================================
# ÉTAPE 3 : FLOTTILLE ET GRILLES
# =====================================================================

def initialiser_flottille(id_partie, id_joueur, conn=None):
    close_after = False
    if not conn:
        conn = get_connection()
        close_after = True
    if not conn: return False

    original_autocommit = conn.autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO public;")
            cur.execute("INSERT INTO Flottille (type) VALUES ('Nationale') RETURNING id_flottille")
            id_flottille = cur.fetchone()[0]

            cur.execute("INSERT INTO Utiliser_Flottille (id_partie, id_joueur, id_flottille) VALUES (%s, %s, %s)", (id_partie, id_joueur, id_flottille))

            tailles_requises = [5, 4, 3, 3, 2]
            navires_a_placer = []
            cur.execute("SELECT id_navire, taille FROM Navire")
            tous_navires = cur.fetchall()
            
            if len(tous_navires) < 5:
                noms_secours = ["Le Terrible", "L'Audacieux", "Le Triomphant", "Le Redoutable", "L'Agile"]
                types_secours = ["Porte-avion", "Croiseur", "Contre-torpilleur", "Contre-torpilleur", "Torpilleur"]
                for i, t in enumerate(tailles_requises):
                    cur.execute("INSERT INTO Navire (nom, type, taille) VALUES (%s, %s, %s) RETURNING id_navire", (noms_secours[i], types_secours[i], t))
                    navires_a_placer.append({'id_navire': cur.fetchone()[0], 'taille': t})
            else:
                navs_dispos = list(tous_navires)
                for t in tailles_requises:
                    for nav in navs_dispos:
                        if nav[1] == t:
                            navires_a_placer.append({'id_navire': nav[0], 'taille': nav[1]})
                            navs_dispos.remove(nav) 
                            break

            cases_occupees = set()
            placements_finaux = []

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
                        placements_finaux.append((id_flottille, navire['id_navire'], x, y, sens, 'Opérationnel'))
                        place = True

            cur.executemany("INSERT INTO Composition_Flottille (id_flottille, id_navire, x, y, sens, etat) VALUES (%s, %s, %s, %s, %s, %s)", placements_finaux)
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur initialisation flottille : {e}")
        return False
    finally:
        conn.autocommit = original_autocommit
        if close_after: conn.close()

def get_cases_flottille(id_partie, id_joueur, conn=None):
    cases_occupees = []
    query = """
        SELECT cf.x, cf.y, cf.sens, n.taille
        FROM Composition_Flottille cf
        JOIN Navire n ON cf.id_navire = n.id_navire
        JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        WHERE uf.id_partie = %s AND uf.id_joueur = %s
    """
    res = execute_query(query, (id_partie, id_joueur), conn=conn)
    if res:
        for x_start, y_start, sens, taille in res:
            for i in range(taille):
                if sens == 'H': cases_occupees.append(f"{x_start + i}-{y_start}")
                else: cases_occupees.append(f"{x_start}-{y_start + i}")
    return cases_occupees

# =====================================================================
# ÉTAPE 4 : LOGIQUE DE JEU, TIRS ET IA
# =====================================================================

def creer_tour(id_partie, id_joueur, conn=None):
    query_ordre = "SELECT COALESCE(MAX(numero_ordre), 0) + 1 FROM Tour WHERE id_partie = %s AND id_joueur = %s"
    res = execute_query(query_ordre, (id_partie, id_joueur), fetch="one", conn=conn)
    numero_ordre = res[0] if res else 1
    
    query_insert = "INSERT INTO Tour (id_partie, id_joueur, numero_ordre) VALUES (%s, %s, %s) RETURNING id_tour"
    res_insert = execute_query(query_insert, (id_partie, id_joueur, numero_ordre), fetch="one", conn=conn)
    return res_insert[0] if res_insert else None

def enregistrer_tir_db(id_tour, x, y, resultat, conn=None):
    query = "INSERT INTO Tir (id_tour, x, y, resultat) VALUES (%s, %s, %s, %s)"
    execute_query(query, (id_tour, x, y, resultat), fetch=None, conn=conn)
    return True

def piocher_carte_partie(id_partie, id_joueur, id_tour, conn=None):
    query = """
        SELECT c.id_carte, tc.nom 
        FROM Carte c
        JOIN Pioche p ON c.id_pioche = p.id_pioche
        JOIN Type_Carte tc ON c.code_type_carte = tc.code
        WHERE p.id_partie = %s AND c.etat = 'Dans la pioche'
        ORDER BY c.rang_apparition ASC
        LIMIT 1
    """
    res = execute_query(query, (id_partie,), fetch="one", conn=conn)
    if res:
        id_carte, nom_carte = res
        execute_query("UPDATE Carte SET etat = 'Piochée', id_joueur_piocheur = %s, date_pioche = CURRENT_TIMESTAMP WHERE id_carte = %s", (id_joueur, id_carte), fetch=None, conn=conn)
        execute_query("UPDATE Tour SET id_carte_piochee = %s WHERE id_tour = %s", (id_carte, id_tour), fetch=None, conn=conn)
        return nom_carte
    return None

def verifier_impact(id_partie, id_joueur_cible, x, y, conn=None):
    query = """
        SELECT n.id_navire, n.nom
        FROM Composition_Flottille cf
        JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        JOIN Navire n ON cf.id_navire = n.id_navire
        WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.etat != 'Coulé'
          AND ((cf.sens = 'H' AND cf.x <= %s AND %s < cf.x + n.taille AND cf.y = %s)
            OR (cf.sens = 'V' AND cf.x = %s AND cf.y <= %s AND %s < cf.y + n.taille))
        LIMIT 1
    """
    res = execute_query(query, (id_partie, id_joueur_cible, x, x, y, x, y, y), fetch="one", conn=conn)
    return (res[0], res[1]) if res else (None, None)

def est_navire_coule(id_partie, id_joueur_cible, id_navire, conn=None):
    query_nav = """
        SELECT n.taille, cf.x, cf.y, cf.sens
        FROM Composition_Flottille cf
        JOIN Navire n ON cf.id_navire = n.id_navire
        JOIN Utiliser_Flottille uf ON cf.id_flottille = uf.id_flottille
        WHERE uf.id_partie = %s AND uf.id_joueur = %s AND cf.id_navire = %s
    """
    nav_info = execute_query(query_nav, (id_partie, id_joueur_cible, id_navire), fetch="one", conn=conn)
    if not nav_info: return False

    taille, x0, y0, sens = nav_info
    cases = [(x0 + i, y0) if sens == 'H' else (x0, y0 + i) for i in range(taille)]

    query_adv = "SELECT id_joueur FROM Participer WHERE id_partie = %s AND id_joueur != %s"
    adv = execute_query(query_adv, (id_partie, id_joueur_cible), fetch="one", conn=conn)
    if not adv: return False
    id_adversaire = adv[0]

    touches = 0
    for (cx, cy) in cases:
        query_tir = "SELECT 1 FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour WHERE tour.id_partie = %s AND tour.id_joueur = %s AND t.x = %s AND t.y = %s AND t.resultat IN ('Touché', 'Coulé') LIMIT 1"
        hit = execute_query(query_tir, (id_partie, id_adversaire, cx, cy), fetch="one", conn=conn)
        if hit: touches += 1

    return touches == taille

def ia_jouer_tour(id_partie, conn=None):
    """
    IA multi-niveaux :
    - Faible : Aléatoire pur
    - Intermédiaire : Damier + Recherche locale
    - Expert : Damier + Recherche locale + 30% chance de triche intelligente
    """
    # 1. Identifier l'IA, le joueur humain et le niveau de l'IA
    query_players = """
        SELECT p.id_joueur, v.niveau
        FROM Participer p
        LEFT JOIN Virtuel v ON p.id_joueur = v.id_joueur
        WHERE p.id_partie = %s
    """
    players = execute_query(query_players, (id_partie,), conn=conn)
    id_joueur_ia = id_humain = niveau_ia = None
    
    if players:
        for pid, niveau in players:
            if niveau is not None: 
                id_joueur_ia = pid
                niveau_ia = niveau
            else: 
                id_humain = pid
                
    if not id_joueur_ia or not id_humain: return None

    # 2. Historique des tirs de l'IA
    query_tirs = """
        SELECT t.x, t.y, t.resultat
        FROM Tir t JOIN Tour tour ON t.id_tour = tour.id_tour
        WHERE tour.id_partie = %s AND tour.id_joueur = %s
    """
    tirs_ia = execute_query(query_tirs, (id_partie, id_joueur_ia), conn=conn) or []
    cases_tirees = set((row[0], row[1]) for row in tirs_ia)

    toutes_cases = [(x, y) for x in range(1, 11) for y in range(1, 11)]
    cases_disponibles = [c for c in toutes_cases if c not in cases_tirees]
    
    if not cases_disponibles: return None

    # --- NIVEAU FAIBLE : Tir purement aléatoire ---
    if niveau_ia == 'Faible':
        return random.choice(cases_disponibles)

    # --- PHASE CHASSE COMMUNE (INTERMÉDIAIRE & EXPERT) ---
    cibles_potentielles = []
    touches = [(row[0], row[1]) for row in tirs_ia if row[2] == 'Touché']
        
    for tx, ty in touches:
        id_navire, _ = verifier_impact(id_partie, id_humain, tx, ty, conn=conn)
        if id_navire and not est_navire_coule(id_partie, id_humain, id_navire, conn=conn):
            adjacents = [(tx+1, ty), (tx-1, ty), (tx, ty+1), (tx, ty-1)]
            for ax, ay in adjacents:
                if 1 <= ax <= 10 and 1 <= ay <= 10 and (ax, ay) not in cases_tirees:
                    cibles_potentielles.append((ax, ay))

    # --- NIVEAU EXPERT : "Intuition" ciblée ---
    # Si l'expert ne "chasse" pas activement, il a 30% de deviner où est un bateau !
    if niveau_ia == 'Expert' and not cibles_potentielles:
        if random.random() < 0.30:
            cases_flotte = get_cases_flottille(id_partie, id_humain, conn=conn)
            cibles_expertes = []
            for c in cases_flotte:
                parts = c.split('-')
                cibles_expertes.append((int(parts[0]), int(parts[1])))
            
            cibles_valides = [c for c in cibles_expertes if c not in cases_tirees]
            if cibles_valides:
                return random.choice(cibles_valides)

    # Si l'IA (Intermédiaire ou Expert) est en chasse, on valide la cible locale
    if cibles_potentielles:
        return random.choice(cibles_potentielles)

    # --- PHASE RECHERCHE COMMUNE (INTERMÉDIAIRE & EXPERT) ---
    # Damier : on tire en diagonale (x+y pair)
    cases_noires = [(x, y) for (x, y) in cases_disponibles if (x + y) % 2 == 0]
    
    if cases_noires: 
        return random.choice(cases_noires)
        
    return random.choice(cases_disponibles)

def calculer_score(nb_tirs_total):
    if nb_tirs_total == 0: return 0
    return math.floor(100 * (17 / nb_tirs_total))

def terminer_partie(id_partie, id_vainqueur, nb_tirs_vainqueur, nb_tirs_perdant, conn=None):
    score_v = calculer_score(nb_tirs_vainqueur)
    score_p = calculer_score(nb_tirs_perdant)
    query = "UPDATE Partie SET etat = 'Terminé', id_vainqueur = %s, score_vainqueur = %s, score_perdant = %s WHERE id_partie = %s"
    execute_query(query, (id_vainqueur, score_v, score_p, id_partie), fetch=None, conn=conn)
    return True