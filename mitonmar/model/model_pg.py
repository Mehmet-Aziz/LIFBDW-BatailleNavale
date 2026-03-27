import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from logzero import logger

def execute_select_query(connexion, query, params=[]):
    """
    Méthode générique pour exécuter une requête SELECT (qui peut retourner plusieurs instances).
    Utilisée par des fonctions plus spécifiques.
    """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, params)
            cursor.row_factory = dict_row
            result = cursor.fetchall()
            return result 
        except psycopg.Error as e:
            logger.error(e)
    return None

def execute_other_query(connexion, query, params=[]):
    """
    Méthode générique pour exécuter une requête INSERT, UPDATE, DELETE.
    Utilisée par des fonctions plus spécifiques.
    """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, params)
            result = cursor.rowcount
            return result 
        except psycopg.Error as e:
            logger.error(e)
    return None

def get_instances(connexion, nom_table):
    """
    Retourne les instances de la table nom_table
    String nom_table : nom de la table
    """
    query = sql.SQL('SELECT * FROM {table}').format(table=sql.Identifier(nom_table), )
    return execute_select_query(connexion, query)

def count_instances(connexion, nom_table):
    """
    Retourne le nombre d'instances de la table nom_table
    String nom_table : nom de la table
    """
    query = sql.SQL('SELECT COUNT(*) AS nb FROM {table}').format(table=sql.Identifier(nom_table))
    return execute_select_query(connexion, query)



def get_recipe(connexion, id_recette):
    """
    Retourne les informations concernant la recette identifiée par id_recette
    """
    query = 'SELECT * FROM recette WHERE id_recette=%s'
    return execute_select_query(connexion, query, [id_recette])

def get_steps_recipe(connexion, id_recette):
    """
    Retourne les étapes de la recette recette id_recette
    Integer id_recette : identifiant de la recette
    """
    query = 'SELECT * FROM etape WHERE id_recette=%s ORDER BY numero'
    return execute_select_query(connexion, query, [id_recette])

def is_existing_recipe(connexion, nom_recette):
    """
    retourne True si le nom de la recette n'existe pas dans la BD
    String nom_recette : nom de la recette
    Retourne un booléen
    """
    query = 'SELECT count(*) AS nb FROM recette WHERE nom_recette=%s'
    nb = execute_select_query(connexion, query, [nom_recette])[0]['nb']
    return (nb > 0)

def insert_recipe(connexion, nom_recette, cat_recette):
    """
    Insère une nouvelle recette dans la BD
    String nom_recette : nom de la recette
    String cat_recette : catégorie de la recette
    Retourne le nombre de tuples insérés, ou None
    """
    query = 'INSERT INTO recette (nom_recette, catégorie) VALUES(%s,%s)'
    return execute_other_query(connexion, query, [nom_recette,cat_recette])

def get_table_like(connexion, nom_table, like_pattern):
    """
    Retourne les instances de la table nom_table dont le nom correspond au motif like_pattern
    String nom_table : nom de la table
    String like_pattern : motif pour une requête LIKE
    """
    motif = '%' + like_pattern + '%'
    nom_att = 'nom'  # nom attribut dans ingrédient 
    if nom_table == 'recette':  
        nom_att += '_recette'  # nom attribut dans recette 
    query = sql.SQL("SELECT * FROM {} WHERE {} ILIKE {}").format(
        sql.Identifier(nom_table),
        sql.Identifier(nom_att),
        sql.Placeholder())
    return execute_select_query(connexion, query, [motif])



