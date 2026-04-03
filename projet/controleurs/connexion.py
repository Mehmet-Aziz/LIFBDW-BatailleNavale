from model.model_pg import chercher_joueur_par_pseudo, creer_joueur

# Initialisation des variables pour le template
REQUEST_VARS['resultat_recherche'] = None
REQUEST_VARS['erreur'] = None

# 1. CAS : RECHERCHE D'UN PSEUDO
pseudo_recherche = POST.get('pseudo_chercher')
if pseudo_recherche:
    joueur = chercher_joueur_par_pseudo(pseudo_recherche)
    if joueur:
        REQUEST_VARS['resultat_recherche'] = joueur
    else:
        REQUEST_VARS['erreur'] = "Joueur introuvable. Voulez-vous le créer ?"

# 2. CAS : CRÉATION ET CONNEXION
pseudo_nouveau = POST.get('pseudo_creer')
if pseudo_nouveau:
    try:
        # On crée le joueur (on peut forcer 'FR' pour le jalon)
        nouveau = creer_joueur(pseudo_nouveau)
        if nouveau:
            SESSION['pseudo'] = pseudo_nouveau
            HTTP_REDIRECT('/') # On va à l'accueil
    except:
        REQUEST_VARS['erreur'] = "Ce pseudo est déjà pris."

# 3. CAS : SE CONNECTER DEPUIS LA RECHERCHE
pseudo_select = POST.get('pseudo_selectionne')
if pseudo_select:
    SESSION['pseudo'] = pseudo_select
    HTTP_REDIRECT('/')