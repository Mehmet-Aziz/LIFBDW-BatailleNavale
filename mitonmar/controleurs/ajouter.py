from model.model_pg import is_existing_recipe, insert_recipe
from controleurs.includes import add_activity


add_activity(SESSION['HISTORIQUE'], "consultation de la page ajouter recette")

if POST and 'bouton_valider' in POST:  # formulaire soumis
    nom_recette = POST['nom_recette'][0]  # attention, un <input> retourne une liste
    cat_recette = POST['cat_recette'][0]
    recette_existe = is_existing_recipe(SESSION['CONNEXION'], nom_recette)
    if not(recette_existe) and len(nom_recette) > 0:  # pas de recette avec ce nom
        recette_ajout = insert_recipe(SESSION['CONNEXION'], nom_recette, cat_recette)
        if recette_ajout and recette_ajout > 0:  # insertion réussie
            REQUEST_VARS['message'] = f"La recette {nom_recette} a bien été ajoutée !"
            REQUEST_VARS['message_class'] = "alert-success"
        else:  # erreur insertion
            REQUEST_VARS['message'] = f"Erreur lors de l'insertion de la recette {nom_recette}."
            REQUEST_VARS['message_class'] = "alert-error"
    else:  # recette de nom déjà existant
        REQUEST_VARS['message'] = f"Erreur : une recette existe déjà avec ce nom ({nom_recette})."
        REQUEST_VARS['message_class'] = "alert-error"


