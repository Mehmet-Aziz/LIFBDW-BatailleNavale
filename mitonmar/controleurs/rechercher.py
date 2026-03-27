from model.model_pg import get_table_like
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "consultation de la page recherche")

if POST and 'bouton_valider' in POST:  # formulaire soumis
    REQUEST_VARS['result'] = None  # réinitialisation du résultat
    # récupérer les recettes ou les ingrédients avec le nom contenant le terme recherché
    table_name = POST['nom_table'][0]
    term = POST['valeur'][0]
    result = get_table_like(SESSION['CONNEXION'], table_name, term)
    if result is None or len(result) == 0:  # pas de résultat
        REQUEST_VARS['message'] = f"Aucun résultat pour la valeur {term}."
        REQUEST_VARS['message_class'] = "alert-warning"
    else:  # stockage du résultat 
        REQUEST_VARS['message_info'] = f"Résultat trouvé pour '{term}' dans {table_name}."
        REQUEST_VARS['schema'] = result[0].keys()
        REQUEST_VARS['result'] = result
       

