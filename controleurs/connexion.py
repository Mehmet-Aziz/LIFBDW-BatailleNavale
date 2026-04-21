# connexion.py — exécuté par exec() dans server.py
# Avec exec(), les fonctions du fichier ne se voient pas entre elles.
# Solution : tout le code SQL est écrit directement dans chaque bloc,
# sans aucun appel de fonction à fonction.

REQUEST_VARS['erreur']         = None
REQUEST_VARS['resultats']      = []
REQUEST_VARS['pseudo_cherche'] = ''

conn   = SESSION.get("CONNEXION")
action = POST.get('action', [None])[0]

# ── Recherche ─────────────────────────────────────────────────────────────
if action == 'chercher':
    pseudo = POST.get('pseudo_chercher', [''])[0].strip()
    REQUEST_VARS['pseudo_cherche'] = pseudo
    if pseudo:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT j.id_joueur, j.pseudo, h.nom, h.prenom
                    FROM   Joueur j
                    LEFT JOIN Humain h ON h.id_joueur = j.id_joueur
                    WHERE  j.pseudo ILIKE %s
                    ORDER  BY j.pseudo
                """, [f"%{pseudo}%"])
                resultats = cur.fetchall()
            if resultats:
                REQUEST_VARS['resultats'] = resultats
            else:
                REQUEST_VARS['erreur'] = f"Aucun joueur trouvé pour « {pseudo} »."
        except Exception as e:
            REQUEST_VARS['erreur'] = f"Erreur base de données : {e}"
    else:
        REQUEST_VARS['erreur'] = "Veuillez saisir un pseudo à rechercher."

# ── Sélection ─────────────────────────────────────────────────────────────
elif action == 'selectionner':
    id_joueur = POST.get('id_joueur', [None])[0]
    pseudo    = POST.get('pseudo',    [None])[0]
    if id_joueur and pseudo:
        SESSION['id_joueur'] = int(id_joueur)
        SESSION['pseudo']    = pseudo
        self.redirect('/')
    else:
        REQUEST_VARS['erreur'] = "Sélection invalide, veuillez réessayer."

# ── Inscription ───────────────────────────────────────────────────────────
elif action == 'inscrire':
    pseudo         = POST.get('pseudo_creer',   [''])[0].strip()
    nom            = POST.get('nom',            [''])[0].strip()
    prenom         = POST.get('prenom',         [''])[0].strip()
    date_naissance = POST.get('date_naissance', [''])[0].strip() or None

    if not pseudo or not nom or not prenom:
        REQUEST_VARS['erreur'] = "Le pseudo, le nom et le prénom sont obligatoires."
    else:
        # Vérifier si le pseudo est déjà pris
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id_joueur FROM Joueur WHERE pseudo = %s", [pseudo])
                existant = cur.fetchone()
        except Exception as e:
            existant = None
            REQUEST_VARS['erreur'] = f"Erreur base de données : {e}"

        if existant:
            REQUEST_VARS['erreur'] = f"Le pseudo « {pseudo} » est déjà pris, choisissez-en un autre."
        elif not REQUEST_VARS['erreur']:
            # Créer le joueur
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO Joueur (pseudo) VALUES (%s) RETURNING id_joueur",
                        [pseudo]
                    )
                    row = cur.fetchone()
                    id_joueur = row[0]
                    cur.execute(
                        "INSERT INTO Humain (id_joueur, nom, prenom, date_naissance) VALUES (%s, %s, %s, %s)",
                        [id_joueur, nom, prenom, date_naissance]
                    )
                # ---> LE CORRECTIF EST ICI : On valide la transaction SQL <---
                conn.commit() 
                
                SESSION['id_joueur'] = id_joueur
                SESSION['pseudo']    = pseudo
                self.redirect('/')
            except Exception as e:
                # En cas d'erreur, on annule tout ce qui a été fait
                conn.rollback() 
                REQUEST_VARS['erreur'] = f"Erreur lors de la création du compte : {e}"