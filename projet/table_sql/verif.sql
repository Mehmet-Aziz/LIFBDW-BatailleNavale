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