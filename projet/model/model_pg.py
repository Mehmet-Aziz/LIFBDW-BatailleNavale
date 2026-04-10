import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from logzero import logger

def execute_select_query(connexion, query, params=[]):
    """Exécute une requête SELECT et retourne une liste de dictionnaires."""
    with connexion.cursor(row_factory=dict_row) as cursor:
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except psycopg.Error as e:
            logger.error(f"Erreur SELECT : {e}")
    return []

# --- GESTION DES UTILISATEURS (CONNEXION / INSCRIPTION) ---

def search_players_for_connexion(conn, pseudo_pattern):
    """
    Recherche des joueurs et retourne une liste de tuples (id, pseudo, nom, prenom)
    pour rester compatible avec les index [0], [1]... du template HTML.
    """
    query = """
        SELECT j.id_joueur, j.pseudo, h.nom, h.prenom
        FROM   Joueur j
        LEFT JOIN Humain h ON h.id_joueur = j.id_joueur
        WHERE  j.pseudo ILIKE %s
        ORDER  BY j.pseudo
    """
    # Ici on n'utilise pas dict_row pour la compatibilité avec l'indexation par chiffre du HTML
    with conn.cursor() as cur:
        cur.execute(query, [f"%{pseudo_pattern}%"])
        return cur.fetchall()

def is_pseudo_taken(conn, pseudo):
    """Vérifie si un pseudo existe déjà."""
    query = "SELECT 1 FROM Joueur WHERE pseudo = %s"
    res = execute_select_query(conn, query, [pseudo])
    return len(res) > 0

def create_new_human_player(conn, pseudo, nom, prenom, date_naissance):
    """
    Crée un joueur (Joueur + Humain) dans une seule transaction.
    Retourne l'id_joueur créé ou None.
    """
    try:
        with conn.cursor() as cur:
            # 1. Insertion Joueur
            cur.execute(
                "INSERT INTO Joueur (pseudo) VALUES (%s) RETURNING id_joueur",
                [pseudo]
            )
            id_joueur = cur.fetchone()[0]
            
            # 2. Insertion Humain
            cur.execute(
                "INSERT INTO Humain (id_joueur, nom, prenom, date_naissance) VALUES (%s, %s, %s, %s)",
                [id_joueur, nom, prenom, date_naissance]
            )
            # Pas besoin de commit manuel si le serveur gère la transaction par bloc
            return id_joueur
    except psycopg.Error as e:
        logger.error(f"Erreur lors de la création du joueur : {e}")
        return None

# --- STATISTIQUES (POUR LA PAGE ACCUEIL) ---

def get_stats_accueil(conn, id_joueur):
    """Récupère l'ensemble des stats requises pour l'accueil."""
    stats = {}
    
    # Parties 3 mois
    q1 = "SELECT COUNT(*) as nb FROM Partie p JOIN Participer pr ON p.id_partie = pr.id_partie WHERE pr.id_joueur = %s AND p.etat = 'Terminé' AND p.date_heure >= CURRENT_DATE - INTERVAL '3 months'"
    r1 = execute_select_query(conn, q1, [id_joueur])
    stats['nb_parties_3mois'] = r1[0]['nb'] if r1 else 0

    # Victoires par niveau
    q2 = "SELECT v.niveau, COUNT(p.id_partie) as nb FROM Partie p JOIN Participer pr_adv ON p.id_partie = pr_adv.id_partie JOIN Virtuel v ON pr_adv.id_joueur = v.id_joueur WHERE p.id_vainqueur = %s AND pr_adv.id_joueur != %s GROUP BY v.niveau"
    stats['victoires_niveaux'] = execute_select_query(conn, q2, [id_joueur, id_joueur])

    # Moyenne tours
    q3 = "SELECT AVG(nb_tours) as moy FROM (SELECT id_partie, COUNT(*) as nb_tours FROM Tour WHERE id_joueur = %s GROUP BY id_partie) as sub"
    r3 = execute_select_query(conn, q3, [id_joueur])
    stats['moyenne_tours'] = round(float(r3[0]['moy']), 2) if r3 and r3[0]['moy'] else 0

    # Points 2026
    q4 = "SELECT SUM(COALESCE(CASE WHEN p.id_vainqueur = %s THEN p.score_vainqueur ELSE p.score_perdant END, 0)) as total FROM Partie p WHERE EXISTS (SELECT 1 FROM Participer pr WHERE pr.id_partie = p.id_partie AND pr.id_joueur = %s) AND EXISTS (SELECT 1 FROM Sequence_Temporelle s WHERE s.id_partie = p.id_partie AND EXTRACT(YEAR FROM s.heure_debut) = 2026)"
    r4 = execute_select_query(conn, q4, [id_joueur, id_joueur])
    stats['points_2026'] = r4[0]['total'] if r4 and r4[0]['total'] else 0

    # Cartes par type
    q5 = "SELECT tc.nom, COUNT(c.id_carte) as nb FROM Type_Carte tc JOIN Carte c ON tc.code = c.code_type_carte WHERE c.id_joueur_piocheur = %s GROUP BY tc.nom"
    stats['cartes_types'] = execute_select_query(conn, q5, [id_joueur])

    # Étoile de la mort (Global)
    q6 = "SELECT COUNT(*) as nb FROM Carte c JOIN Type_Carte tc ON c.code_type_carte = tc.code WHERE tc.nom ILIKE '%étoile%' AND c.id_pioche IN (SELECT id_pioche FROM Partie WHERE id_pioche IS NOT NULL ORDER BY date_heure DESC LIMIT 10)"
    r6 = execute_select_query(conn, q6)
    stats['etoile_mort_10_derniere'] = r6[0]['nb'] if r6 else 0

    return stats