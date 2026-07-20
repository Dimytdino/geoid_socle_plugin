---
name: environnement-arcgis-tse
description: "Environnement ArcGIS du pôle GéoID (TSE) et standards de développement d'un widget ArcGIS Experience Builder. Utiliser ce skill dès qu'une tâche touche ArcGIS ou ExB, même si l'utilisateur ne donne ni version ni détail : « générer widget exb », « experience builder », « arcgis », « arcgis server », « arcgis enterprise », « application arcgis », « je souhaite créer un widget pour experience builder », « je souhaite générer un module sur arcgis », « je dois créer une fonctionnalité sur arcgis » ; ainsi que publication ou administration ArcGIS, Portal, jimu, JimuMapView, VDI de développement. Ne couvre PAS les règles SIG génériques (SRC, validité géométrique, formats, confidentialité foncière → skill conventions-sig-tse), les workflows FME / ETL (→ skill fme-tse), ni l'orchestration des agents (ADR, revue, rôles → socle geoid-socle)."
---

# Environnement ArcGIS TSE — pôle GéoID

Ce que Claude doit savoir de l'environnement ArcGIS de TSE et comment
développer un widget ArcGIS Experience Builder (ExB) qui tient le standard
du pôle et tourne sur les sept agences sans fork. Cible : toute personne
qui crée un widget ou une fonctionnalité ArcGIS. Co-maintenu par Fateh et
Dimitry.

## Environnement (faits connus)

- **ArcGIS Enterprise / ArcGIS Server : 11.3.** Embarque `arcgispro-py3`
  en Python 3.11.
- **ArcGIS Experience Builder Developer Edition : 1.17.**
- **Stockage : EPSG:2154** (Lambert-93, cf. `conventions-sig-tse`).
- Source de ces faits : dépôt `nemelios_ags` (ADR-001).

> Le nombre exact d'applications métier et la liste des intervenants
> ArcGIS sont **à confirmer avec Fateh** (non chiffrés à ce jour).

## Règles non négociables

1. **Déclarer les versions avant tout code — prérequis bloquant.** Avant
   de produire le moindre code, exiger les versions des composants
   concernés (ExB Developer Edition, ArcGIS Enterprise, et tout autre :
   Portal, SDK, dépendances clés). Sans déclaration, aucun code produit,
   aucune validation possible — c'est en amont qu'on vérifie la
   compatibilité des API jimu et les breaking changes, pas en fin de tâche.
2. **API conforme à la version déclarée.** En 1.17, n'utiliser que les API
   jimu de 1.17 — jamais celles d'une autre release.
3. **Développement sur la VDI obligatoire.** ExB Developer Edition et
   l'accès direct aux bases passent par la VDI. Aucun développement ExB ni
   accès base hors VDI.
