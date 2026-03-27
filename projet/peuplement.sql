-- =========================================================================
-- PEUPLEMENT
-- =========================================================================

-- PAVILLON
INSERT INTO Pavillon (code_pays, nom_pays) VALUES
('FR',  'France'),
('USA', 'États-Unis'),
('GB',  'Royaume-Uni'),
('DE',  'Allemagne'),
('JP',  'Japon');

-- DISTRIBUTION
INSERT INTO Distribution (nom, pourcentage_missile, pourcentage_rejoue,
    pourcentage_vide, pourcentage_mpm, pourcentage_leurre, pourcentage_willy,
    pourcentage_mega, pourcentage_etoile, pourcentage_passe, pourcentage_oups)
VALUES
('Distribution 1', 50, 10, 10, 5, 3, 3, 3, 1, 10, 5),
('Distribution 2', 20, 15, 13, 10, 5, 5, 5, 2, 15, 10),
('Distribution 3', 10,  5, 15, 10, 10, 10, 10, 5,  5, 20);

-- TYPE_CARTE
INSERT INTO Type_Carte (code, nom, description, est_bonus, image_path) VALUES
('C_MISSILE','Missile',          'Tire un missile classique sur la case indiquée',         true,  'img/missile.png'),
('C_REJOUE', 'Rejoue une fois',  'Tire une seconde fois dans le même tour',                true,  'img/rejoue.png'),
('C_VIDE',   'Vide ou pas vide ?','Révèle si une case est vide avant de tirer',            true,  'img/vide.png'),
('C_MPM',    'Même pas mal !',   'Annule un dégât subi et déplace le navire',              true,  'img/mpm.png'),
('C_LEURRE', 'Bateau leurre',    'Place un bateau leurre dans la grille',                  true,  'img/leurre.png'),
('C_WILLY',  'Sauvez Willy',     'Orque : si touchée, coule les 3 plus petits navires',   true,  'img/willy.png'),
('C_MEGA',   'Méga-bombe',       'Frappe la cible et ses 8 cases adjacentes (9 cases)',    true,  'img/mega.png'),
('C_ETOILE', 'Étoile de la mort','Frappe la cible et les 24 cases proches (25 cases)',    true,  'img/etoile.png'),
('C_PASSE',  'Passe ton tour',   'Le joueur perd son tour',                                false, 'img/passe.png'),
('C_OUPS',   'Mauvaise manip',   'Touche un de vos propres navires et perd le tour',      false, 'img/oups.png');

-- GRILLE
INSERT INTO Grille (nb_lignes, nb_colonnes, image_vide, image_eau, image_touche) VALUES
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png'),
(10, 10, 'img/vide.png', 'img/eau.png', 'img/touche.png');

-- JOUEURS HUMAINS
INSERT INTO Joueur (pseudo) VALUES ('joueur_test'),('alice'),('bob');
INSERT INTO Humain (id_joueur, nom, prenom, date_naissance)
SELECT j.id_joueur, v.nom, v.prenom, v.ddn::date
FROM (VALUES
    ('joueur_test','Dupont','Jean','1995-06-15'),
    ('alice','Martin','Alice','1998-03-22'),
    ('bob','Durand','Bob','2000-11-05')
) AS v(pseudo, nom, prenom, ddn)
JOIN Joueur j ON j.pseudo = v.pseudo;

-- JOUEURS VIRTUELS
INSERT INTO Joueur (pseudo) VALUES ('IA_Faible'),('IA_Intermediaire'),('IA_Expert');
INSERT INTO Virtuel (id_joueur, niveau, id_createur_humain)
SELECT j.id_joueur, v.niveau,
       (SELECT id_joueur FROM Joueur WHERE pseudo = 'joueur_test')
FROM (VALUES
    ('IA_Faible',        'Faible'),
    ('IA_Intermediaire', 'Intermédiaire'),
    ('IA_Expert',        'Expert')
) AS v(pseudo, niveau)
JOIN Joueur j ON j.pseudo = v.pseudo;

