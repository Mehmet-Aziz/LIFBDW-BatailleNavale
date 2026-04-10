

CREATE TABLE Pavillon (
    code_pays VARCHAR(10) PRIMARY KEY,
    nom_pays VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Distribution (
    nom VARCHAR(100) PRIMARY KEY,
    pourcentage_missile INT NOT NULL,
    pourcentage_rejoue  INT NOT NULL,
    pourcentage_vide    INT NOT NULL,
    pourcentage_mpm     INT NOT NULL,
    pourcentage_leurre  INT NOT NULL,
    pourcentage_willy   INT NOT NULL,
    pourcentage_mega    INT NOT NULL,
    pourcentage_etoile  INT NOT NULL,
    pourcentage_passe   INT NOT NULL,
    pourcentage_oups    INT NOT NULL,
    CONSTRAINT check_total CHECK (
        pourcentage_missile + pourcentage_rejoue + pourcentage_vide +
        pourcentage_mpm + pourcentage_leurre + pourcentage_willy +
        pourcentage_mega + pourcentage_etoile + pourcentage_passe +
        pourcentage_oups = 100
    )
);

CREATE TABLE Type_Carte (
    code        VARCHAR(10) PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    description TEXT,
    est_bonus   BOOLEAN NOT NULL,
    image_path  VARCHAR(255)
);

CREATE TABLE Grille (
    id_grille   SERIAL PRIMARY KEY,
    nb_lignes   INT NOT NULL DEFAULT 10,
    nb_colonnes INT NOT NULL DEFAULT 10,
    image_vide  VARCHAR(255),
    image_eau   VARCHAR(255),
    image_touche VARCHAR(255)
);

CREATE TABLE Joueur (
    id_joueur            SERIAL PRIMARY KEY,
    pseudo               VARCHAR(100) NOT NULL UNIQUE,
    date_creation_compte TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Humain (
    id_joueur       INT PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL,
    prenom          VARCHAR(100) NOT NULL,
    date_naissance  DATE,
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur) ON DELETE CASCADE
);

CREATE TABLE Virtuel (
    id_joueur          INT PRIMARY KEY,
    niveau             VARCHAR(20) NOT NULL,
    date_creation      DATE NOT NULL DEFAULT CURRENT_DATE,
    id_createur_humain INT,
    CONSTRAINT check_niveau CHECK (niveau IN ('Faible', 'Intermédiaire', 'Expert')),
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur) ON DELETE CASCADE,
    FOREIGN KEY (id_createur_humain) REFERENCES Humain(id_joueur)
);

CREATE TABLE Navire (
    id_navire          SERIAL PRIMARY KEY,
    nom                VARCHAR(100) NOT NULL,
    type               VARCHAR(50) NOT NULL,
    taille             INT NOT NULL,
    code_pays_pavillon VARCHAR(10),
    CONSTRAINT check_type_navire CHECK (type IN ('Porte-avion','Croiseur','Contre-torpilleur','Torpilleur')),
    CONSTRAINT check_taille CHECK (taille BETWEEN 2 AND 5),
    FOREIGN KEY (code_pays_pavillon) REFERENCES Pavillon(code_pays)
);

CREATE TABLE Flottille (
    id_flottille SERIAL PRIMARY KEY,
    type         VARCHAR(20) NOT NULL,
    CONSTRAINT check_type_flottille CHECK (type IN ('Nationale','Coalition'))
);

CREATE TABLE Flottille_Nationale (
    id_flottille INT,
    code_pays    VARCHAR(10),
    PRIMARY KEY (id_flottille, code_pays),
    FOREIGN KEY (id_flottille) REFERENCES Flottille(id_flottille) ON DELETE CASCADE,
    FOREIGN KEY (code_pays)    REFERENCES Pavillon(code_pays)
);

CREATE TABLE Composition_Flottille (
    id_flottille INT,
    id_navire    INT,
    x            INT,
    y            INT,
    sens         CHAR(1),
    etat         VARCHAR(20) NOT NULL DEFAULT 'Opérationnel',
    PRIMARY KEY (id_flottille, id_navire),
    CONSTRAINT check_sens CHECK (sens IN ('H','V')),
    CONSTRAINT check_etat_navire CHECK (etat IN ('Opérationnel','Touché','Coulé')),
    CONSTRAINT check_coords CHECK (x BETWEEN 1 AND 10 AND y BETWEEN 1 AND 10),
    FOREIGN KEY (id_flottille) REFERENCES Flottille(id_flottille) ON DELETE CASCADE,
    FOREIGN KEY (id_navire)    REFERENCES Navire(id_navire)
);