4. **Aucun code validé sans la revue de Fateh ou Dimitry.**
5. **Aucun credential ni donnée sensible en dur** (token, mot de passe,
   chaîne de connexion, URL d'infrastructure interne, donnée nominative).
   Source de vérité : CHARTE §4 / socle ; s'applique intégralement aux
   widgets ExB.

## Comment faire

**Architecture modulaire — jamais monolithique** (critère de validation) :
- `widget.tsx` orchestre, il n'exécute pas : la logique métier sort du
  composant.
- Logique métier isolée dans un module pur, sans React, testable et
  réutilisable (ex. `geojson-export` : sérialisation + zip jszip +
  file-saver, indépendant du composant).
- Séparation ExB native : UI dans `components/`, logique dans des hooks
  (`useXxx`) ou `utils/`, configuration typée dans `config.ts` (IMConfig),
  types dans `types.ts`. Logique partagée runtime/setting dans un `utils`
  commun, jamais dupliquée.

**Réutiliser jimu avant de recoder** (règle 0) : `DataSourceComponent`,
`JimuMapViewComponent`, hooks `jimu-core` / `jimu-arcgis` plutôt que des
réimplémentations. Chaînes UI dans les fichiers `nls` (i18n), jamais en dur.

**Cycle de vie `JimuMapView`** : retirer les watchers / handles
(`reactiveUtils`) à l'unmount ; pas de fuite au remount.

**Config-driven, multi-agences** : zéro layer id, URL ou spécificité
d'agence en dur — tout en `config.ts`. Le widget doit tourner sur les sept
agences en ne touchant qu'à la configuration. Un widget qu'il faut forker
pour passer d'une agence à l'autre n'est pas scalable au sens attendu.

**Volumétrie / données** : query serveur paginée (`resultOffset` /
`resultRecordCount`, en respectant le `maxRecordCount` du service) — ne
jamais charger toutes les features d'un coup ; `outFields` ciblés, `where`
+ filtre géométrique côté serveur, `returnGeometry` seulement si
nécessaire ; demander la SR cible (EPSG:2154) directement à la query pour
éviter la reprojection client ; chunker (ou web worker) sérialisation et
zip lourds pour ne pas geler l'UI ; `AbortController` sur les requêtes en
vol quand les paramètres changent (sélection, étendue).

**Bonnes pratiques génériques** (Claude les connaît — appliquer sans les
détailler) : TypeScript réellement typé via IMConfig et résultats de query
typés, pas de `any` résiduel ; pas de mutation directe du state (passer par
le store / `setState`) ; dépendances externes épinglées (ex. `file-saver`,
`jszip`), vigilance bundle/webpack ; gestion d'erreur explicite des queries
async, aucune promesse qui échoue en silence.

**Toujours proposer de générer la documentation** en fin de tâche.

## Exemples

Demande : « Je souhaite créer un widget pour Experience Builder qui exporte
la sélection en GeoJSON. »
Bonne réponse : ne pas produire de code tout de suite ; demander d'abord les
versions (ExB Dev Edition + ArcGIS Enterprise) pour valider la compatibilité
des API jimu ; rappeler que le dev se fait sur la VDI ; proposer
l'architecture modulaire (`widget.tsx` orchestre, module pur
`geojson-export` avec jszip/file-saver hors React) ; finir en proposant de
générer la doc.

Demande : « Génère le module d'export GeoJSON. »
Bonne réponse : module pur sans React (testable isolément) ; query serveur
paginée (`resultOffset`/`resultRecordCount`, respect du `maxRecordCount`) ;
`outFields` ciblés, `returnGeometry` au besoin ; SR demandée en 2154 à la
query ; sérialisation + zip chunkés pour ne pas geler l'UI ; aucune
URL/layer id en dur → tout en `config.ts` (IMConfig) ; dépendances épinglées
(jszip, file-saver). NB : l'export GeoJSON se reprojette en 4326 à la
sérialisation (cf. `conventions-sig-tse`), 2154 étant le SRC de stockage.

## Pièges connus

- Piège : Claude redemande les versions en boucle. Solution : une fois les
  versions déclarées, les retenir pour toute la tâche — ne plus les
  redemander.
- Piège : standard incohérent d'un développement à l'autre (code propre
  pour l'un, monolithique pour l'autre). Solution : appliquer
  systématiquement la grille « modulaire / config-driven / cycle de vie »
  ci-dessus à chaque widget.
- Piège : Claude oublie de proposer la documentation. Solution : toujours
  proposer de générer la doc en fin de tâche.
- Piège : le widget gèle sur gros volume. Solution : chunker sérialisation
  et zip (ou web worker), paginer la query, `AbortController` sur les
  requêtes périmées.
- Piège : fuite mémoire au remount du widget. Solution : retirer les
  watchers/handles `JimuMapView` (`reactiveUtils`) à l'unmount.

## Ce qui n'est pas couvert

- Règles SIG génériques — SRC (Lambert-93 / EPSG:2154), validité
  géométrique, formats d'échange, confidentialité foncière, traçabilité
  → skill `conventions-sig-tse`.
- Workflows FME / ETL → skill `fme-tse`.
- Sécurité / credentials — rappel ici, source de vérité = CHARTE §4 / socle.
- Orchestration des agents (ADR, revue, rôles) → socle `geoid-socle`.
- Procédure pas-à-pas de lancement de la VDI, nombre d'applications métier
  et liste des intervenants ArcGIS → **à confirmer avec Fateh** (potentiel
  CLAUDE.md projet).
