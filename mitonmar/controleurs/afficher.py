from model.model_pg import get_instances, get_recipe, get_steps_recipe
from controleurs.includes import add_activity

add_activity(SESSION['HISTORIQUE'], "affichage des données")

if GET and 'id_recette' in GET: # Cas affichage des détails d'une recette 
    REQUEST_VARS['affichage'] = 'detail'
    current_id = GET['id_recette'][0] # récupération de l'identifiant de la recette à afficher
    REQUEST_VARS['recette'] = get_recipe(SESSION['CONNEXION'], current_id)[0]
    REQUEST_VARS['étapes'] = get_steps_recipe(SESSION['CONNEXION'], current_id)
    print(REQUEST_VARS['recette'])
else: # Cas affichage des listes recettes, auteurs et ingrédients
    REQUEST_VARS['affichage'] = 'listes'
    # récupérer les recettes
    REQUEST_VARS['recettes'] = get_instances(SESSION['CONNEXION'], 'recette')
    # récupérer les auteurs
    REQUEST_VARS['auteurs'] = get_instances(SESSION['CONNEXION'], 'auteur')
   