-- NAVIRES
INSERT INTO Navire (nom, type, taille, code_pays_pavillon) VALUES
('Le Foch',        'Porte-avion',       5, 'FR'),
('Le Jean Bart',   'Croiseur',          4, 'FR'),
('Le Terrible',    'Contre-torpilleur', 3, 'FR'),
('Le Triomphant',  'Contre-torpilleur', 3, 'FR'),
('La Combattante', 'Torpilleur',        2, 'FR'),
('USS Enterprise', 'Porte-avion',       5, 'USA'),
('USS Leyte Gulf', 'Croiseur',          4, 'USA'),
('HMS Daring',     'Contre-torpilleur', 3, 'GB'),
('HMS Dragon',     'Contre-torpilleur', 3, 'GB'),
('HMS Swift',      'Torpilleur',        2, 'GB');

-- FLOTTILLES
INSERT INTO Flottille (type) VALUES ('Nationale'),('Nationale'),('Nationale');

INSERT INTO Flottille_Nationale (id_flottille, code_pays)
SELECT f.id_flottille, v.code_pays
FROM (VALUES (1,'FR'),(2,'USA'),(3,'GB')) AS v(num, code_pays)
JOIN Flottille f ON f.id_flottille = v.num;

-- Flottille FR (id=1)
INSERT INTO Composition_Flottille (id_flottille, id_navire, x, y, sens, etat)
SELECT 1, n.id_navire, v.x, v.y, v.sens, 'Opérationnel'
FROM (VALUES
    ('Le Foch',        1, 1, 'H'),
    ('Le Jean Bart',   1, 3, 'H'),
    ('Le Terrible',    1, 5, 'H'),
    ('Le Triomphant',  1, 7, 'H'),
    ('La Combattante', 1, 9, 'H')
) AS v(nom, x, y, sens)
JOIN Navire n ON n.nom = v.nom;

-- Flottille USA (id=2)
INSERT INTO Composition_Flottille (id_flottille, id_navire, x, y, sens, etat)
SELECT 2, n.id_navire, v.x, v.y, v.sens, 'Opérationnel'
FROM (VALUES
    ('USS Enterprise', 1, 1, 'H'),
    ('USS Leyte Gulf', 1, 3, 'H')
) AS v(nom, x, y, sens)
JOIN Navire n ON n.nom = v.nom;

-- Flottille GB (id=3)
INSERT INTO Composition_Flottille (id_flottille, id_navire, x, y, sens, etat)
SELECT 3, n.id_navire, v.x, v.y, v.sens, 'Opérationnel'
FROM (VALUES
    ('HMS Daring', 1, 1, 'H'),
    ('HMS Dragon', 1, 3, 'H'),
    ('HMS Swift',  1, 5, 'H')
) AS v(nom, x, y, sens)
JOIN Navire n ON n.nom = v.nom;

