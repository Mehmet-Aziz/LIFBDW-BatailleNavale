import psycopg
import tomllib
from logzero import logger
import random

def get_connection():
    """Garde cette fonction en secours, mais elle ne devrait plus être la méthode principale."""
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
            cur.execute("SET search_path TO BatNav, public;")
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
        logger.error(f"Erreur SQL : {e}")
        if close_after and conn:
            conn.close()
        return None

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
        'victoires_par_niveau': [],
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
    
    q2 = """
        SELECT v.niveau, COUNT(p.id_partie) as nb_victoires
        FROM Partie p
        JOIN Participer opp_pa ON p.id_partie = opp_pa.id_partie
        JOIN Virtuel v ON opp_pa.id_joueur = v.id_joueur
        WHERE p.id_vainqueur = %s AND opp_pa.id_joueur != %s
        GROUP BY v.niveau
        ORDER BY nb_victoires DESC
    """
    res2 = execute_query(q2, (id_joueur, id_joueur), conn=conn)
    if res2: stats['victoires_par_niveau'] = res2
    
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

# =====================================================================
# NOUVELLES FONCTIONS POUR L'ÉTAPE 2 (CRÉATION DE PARTIE)
# =====================================================================

def get_adversaires_virtuels(conn=None):
    """Récupère la liste des adversaires IA pour le formulaire"""
    query = """
        SELECT j.id_joueur, j.pseudo, v.niveau 
        FROM Virtuel v 
        JOIN Joueur j ON v.id_joueur = j.id_joueur
        ORDER BY 
            CASE v.niveau 
                WHEN 'Faible' THEN 1 
                WHEN 'Intermédiaire' THEN 2 
                WHEN 'Expert' THEN 3 
            END;
    """
    return execute_query(query, conn=conn)

def get_distributions(conn=None):
    """Récupère le nom de toutes les distributions disponibles"""
    res = execute_query("SELECT nom FROM Distribution ORDER BY nom", conn=conn)
    return [row[0] for row in res] if res else []

def creer_partie_complete(id_joueur, id_adversaire, nom_distribution, conn=None):
    """
    Crée la partie, inscrit les joueurs, crée la pioche et génère les 100 cartes.
    Le tout est géré dans une transaction pour éviter les données orphelines.
    """
    close_after = False
    if not conn:
        conn = get_connection()
        close_after = True

    if not conn: return None

    # Désactiver l'autocommit pour gérer la transaction manuellement
    original_autocommit = conn.autocommit
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # 1. Création de la Partie
            cur.execute("INSERT INTO Partie (etat) VALUES ('Créée') RETURNING id_partie")
            id_partie = cur.fetchone()[0]

            # 2. Inscription des participants (Humain et Virtuel)
            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_joueur))
            cur.execute("INSERT INTO Participer (id_partie, id_joueur) VALUES (%s, %s)", (id_partie, id_adversaire))

            # 3. Création de la Pioche
            cur.execute(
                "INSERT INTO Pioche (nom_distribution, id_partie) VALUES (%s, %s) RETURNING id_pioche", 
                (nom_distribution, id_partie)
            )
            id_pioche = cur.fetchone()[0]

            # 4. Mise à jour de la clé étrangère dans Partie
            cur.execute("UPDATE Partie SET id_pioche = %s WHERE id_partie = %s", (id_pioche, id_partie))

            # 5. Récupération des pourcentages de la distribution choisie
            query_dist = """
                SELECT pourcentage_missile, pourcentage_rejoue, pourcentage_vide, 
                       pourcentage_mpm, pourcentage_leurre, pourcentage_willy, 
                       pourcentage_mega, pourcentage_etoile, pourcentage_passe, pourcentage_oups 
                FROM Distribution WHERE nom = %s
            """
            cur.execute(query_dist, (nom_distribution,))
            dist = cur.fetchone()

            if not dist:
                raise ValueError("Distribution introuvable.")

            # Correspondance stricte avec les codes de Type_Carte (10 caractères max)
            codes_types = ['C_MISSILE', 'C_REJOUE', 'C_VIDE', 'C_MPM', 'C_LEURRE', 'C_WILLY', 'C_MEGA', 'C_ETOILE', 'C_PASSE', 'C_OUPS']
            
            # 6. Génération du deck (exactement 100 cartes)
            deck = []
            for i in range(10):
                # Ajoute 'n' fois le code de la carte en fonction de son pourcentage
                deck.extend([codes_types[i]] * dist[i])

            # Mélange aléatoire du deck pour le tirage
            random.shuffle(deck)

            # 7. Insertion en masse (Batch Insert) des 100 cartes
            # On utilise executemany pour des performances optimales
            cartes_data = [(code, id_pioche, rang) for rang, code in enumerate(deck, start=1)]
            
            query_insert_cartes = """
                INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition) 
                VALUES (%s, %s, %s)
            """
            cur.executemany(query_insert_cartes, cartes_data)

            # Validation de toute la transaction
            conn.commit()
            return id_partie

    except Exception as e:
        conn.rollback() # Annulation en cas d'erreur
        logger.error(f"Erreur transaction création partie : {e}")
        return None
    finally:
        # Restauration de l'état initial de la connexion
        conn.autocommit = original_autocommit
        if close_after:
            conn.close()