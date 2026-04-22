🏴‍☠️ Bataille Navale : Sur la Route de Grand Line

Bienvenue sur le dépôt du projet LIFBDW - Bataille Navale !
Ce projet universitaire (UCBL) revisite le grand classique de la bataille navale en y ajoutant des mécaniques de jeu avancées (cartes bonus, pièges, IA de différents niveaux) le tout plongé dans l'univers épique de One Piece.

Réalisé par : GEDIK & DAHOUI

⚓ Les Trésors de ce Projet (Fonctionnalités)

Cartes d'Action Spéciales : Fini le simple tir à l'aveugle ! Utilisez des Méga-Bombes, des Étoiles, ou révélez des cases avec la carte Sonde (Vide).

Pièges Redoutables : Placez un Leurre pour tromper l'ennemi ou invoquez Willy (Laboon) qui, si touché, détruira les plus petits navires du tireur.

Intelligence Artificielle (La Marine) : Affrontez des flottes gérées par l'ordinateur avec différents niveaux de difficulté (Faible, Intermédiaire, Expert).

Tableau des Primes (Classement dynamiques) : Les scores sont calculés en temps réel à la fin de chaque affrontement pour classer les meilleurs Pirates et Équipages de Grand Line.

Interface Immersive : Un design soigné (HTML/CSS) reprenant les codes de la piraterie (Avis de recherche, Berrys, Navires animés en CSS pur).

🗺️ La Carte au Trésor (Architecture du projet)

Voici la structure de notre navire :

LIFBDW-BatailleNavale/
├── controleurs/          # Logique métier et routes du serveur
│   ├── aceuille.py
│   ├── classement.py
│   ├── connexion.py
│   ├── deconnexion.py
│   ├── jeu.py
│   ├── parties.py
│   └── tirer.py
├── model/                # Logique de données et requêtes SQL
│   └── model_pg.py
├── static/               # Ressources statiques
│   └── css/
│       └── style.css
│   └── img/              # (Images du Sunny, de la Marine, du Baratie...)
├── table_sql/            # Scripts de base de données
│   ├── peuplement.sql
│   ├── table.sql
│   └── verif.sql
├── template/             # Vues HTML (Moteur de template)
│   ├── acceuille.html
│   ├── api_reponse.html
│   ├── base.html
│   ├── classement.html
│   ├── connexion.html
│   ├── footer.html
│   ├── header.html
│   ├── jeu.html
│   └── parties.html
├── config-bd.toml        # Identifiants de connexion PostgreSQL
├── routes.toml           # Définition des routes du framework maison
├── requierment.in        # Dépendances Python
└── server.py             # Script principal de lancement du serveur


⛵ Prendre la Mer (Installation & Lancement)

Prêt à hisser les voiles ? Suivez ces instructions étape par étape dans votre terminal pour lancer le jeu localement.

Prérequis : Avoir configuré une base de données PostgreSQL locale et mis à jour le fichier config-bd.toml. Avoir exécuté les scripts du dossier table_sql/ pour créer et peupler la base.

1. Cloner le navire (le dépôt)

git clone [https://github.com/Mehmet-Aziz/LIFBDW-BatailleNavale.git](https://github.com/Mehmet-Aziz/LIFBDW-BatailleNavale.git)
cd LIFBDW-BatailleNavale


2. Préparer les vivres (Environnement virtuel)

On isole les dépendances du projet dans un environnement virtuel :

python3 -m venv .vebdw


Note : Activez l'environnement avant d'installer les dépendances.

Sur Linux/Mac : source .vebdw/bin/activate

Sur Windows : .vebdw\Scripts\activate

Installez ensuite les paquets requis :

pip install -r requierment.in


3. Larguer les amarres (Lancer le serveur)

Exécutez le script serveur à la racine du dossier :

python3 server.py .


4. Jouer !

Enfin, ouvrez votre navigateur web préféré et cliquez sur l'adresse locale générée par le serveur (généralement http://127.0.0.1:4242 ou http://localhost:8000).

Bonne chance sur Grand Line, Amiral ! 🌊