-- =========================================================================
-- PARTIES (sans id_pioche d'abord, on le mettra après)
-- =========================================================================
INSERT INTO Partie (date_heure, etat, score_vainqueur, score_perdant) VALUES
('2025-12-29 16:54:00', 'Gagnée',    85,  0),
('2026-01-15 10:30:00', 'Perdue',     0, 72),
('2026-02-10 14:00:00', 'Suspendue',  0,  0),
('2026-03-20 09:00:00', 'En cours',   0,  0);

-- PARTICIPER (dynamique par pseudo et date)
INSERT INTO Participer (id_partie, id_joueur)
SELECT p.id_partie, j.id_joueur
FROM (VALUES
    ('2025-12-29 16:54:00'::timestamp, 'joueur_test'),
    ('2025-12-29 16:54:00'::timestamp, 'IA_Faible'),
    ('2026-01-15 10:30:00'::timestamp, 'joueur_test'),
    ('2026-01-15 10:30:00'::timestamp, 'IA_Faible'),
    ('2026-02-10 14:00:00'::timestamp, 'joueur_test'),
    ('2026-02-10 14:00:00'::timestamp, 'IA_Intermediaire'),
    ('2026-03-20 09:00:00'::timestamp, 'joueur_test'),
    ('2026-03-20 09:00:00'::timestamp, 'IA_Expert')
) AS v(date_heure, pseudo)
JOIN Partie p ON p.date_heure = v.date_heure
JOIN Joueur j ON j.pseudo    = v.pseudo;

-- SÉQUENCE TEMPORELLE
INSERT INTO Sequence_Temporelle (id_partie, id_joueur, heure_debut, heure_fin)
SELECT p.id_partie, j.id_joueur, v.heure_debut::timestamp, v.heure_fin::timestamp
FROM (VALUES
    ('2025-12-29 16:54:00', 'joueur_test', '2025-12-29 16:54:00', '2025-12-29 17:30:00'),
    ('2026-01-15 10:30:00', 'joueur_test', '2026-01-15 10:30:00', '2026-01-15 11:15:00'),
    ('2026-02-10 14:00:00', 'joueur_test', '2026-02-10 14:00:00', '2026-02-10 14:45:00'),
    ('2026-03-20 09:00:00', 'joueur_test', '2026-03-20 09:00:00', NULL)
) AS v(date_partie, pseudo, heure_debut, heure_fin)
JOIN Partie p ON p.date_heure = v.date_partie::timestamp
JOIN Joueur j ON j.pseudo     = v.pseudo;

-- GRILLE_PARTIE (2 grilles par joueur par partie)
INSERT INTO Grille_Partie (id_partie, id_joueur, id_grille)
SELECT p.id_partie, j.id_joueur, g.id_grille
FROM (VALUES
    ('2025-12-29 16:54:00'::timestamp, 'joueur_test',     1),
    ('2025-12-29 16:54:00'::timestamp, 'IA_Faible',       2),
    ('2026-01-15 10:30:00'::timestamp, 'joueur_test',     3),
    ('2026-01-15 10:30:00'::timestamp, 'IA_Faible',       4),
    ('2026-02-10 14:00:00'::timestamp, 'joueur_test',     5),
    ('2026-02-10 14:00:00'::timestamp, 'IA_Intermediaire',6),
    ('2026-03-20 09:00:00'::timestamp, 'joueur_test',     7),
    ('2026-03-20 09:00:00'::timestamp, 'IA_Expert',       8)
) AS v(date_heure, pseudo, num_grille)
JOIN Partie p ON p.date_heure = v.date_heure
JOIN Joueur j ON j.pseudo     = v.pseudo
JOIN Grille g ON g.id_grille  = v.num_grille;

-- UTILISER_FLOTTILLE
INSERT INTO Utiliser_Flottille (id_partie, id_joueur, id_flottille)
SELECT p.id_partie, j.id_joueur, v.id_flottille
FROM (VALUES
    ('2025-12-29 16:54:00'::timestamp, 'joueur_test', 1),
    ('2026-01-15 10:30:00'::timestamp, 'joueur_test', 1),
    ('2026-02-10 14:00:00'::timestamp, 'joueur_test', 1),
    ('2026-03-20 09:00:00'::timestamp, 'joueur_test', 1)
) AS v(date_heure, pseudo, id_flottille)
JOIN Partie p ON p.date_heure = v.date_heure
JOIN Joueur j ON j.pseudo     = v.pseudo;

-- =========================================================================
-- PIOCHE (après les parties)
-- =========================================================================
INSERT INTO Pioche (nom_distribution, id_partie)
SELECT v.distrib, p.id_partie
FROM (VALUES
    ('2025-12-29 16:54:00'::timestamp, 'Distribution 1'),
    ('2026-01-15 10:30:00'::timestamp, 'Distribution 2'),
    ('2026-02-10 14:00:00'::timestamp, 'Distribution 1'),
    ('2026-03-20 09:00:00'::timestamp, 'Distribution 3')
) AS v(date_heure, distrib)
JOIN Partie p ON p.date_heure = v.date_heure;

-- Lier pioche -> partie
UPDATE Partie SET id_pioche = pi.id_pioche
FROM Pioche pi
WHERE Partie.id_partie = pi.id_partie;

-- =========================================================================
-- CARTES (100 par pioche, dynamique)
-- =========================================================================
-- Pioche partie 1 - Distribution 1
INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition, etat)
SELECT code, pi.id_pioche, ROW_NUMBER() OVER (ORDER BY RANDOM()), 'Dans la pioche'
FROM (
         SELECT 'C_MISSILE' AS code FROM generate_series(1,50)
  UNION ALL SELECT 'C_REJOUE'        FROM generate_series(1,10)
  UNION ALL SELECT 'C_VIDE'          FROM generate_series(1,10)
  UNION ALL SELECT 'C_MPM'           FROM generate_series(1, 5)
  UNION ALL SELECT 'C_LEURRE'        FROM generate_series(1, 3)
  UNION ALL SELECT 'C_WILLY'         FROM generate_series(1, 3)
  UNION ALL SELECT 'C_MEGA'          FROM generate_series(1, 3)
  UNION ALL SELECT 'C_ETOILE'        FROM generate_series(1, 1)
  UNION ALL SELECT 'C_PASSE'         FROM generate_series(1,10)
  UNION ALL SELECT 'C_OUPS'          FROM generate_series(1, 5)
) t
CROSS JOIN (
    SELECT pi.id_pioche FROM Pioche pi
    JOIN Partie p ON p.id_partie = pi.id_partie
    WHERE p.date_heure = '2025-12-29 16:54:00'
) pi;

