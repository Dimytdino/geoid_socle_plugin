---
name: conventions-sig-tse
description: "Conventions SIG du pôle GéoID (TSE) : systèmes de coordonnées, formats d'échange, qualité géométrique, confidentialité des données foncières, traçabilité des sources. Utiliser ce skill dès qu'une tâche touche de près ou de loin aux données géographiques : géotraitement, analyse spatiale, requête SQL spatiale (PostGIS), script Python manipulant des géométries (GeoPandas, Shapely, PyQGIS), workflow FME, création ou modification de couches, production de cartes, parcelles, terrains, secteurs, emprises, reprojection, export ou import de données géo — même si l'utilisateur ne mentionne pas explicitement de système de coordonnées ou de format. Ne couvre pas : l'administration de la plateforme ArcGIS (voir skill environnement-arcgis-tse) ni l'orchestration des agents (voir le socle geoid-socle)."
---

# Conventions SIG TSE — pôle GéoID

Règles métier applicables à toute manipulation de données géographiques
chez TSE. Elles s'appliquent au code produit, aux analyses, aux requêtes
et aux livrables — sans que l'utilisateur ait à les rappeler.

> Copie dérivée de la CHARTE §3-§4 du socle `geoid-socle` (master). Toute
> divergence se corrige côté CHARTE, puis se répercute ici (régénération
> par le mainteneur du socle).

## Règles non négociables

1. **SRC de stockage et de calcul : Lambert-93 — EPSG:2154.** Toutes les
   surfaces, distances et géotraitements se font en 2154. Ne jamais
   calculer une surface ou une distance en EPSG:3857 (Web Mercator déforme
   les mesures, jusqu'à +40 % aux latitudes françaises).
2. **SRC d'affichage web : EPSG:3857**, par reprojection à l'affichage
   uniquement. À l'écriture, toujours revenir en 2154.
3. **Le SRC d'un format d'échange prime sur le SRC de stockage pour la
   donnée produite.** En particulier, **GeoJSON (RFC 7946) impose le
   WGS84 — EPSG:4326** : un export GeoJSON se reprojette explicitement en
   4326, quel que soit le SRC de stockage. Ne jamais déduire le SRC de
   sortie de la règle « stockage = 2154 » : il est dicté par le format et
   le destinataire. (KML = 4326 aussi ; GeoPackage et Shapefile portent le
   SRC qu'on leur écrit — y écrire en 2154.)
4. **Toute reprojection est explicite.** Ne jamais supposer le SRC d'une
   donnée : le lire (`.crs`, `ST_SRID`, `Find_SRID`) et le déclarer dans
   le code. Une donnée sans SRC déclaré est une anomalie à signaler.
5. **Valider la géométrie avant toute écriture** : `ST_IsValid` /
   `ST_MakeValid` en PostGIS, `shapely.validation.make_valid` en Python,
   « Vérifier la validité » dans QGIS. Aucun INSERT/UPDATE de géométrie
   invalide.
6. **Confidentialité des données foncières.** Les coordonnées de parcelles
   identifiables, identités de propriétaires et stratégies de secteurs
   sont confidentielles : jamais dans des exemples de code, de la
   documentation, des jeux de test ou tout contenu destiné à sortir de
   TSE. Pour illustrer, utiliser des coordonnées fictives ou tronquées.
7. **Traçabilité** : toute donnée utilisée ou produite porte sa source et
   son millésime (ex. « RPG 2025, IGN »). Une analyse sans ses sources
   n'est pas terminée.

## Comment faire

- **Formats d'échange par défaut** : GeoPackage (.gpkg) ou GeoJSON.
  Shapefile uniquement si un destinataire l'exige (et signaler ses
  limites : noms de champs 10 caractères, pas de type date/heure,
  multi-fichiers).
- **Performance** : créer l'index spatial (GIST en PostGIS) avant toute
  jointure spatiale ; privilégier le SQL ensembliste aux boucles Python
  sur les gros volumes ; en lecture web, paginer et simplifier les
  géométries selon le zoom.
- **Précision** : arrondir les surfaces restituées à l'hectare ou à l'are
  selon le contexte ; ne pas afficher de précision illusoire (une surface
  cadastrale au m² près n'a pas de sens en identification).
- **Unités** : surfaces en hectares dans les livrables métier (les calculs
  internes en m² sont acceptés s'ils sont convertis à la restitution).

## Exemples

Demande : « calcule la surface des parcelles de ma couche »
Bonne réponse : vérifier le SRC de la couche ; si ≠ 2154, reprojeter
explicitement ; calculer en 2154 ; restituer en hectares avec la source
et le millésime de la couche.

Demande : « insère ces géométries dans la table »
Bonne réponse : `INSERT INTO ... SELECT ST_MakeValid(geom), ...` dans une
transaction, après vérification que `ST_SRID(geom) = 2154`.

Demande : « exporte la sélection / cette couche en GeoJSON »
Bonne réponse : reprojeter chaque géométrie en EPSG:4326 (RFC 7946) AVANT
sérialisation — `webMercatorToGeographic` depuis 3857, module `projection`
chargé depuis 2154 — émettre les coordonnées en [longitude, latitude],
borner à ~6-7 décimales, sans s'appuyer sur un membre `crs`. La sortie en
2154 « parce que la CHARTE dit Lambert-93 » est l'erreur à ne pas commettre :
2154 est le SRC de stockage, pas celui du format GeoJSON.

## Pièges connus

- **Surface en 3857** : l'erreur classique. Une parcelle de 10 ha « mesure »
  ~13,5 ha en Web Mercator dans le sud de la France. Toujours 2154.
- **SRC supposé à l'import** : un GeoJSON est réputé en WGS84 (EPSG:4326)
  par spécification — pas en 2154. Reprojeter à l'import.
- **GeoJSON exporté en 2154 ou 3857** : erreur classique née d'une
  confusion entre SRC de *stockage* (2154) et SRC du *format de sortie*.
  Un GeoJSON doit sortir en 4326 (cf. règle 3). Reprojeter avant
  sérialisation ; ne pas se contenter d'un membre `crs` non standard, que
  les consommateurs WGS84 (Leaflet, Mapbox, GDAL en mode strict) ignorent.
- **`ST_Intersects` sans index** : fonctionne, mais peut prendre des heures
  sur des millions de parcelles. Index GIST d'abord.
- **Shapefile tronqué** : des noms de champs > 10 caractères sont coupés
  silencieusement à l'export. Vérifier ou éviter le format.

## Ce qui n'est pas couvert

Administration de la plateforme ArcGIS Enterprise, publication de services,
droits et licences → skill `environnement-arcgis-tse`.
Conventions de workflows FME → skill `fme-tse`.
Règles d'orchestration des agents (ADR, revue, rôles) → socle `geoid-socle`.
