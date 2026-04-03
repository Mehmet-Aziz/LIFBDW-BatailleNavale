import psycopg
import tomllib
from logzero import logger

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
        # CETTE LIGNE EST LA CLÉ : elle dit à Postgres de chercher dans BatNav et public
        with conn.cursor() as cur:
            cur.execute("SET search_path TO BatNav, public;")
        
        return conn
    except Exception as e:
        logger.error(f"Impossible de se connecter : {e}")
        return None

def execute_query(query, params=None, fetch="all"):
    conn = get_connection()
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            res = cur.fetchone() if fetch == "one" else cur.fetchall()
            conn.close()
            return res
    except Exception as e:
        logger.error(f"Erreur SQL : {e}")
        if conn: conn.close()
        return None

def get_statistiques_accueil():
    stats = {'nb_joueurs': 0, 'nb_parties': 0, 'top_joueurs': []}
    
    # On compte les joueurs
    res_j = execute_query("SELECT COUNT(*) FROM Joueur", fetch="one")
    if res_j: stats['nb_joueurs'] = res_j[0]

    # On compte les parties
    res_p = execute_query("SELECT COUNT(*) FROM Partie", fetch="one")
    if res_p: stats['nb_parties'] = res_p[0]

    # Top 3
    query_top = """
        SELECT pseudo, COUNT(*) as victoires
        FROM Joueur
        JOIN Participer ON Joueur.id_joueur = Participer.id_joueur
        WHERE est_gagnant = TRUE
        GROUP BY pseudo ORDER BY victoires DESC LIMIT 3
    """
    res_top = execute_query(query_top)
    if res_top: stats['top_joueurs'] = res_top

    return stats