-- Pioche partie 2 - Distribution 2
INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition, etat)
SELECT code, pi.id_pioche, ROW_NUMBER() OVER (ORDER BY RANDOM()), 'Dans la pioche'
FROM (
         SELECT 'C_MISSILE' AS code FROM generate_series(1,20)
  UNION ALL SELECT 'C_REJOUE'        FROM generate_series(1,15)
  UNION ALL SELECT 'C_VIDE'          FROM generate_series(1,13)
  UNION ALL SELECT 'C_MPM'           FROM generate_series(1,10)
  UNION ALL SELECT 'C_LEURRE'        FROM generate_series(1, 5)
  UNION ALL SELECT 'C_WILLY'         FROM generate_series(1, 5)
  UNION ALL SELECT 'C_MEGA'          FROM generate_series(1, 5)
  UNION ALL SELECT 'C_ETOILE'        FROM generate_series(1, 2)
  UNION ALL SELECT 'C_PASSE'         FROM generate_series(1,15)
  UNION ALL SELECT 'C_OUPS'          FROM generate_series(1,10)
) t
CROSS JOIN (
    SELECT pi.id_pioche FROM Pioche pi
    JOIN Partie p ON p.id_partie = pi.id_partie
    WHERE p.date_heure = '2026-01-15 10:30:00'
) pi;

-- Pioche partie 3 - Distribution 1
INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition, etat)
SELECT code, pi.id_pioche, ROW_NUMBER() OVER (ORDER BY RANDOM()), 'Dans la pioche'
FROM (
         SELECT 'C_MISSILE' AS code FROM generate_series(1,50)
  UNION ALL SELECT 'C_REJOUE'        FROM generate_series(1,10)
  UNION ALL SELECT 'C_VIDE'          FROM generate_series(1,10)
  UNION ALL SELECT 'C_MPM'           FROM generate_series(1, 5)
  UNION ALL SELECT 'C_LEURRE'        FROM generate_series(1, 3)
  UNION ALL SELECT 'C_WILLY'         FROM generate_series(1, 3)
  UNION ALL SELECT 'C_MEGA'          FROM generate_series(1, 3)
  UNION ALL SELECT 'C_ETOILE'        FROM generate_series(1, 1)
  UNION ALL SELECT 'C_PASSE'         FROM generate_series(1,10)
  UNION ALL SELECT 'C_OUPS'          FROM generate_series(1, 5)
) t
CROSS JOIN (
    SELECT pi.id_pioche FROM Pioche pi
    JOIN Partie p ON p.id_partie = pi.id_partie
    WHERE p.date_heure = '2026-02-10 14:00:00'
) pi;