-- =========================================================================
-- PARTIE 2 : TABLES PARTIE
-- =========================================================================

CREATE TABLE Partie (
    id_partie        SERIAL PRIMARY KEY,
    date_heure       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    etat             VARCHAR(20) NOT NULL,
    score_vainqueur  INT DEFAULT 0,
    score_perdant    INT DEFAULT 0,
    id_vainqueur     INT,
    id_pioche        INT,
    CONSTRAINT check_etat CHECK (etat IN ('Créée','En cours','Suspendue','Gagnée','Perdue','Terminé')),
    CONSTRAINT check_score CHECK (score_vainqueur >= 0 AND score_perdant >= 0),
    FOREIGN KEY (id_vainqueur) REFERENCES Joueur(id_joueur)
);

CREATE TABLE Participer (
    id_partie INT,
    id_joueur INT,
    PRIMARY KEY (id_partie, id_joueur),
    FOREIGN KEY (id_partie) REFERENCES Partie(id_partie) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur) ON DELETE CASCADE
);

CREATE TABLE Sequence_Temporelle (
    id_seq     SERIAL PRIMARY KEY,
    id_partie  INT NOT NULL,
    id_joueur  INT,
    heure_debut TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    heure_fin   TIMESTAMP,
    CONSTRAINT check_temps CHECK (heure_fin IS NULL OR heure_fin > heure_debut),
    FOREIGN KEY (id_partie) REFERENCES Partie(id_partie) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur)
);

CREATE TABLE Grille_Partie (
    id_partie INT,
    id_joueur INT,
    id_grille INT,
    PRIMARY KEY (id_partie, id_joueur, id_grille),
    FOREIGN KEY (id_partie) REFERENCES Partie(id_partie) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur) ON DELETE CASCADE,
    FOREIGN KEY (id_grille) REFERENCES Grille(id_grille)
);

CREATE TABLE Utiliser_Flottille (
    id_partie    INT,
    id_joueur    INT,
    id_flottille INT,
    PRIMARY KEY (id_partie, id_joueur, id_flottille),
    FOREIGN KEY (id_partie)    REFERENCES Partie(id_partie) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur)    REFERENCES Joueur(id_joueur) ON DELETE CASCADE,
    FOREIGN KEY (id_flottille) REFERENCES Flottille(id_flottille)
);

CREATE TABLE Classement (
    id_classement SERIAL PRIMARY KEY,
    type          VARCHAR(20) NOT NULL,
    duree_mois    INT NOT NULL,
    date_calcul   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rang          INT,
    id_joueur     INT,
    code_pays     VARCHAR(10),
    score_total   INT,
    CONSTRAINT check_type_classement CHECK (type IN ('IJH','CPP')),
    CONSTRAINT check_duree CHECK (duree_mois >= 0),
    FOREIGN KEY (id_joueur)  REFERENCES Joueur(id_joueur),
    FOREIGN KEY (code_pays)  REFERENCES Pavillon(code_pays)
);

-- =========================================================================
-- PARTIE 3 : TABLES PIOCHE ET CARTES
-- =========================================================================

CREATE TABLE Pioche (
    id_pioche        SERIAL PRIMARY KEY,
    nom_distribution VARCHAR(100),
    id_partie        INT UNIQUE,
    FOREIGN KEY (nom_distribution) REFERENCES Distribution(nom),
    FOREIGN KEY (id_partie)        REFERENCES Partie(id_partie) ON DELETE CASCADE
);

ALTER TABLE Partie ADD CONSTRAINT fk_partie_pioche
    FOREIGN KEY (id_pioche) REFERENCES Pioche(id_pioche);

CREATE TABLE Carte (
    id_carte          SERIAL PRIMARY KEY,
    code_type_carte   VARCHAR(10) NOT NULL,
    id_pioche         INT NOT NULL,
    rang_apparition   INT NOT NULL,
    etat              VARCHAR(20) NOT NULL DEFAULT 'Dans la pioche',
    id_joueur_piocheur INT,
    date_pioche       TIMESTAMP,
    CONSTRAINT check_etat_carte CHECK (etat IN ('Dans la pioche','Piochée','Utilisée')),
    CONSTRAINT check_rang       CHECK (rang_apparition BETWEEN 1 AND 100),
    FOREIGN KEY (code_type_carte)    REFERENCES Type_Carte(code),
    FOREIGN KEY (id_pioche)          REFERENCES Pioche(id_pioche) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur_piocheur) REFERENCES Joueur(id_joueur)
);

