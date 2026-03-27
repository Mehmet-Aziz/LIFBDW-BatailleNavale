DROP SCHEMA IF EXISTS mitonmar CASCADE;
CREATE SCHEMA IF NOT EXISTS mitonmar;
SET search_path TO mitonmar;

/* Creating tables */ 

CREATE TABLE RECETTE (
  id_recette SERIAL ,
  nom_recette VARCHAR(80),
  catégorie varchar(80),
  description TEXT,
  nb_personnes integer,
  tmps_préparation TIME,
  tmps_repos TIME,
  tmps_cuisson TIME,
  PRIMARY KEY (id_recette)
);

CREATE TABLE ETAPE (
  id_recette INTEGER,
  numero INTEGER,
  explication TEXT,
  PRIMARY KEY (id_recette, numero)
);

CREATE TABLE AUTEUR (
  id_auteur SERIAL,
  nom VARCHAR(80),
  prénom VARCHAR(80),
  pseudo VARCHAR(80),
  PRIMARY KEY (id_auteur)
);

CREATE TABLE PROPOSE (
  id_recette INTEGER,
  id_auteur INTEGER,
  date_dépôt DATE,
  PRIMARY KEY (id_recette, id_auteur)
);

CREATE TABLE INGREDIENT (
  id_ingrédient SERIAL,
  nom VARCHAR(100),
  catégorie VARCHAR(100),
  PRIMARY KEY (id_ingrédient)
);


CREATE TABLE EST_COMPOSE (
  id_recette INTEGER,
  id_ingrédient INTEGER,
  quantité INTEGER,
  unité VARCHAR(42),
  PRIMARY KEY (id_recette, id_ingrédient)
);

CREATE TABLE COMMENTAIRE ( 
  id_recette INTEGER REFERENCES RECETTE(id_recette),
  id_auteur INTEGER REFERENCES AUTEUR(id_auteur),
  date_commentaire TIMESTAMP,
  texte VARCHAR(255),
  etoiles INT,
  PRIMARY KEY(id_auteur, id_recette, date_commentaire)
);

ALTER TABLE ETAPE ADD FOREIGN KEY (id_recette) REFERENCES RECETTE (id_recette);
ALTER TABLE PROPOSE ADD FOREIGN KEY (id_recette) REFERENCES RECETTE (id_recette);
ALTER TABLE PROPOSE ADD FOREIGN KEY (id_auteur) REFERENCES AUTEUR (id_auteur);
ALTER TABLE EST_COMPOSE ADD FOREIGN KEY (id_recette) REFERENCES RECETTE (id_recette);
ALTER TABLE EST_COMPOSE ADD FOREIGN KEY (id_ingrédient) REFERENCES INGREDIENT (id_ingrédient);

/* Inserting instances */ 
 

INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (1,'Spaghetti bolognaise', 'Plat', 'Les spaghettis bolognaises sont une variété de pâtes longues, fines et cylindriques, typique de la cuisine italienne accompagnées d''une sauce dite bolognaise (italien : ragù bolognese) qui est une recette de sauce traditionnelle de la cuisine italienne, originaire de Bologne en Émilie-Romagne, à base de bœuf haché, sauce tomate, oignon, céleri, carottes, et d''huile d''olive.',4,'00:20:00', null,'01:00:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (2,'Pâté au pommes de terre', 'Plat', 'Le pâté aux pommes de terre est une spécialité culinaire du centre de la France. Il est préparé et consommé principalement dans le Berry et l''Orléanais, le Limousin, le Bourbonnais et la pointe nord-ouest de l''Auvergne.',8,'00:25:00', null,'01:00:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (3,'Gratin dauphinois', 'Plat', 'Le gratin dauphinois ou pommes de terre à la dauphinoise est un plat gratiné traditionnel de la cuisine française, d''origine dauphinoise (Sud-Est de la France), à base de pommes de terre et de lait. Ce plat est connu en Amérique du Nord comme « au gratin style potatoes » (États-Unis et Canada anglophone) ou « pommes de terre au gratin » (Canada francophone).',6,'00:25:00', null,'01:00:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (4,'Crème brulée', 'Dessert', 'La crème brûlée est un dessert composé de jaunes d''oeufs, de sucre, de crème, de vanille et de caramel.',6,'00:20:00', null,'00:50:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (5,'Mousse au chocolat', 'Dessert', 'La mousse au chocolat est un dessert dont la composition traditionnelle comporte au minimum du chocolat et du blanc d''oeuf, monté en neige. Elle peut parfois être agrémentée de sel ou de jaune d’oeuf, de sucre ou de crème montée, d''épices ou de zestes d''agrumes.',4,'00:10:00', null,'00:05:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (6,'Salade lyonnaise', 'Entrée', 'La salade lyonnaise est une salade composée traditionnelle de la cuisine lyonnaise à Lyon, variante de la salade de pissenlit.',6,'00:20:00', null,'00:35:00');
INSERT INTO RECETTE (id_recette, nom_recette, catégorie, description, nb_personnes, tmps_préparation, tmps_repos, tmps_cuisson) VALUES (7,'Cake à la fourme d''Ambert', 'Entrée/Apéritif', null,4,'00:20:00', null,'00:05:00');

INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 1, 'Hachez l''ail, l''oignon, puis coupez la carotte et le céleri en petits dés (enlevez les principales nervures du céleri).');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 2, 'Faites chauffer l''huile dans une casserole assez grande. Faites revenir l''ail, l''oignon, la carotte et le céleri à feu doux pendant 5 min en remuant.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 3, 'Augmenter la flamme, puis ajoutez le boeuf. Faites brunir et remuez de façon à ce que la viande ne fasse pas de gros paquets.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 4, 'Ajoutez le bouillon, le vin rouge, les tomates préalablement coupées assez grossièrement, le sucre et le persil haché. Portez à ébullition.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 5, 'Baisser ensuite le feu et laissez mijoter à couvert 1h à 1h30, de façon à ce que le vin s''évapore.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 6, 'Faites cuire les spaghetti, puis mettez-les dans un plat.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (1, 7, 'Ajoutez la sauce bolognaise.');


INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 1, 'Eplucher les pommes de terre, les laver, les sécher, les découper en fines lamelles. Epluchez et émincer l''oignon, mélanger avec les pommes de terre, salez, poivrer.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 2, 'Disposer une des 2 pâtes feuilletée dans le fond d''une plaque à tarte, remplir avec les pommes de terre.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 3, 'Ajouter la moitié de la crème fraîche. Recouvrir le tout avec la 2ème pâte à tarte en la soudant avec la 1ère, puis badigeonner la pâte supérieure avec un jaune d''oeuf.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 4, 'Faire une cheminée centrale.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 5, 'Cuire au four (thermostat 6/7) environ 1 heure.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (2, 6, 'Déguster avec le reste de la crème.');


INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 1,'Eplucher, laver et couper les pommes de terre en rondelles fines (NB : ne pas les laver APRES les avoir coupées, car l''amidon est nécessaire à une consistance correcte).');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 2,'Hacher l''ail très finement.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 3,'Porter à ébullition dans une casserole le lait, l''ail, le sel, le poivre et la muscade puis y plonger les pommes de terre et laisser cuire 10 à 15 min, selon leur fermeté.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 4,'Préchauffer le four à 180°C (thermostat 6) et beurrer un plat à gratin à l''aide d''une feuille de papier essuie-tout.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 5,'Placer les pommes de terre égouttées dans le plat. Les recouvrir de crème, puis disposer des petites noix de beurre sur le dessus.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (3, 6,'Enfourner pour 50 min à 1 heure de cuisson. Utiliser le lait restant de la cuisson des pommes de terre pour faire une soupe ou une purée dans la foulée.');



INSERT INTO ETAPE (id_recette, numero, explication) VALUES (4, 1,'Faire bouillir le lait, ajouter la crème et le sucre hors du feu. Ajouter les jaunes d''oeufs, mettre à chauffer tout doucement (surtout ne pas bouillir), puis verser dans de petits plats individuels.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (4, 2,'Mettre au four au bain marie et laisser cuire doucement à 180°C environ 50 minutes.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (4, 3,'Laisser refroidir puis mettre dessus du sucre roux et le brûler avec un petit chalumeau de cuisine.');

INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 1,'Séparer les blancs des jaunes d''oeufs.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 2,'Faire ramollir le chocolat dans une casserole au bain-marie.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 3,'Hors du feu, incorporer les jaunes et le sucre.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 4,'Battre les blancs en neige ferme.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 5,'Ajouter délicatement les blancs au mélange à l''aide d''une spatule.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 6,'Verser dans une terrine ou des verrines.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 7,'Mettre au frais 2h minimum.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 8,'Décorer de cacao ou de chocolat râpé.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (5, 9,'Déguster');


INSERT INTO ETAPE (id_recette, numero, explication) VALUES (6, 1,'Trier et bien laver les pissenlits à l''eau vinaigrée.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (6, 2,'Préparer une vinaigrette moutardée.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (6, 3,'Détailler le lard en lardons, le pain en dés. Faire rissoler les lardons dans une poêle anti-adhésive, puis revenir les croûtons dans la même poêle dans le gras rendu par le lard.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (6, 4,'Pendant ce temps, faire pocher les oeufs : porter à ébullition une casserole d''eau additionnée de vinaigre d''alcool. Casser l''oeuf dans une tasse, utiliser la tasse pour le transvaser dans l''eau bouillante sans le disperser (si la casserole est assez grande, ajouter les autres oeufs, toujours 1 à 1 ). Au bout d''1 mn à 1 mn 30 , l''oeuf est mollet, le sortir délicatement de l''eau et le mettre à égoutter dans un bol.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (6, 5,'Servir les pissenlits assaisonnés avec la vinaigrette, répartir dessus les lardons et croûtons chauds, couronner le tout d''un oeuf poché encore tiède et décorer de ciboulette ciselée. Servir aussitôt.');


INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 1, 'Préchauffez le four à 210°c (thermostat 7).');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 2,'Si vous souhaitez le réaliser avec les raisins : Faites tremper les raisins dans le vin blanc pour qu''ils se réhydratent.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 3,'Coupez la fourme en petits morceaux réguliers, sans enlever la croûte mais en grattant la surface avec la lame d''un couteau.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 4,'Mélangez la farine, la levure, les œufs, la crème fraîche dans une terrine, puis incorporez la fourme.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 5,'Travaillez la pâte avec une spatule.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 6,'Égouttez les raisins puis ajoutez-les à la pâte en mélangeant bien.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 7,'Beurrez soigneusement un moule à cake et versez-y la préparation. Enfournez pour 35 min environ.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 8,'Vous pouvez également mettre la préparation dans des petits moules individuels, plus sympa à présenter. Attention, dans ce cas la cuisson sera de 20 à 25 minutes, à surveiller.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 9,'Sortez le ou les cake(s) du four et laissez-le(s) tiédir avant de démouler.');
INSERT INTO ETAPE (id_recette, numero, explication) VALUES (7, 10,'Accompagnez d''une salade verte.');



INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (1,'Toumanget','Ella','Ella_132456');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (2,'Atoudevorais','Yves','Yves_546343');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (3,'Aplus','Yann','Yann_346759');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (4,'Foie','Malo','Malo_768645');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (5,'Gourmet','Justin','Justin_345768');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (6,'Vie-Legras','Célia','Célia_678934');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (7,'Lebec-Sucré','Ella','Ella_648764');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (8,'Donc-Cétrogras','Medhi','Medhi_5275785');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (9,'Holle','Jenny-Diane-Beth-Nicole-Esther','JDBNE_445678');
INSERT INTO AUTEUR (id_auteur, nom, prénom, pseudo) VALUES (10,'Lefrigo','Steve-Eudes-Hubert-Yann-Adam','SEHYA_567834');

INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (1,1, '2024-09-01');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (2,1, '2024-10-11');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (3,1, '2024-11-11');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (4,1, '2024-12-02');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (5,1, '2025-01-04');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (6,1, '2025-02-14');
INSERT INTO PROPOSE (id_recette, id_auteur, date_dépôt) VALUES (7,1, '2025-03-03');


INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (1,'Moutarde','Condiment');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (2,'Vinaigre de vin rouge','Condiment');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (3,'Huile de tournesol','Huile végétale');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (4,'Lard fumé','Charcutrie');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (5,'Oeuf', null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (6,'Pissenlit','Plante');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (7,'Pain',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (8,'Ciboulette','Plante arômatique');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (9,'Crème fraîche','Crème');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (10,'Levure chimique',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (11,'Farine',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (12,'Fourme d''Ambert','Fromage');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (13,'Raisin sec','Fruit sec');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (14,'Vin blanc','Alcool');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (15,'Chocolat noir','Chocolat');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (16,'Sucre vanillé','Sucre');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (17,'Sucre poudre','Sucre');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (18,'Crème liquide','Crème');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (19,'Lait','Lait');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (20,'Poivre','Condiment');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (21,'Sel','Condiment');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (22,'Muscade','Épice');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (23,'Beurre',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (24,'Pommes de terre','légume');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (25,'Ail',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (26,'Oignon',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (27,'Pâte feuilletée',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (28,'Persil','Plante arômatique');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (29,'Vin rouge','Alcool');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (30,'Tomate','Légume');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (31,'Carotte','Légume');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (32,'Spaghetti',null);
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (33,'Céléri','Légume');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (34,'Boeuf haché','Viande');
INSERT INTO INGREDIENT (id_ingrédient, nom, catégorie) VALUES (35,'Bouillon de vollaile','Bouillon');


INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,3,2,'Cuill. à soupe');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,17,1,'Cuill. à café');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,28,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,29,37,'ml');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,30,850,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,31,1,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,26,1,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,32,500,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,25,2,'gousse');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,33,1,'branche');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,34,500,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (1,35,50,'cl');

INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,20,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,21,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,26,1,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,27,2,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,24,1.5,'kg');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (2,9,50,'cl');

INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,20,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,21,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,22,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,23,100,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,24,1.5,'kg');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,25,2,'gousse');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,9,30,'cl');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (3,19,1,'L');


INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (4,17,200,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (4,5,6,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (4,18,40,'cL');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (4,19,25,'cL');

INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (5,15,100,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (5,5,3,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (5,16,1,'sachet');

INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,1,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,2,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,3,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,4,200,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,5,4,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,6,400,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,7,4,'tranche');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (6,8,1,'botte');

INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,9,20,'cL');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,10,1,'sachet');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,11,200,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,5,3,'unité');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,12,150,'g');
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,13,null,null);
INSERT INTO EST_COMPOSE (id_recette, id_ingrédient, quantité, unité) VALUES (7,14,null,null);