-- Pioche partie 4 - Distribution 3
INSERT INTO Carte (code_type_carte, id_pioche, rang_apparition, etat)
SELECT code, pi.id_pioche, ROW_NUMBER() OVER (ORDER BY RANDOM()), 'Dans la pioche'
FROM (
         SELECT 'C_MISSILE' AS code FROM generate_series(1,10)
  UNION ALL SELECT 'C_REJOUE'        FROM generate_series(1, 5)
  UNION ALL SELECT 'C_VIDE'          FROM generate_series(1,15)
  UNION ALL SELECT 'C_MPM'           FROM generate_series(1,10)
  UNION ALL SELECT 'C_LEURRE'        FROM generate_series(1,10)
  UNION ALL SELECT 'C_WILLY'         FROM generate_series(1,10)
  UNION ALL SELECT 'C_MEGA'          FROM generate_series(1,10)
  UNION ALL SELECT 'C_ETOILE'        FROM generate_series(1, 5)
  UNION ALL SELECT 'C_PASSE'         FROM generate_series(1, 5)
  UNION ALL SELECT 'C_OUPS'          FROM generate_series(1,20)
) t
CROSS JOIN (
    SELECT pi.id_pioche FROM Pioche pi
    JOIN Partie p ON p.id_partie = pi.id_partie
    WHERE p.date_heure = '2026-03-20 09:00:00'
) pi;

-- =========================================================================
-- TOURS
-- =========================================================================
INSERT INTO Tour (id_partie, id_joueur, numero_ordre, nb_coulis, nb_touches,
                  nb_cellules_explorables, date_debut, date_fin)
SELECT p.id_partie, j.id_joueur,
       v.numero_ordre, v.nb_coulis, v.nb_touches, v.nb_cellules,
       v.date_debut::timestamp, v.date_fin::timestamp
FROM (VALUES
    ('2025-12-29 16:54:00','joueur_test',1,0,1,99,'2025-12-29 16:54:00','2025-12-29 16:56:00'),
    ('2025-12-29 16:54:00','joueur_test',2,0,2,97,'2025-12-29 16:56:00','2025-12-29 16:58:00'),
    ('2025-12-29 16:54:00','joueur_test',3,1,2,96,'2025-12-29 16:58:00','2025-12-29 17:00:00'),
    ('2025-12-29 16:54:00','joueur_test',4,2,2,95,'2025-12-29 17:00:00','2025-12-29 17:05:00'),
    ('2026-01-15 10:30:00','joueur_test',1,0,1,99,'2026-01-15 10:30:00','2026-01-15 10:35:00'),
    ('2026-01-15 10:30:00','joueur_test',2,1,1,98,'2026-01-15 10:35:00','2026-01-15 10:40:00'),
    ('2026-03-20 09:00:00','joueur_test',1,0,0,100,'2026-03-20 09:00:00',NULL)
) AS v(date_partie, pseudo, numero_ordre, nb_coulis, nb_touches,
       nb_cellules, date_debut, date_fin)
JOIN Partie p ON p.date_heure = v.date_partie::timestamp
JOIN Joueur j ON j.pseudo     = v.pseudo;

-- =========================================================================
-- CLASSEMENT
-- =========================================================================
INSERT INTO Classement (type, duree_mois, rang, id_joueur, score_total)
SELECT 'IJH', 3, ROW_NUMBER() OVER (ORDER BY score DESC), j.id_joueur, score
FROM (VALUES
    ('joueur_test', 85),
    ('alice',       60),
    ('bob',         45)
) AS v(pseudo, score)
JOIN Joueur j ON j.pseudo = v.pseudo;