-- =========================================================================
-- PARTIE 4 : TABLES TOURS ET TIRS
-- =========================================================================

CREATE TABLE Tour (
    id_tour                 SERIAL PRIMARY KEY,
    id_partie               INT NOT NULL,
    id_joueur               INT NOT NULL,
    numero_ordre            INT NOT NULL,
    nb_coulis               INT DEFAULT 0,
    nb_touches              INT DEFAULT 0,
    nb_cellules_explorables INT DEFAULT 100,
    date_debut              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fin                TIMESTAMP,
    id_carte_piochee        INT,
    CONSTRAINT check_ordre CHECK (numero_ordre > 0),
    FOREIGN KEY (id_partie) REFERENCES Partie(id_partie) ON DELETE CASCADE,
    FOREIGN KEY (id_joueur) REFERENCES Joueur(id_joueur),
    FOREIGN KEY (id_carte_piochee) REFERENCES Carte(id_carte)
);

CREATE TABLE Tir (
    id_tir           SERIAL PRIMARY KEY,
    id_tour          INT NOT NULL,
    x                INT NOT NULL,
    y                INT NOT NULL,
    id_carte_utilisee INT,
    resultat         VARCHAR(20),
    CONSTRAINT check_coords_tir CHECK (x BETWEEN 1 AND 10 AND y BETWEEN 1 AND 10),
    CONSTRAINT check_resultat   CHECK (resultat IN ('Eau','Touché','Coulé','Orque','Leurre')),
    FOREIGN KEY (id_tour)           REFERENCES Tour(id_tour) ON DELETE CASCADE,
    FOREIGN KEY (id_carte_utilisee) REFERENCES Carte(id_carte)
);

CREATE TABLE Contenu_Grille (
    id_contenu  SERIAL PRIMARY KEY,
    id_grille   INT NOT NULL,
    type        VARCHAR(20) NOT NULL,
    nom         VARCHAR(100),
    image_path  VARCHAR(255),
    x           INT NOT NULL,
    y           INT NOT NULL,
    taille      INT DEFAULT 3,
    etat        VARCHAR(20) DEFAULT 'Actif',
    CONSTRAINT check_type_contenu CHECK (type IN ('Orque','Leurre')),
    CONSTRAINT check_coords_grille CHECK (x BETWEEN 1 AND 10 AND y BETWEEN 1 AND 10),
    CONSTRAINT check_etat_contenu CHECK (etat IN ('Actif','Touché','Détruit')),
    FOREIGN KEY (id_grille) REFERENCES Grille(id_grille) ON DELETE CASCADE
);

-- =========================================================================
-- INDEX
-- =========================================================================
CREATE INDEX idx_partie_etat      ON Partie(etat);
CREATE INDEX idx_tour_partie       ON Tour(id_partie);
CREATE INDEX idx_carte_pioche      ON Carte(id_pioche);
CREATE INDEX idx_sequence_partie   ON Sequence_Temporelle(id_partie);


-- =========================================================================
-- VÉRIFICATION FINALE
-- =========================================================================
SELECT 'Pavillon'            AS table_name, COUNT(*) AS count FROM Pavillon
UNION ALL SELECT 'Distribution',           COUNT(*) FROM Distribution
UNION ALL SELECT 'Type_Carte',             COUNT(*) FROM Type_Carte
UNION ALL SELECT 'Grille',                 COUNT(*) FROM Grille
UNION ALL SELECT 'Joueur',                 COUNT(*) FROM Joueur
UNION ALL SELECT 'Humain',                 COUNT(*) FROM Humain
UNION ALL SELECT 'Virtuel',                COUNT(*) FROM Virtuel
UNION ALL SELECT 'Navire',                 COUNT(*) FROM Navire
UNION ALL SELECT 'Flottille',              COUNT(*) FROM Flottille
UNION ALL SELECT 'Partie',                 COUNT(*) FROM Partie
UNION ALL SELECT 'Participer',             COUNT(*) FROM Participer
UNION ALL SELECT 'Sequence_Temporelle',    COUNT(*) FROM Sequence_Temporelle
UNION ALL SELECT 'Pioche',                 COUNT(*) FROM Pioche
UNION ALL SELECT 'Carte',                  COUNT(*) FROM Carte
UNION ALL SELECT 'Grille_Partie',          COUNT(*) FROM Grille_Partie
UNION ALL SELECT 'Utiliser_Flottille',     COUNT(*) FROM Utiliser_Flottille
UNION ALL SELECT 'Tour',                   COUNT(*) FROM Tour
UNION ALL SELECT 'Classement',             COUNT(*) FROM Classement;