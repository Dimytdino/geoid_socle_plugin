# Interview skill — environnement-arcgis-tse
Date : 2026-06-25
Expert interviewé : Dimitry (réponses à confirmer ponctuellement avec Fateh, co-mainteneur)
Intervieweur : agent interviewer_skill (conduit en session principale)

---

## Q1 — Nom et périmètre

Nom : `environnement-arcgis-tse` (confirmé).

À quoi sert le skill :
- Claude doit **connaître notre environnement ArcGIS Server** : version, nombre
  d'applications métier, intervenants sur ArcGIS.
- Claude doit être capable, **lors de la génération d'un widget sur ExB**, de
  **guider l'utilisateur** sur la marche à suivre opérationnelle (lancer la VDI,
  etc.).

Le skill porte donc deux choses : (1) la connaissance de l'environnement, (2) le
guidage opérationnel + les standards de développement d'un widget ExB.

---

## Q2 — Déclencheurs réels (mots exacts de l'expert)

- « générer widget exb »
- « experience builder »
- « arcgis »
- « arcgis server »
- « arcgis enterprise »
- « application arcgis »
- « je souhaite créer un widget pour experience builder »
- « je souhaite générer un module sur arcgis »
- « je dois créer une fonctionnalité sur arcgis »

---

## Q3 — Règles non négociables

### Règles absolues (bloquantes — aucune exception ; leur non-respect bloque la production de code ou la validation)

**1. Déclaration des versions — prérequis bloquant.**
Avant toute production de code, les versions des composants concernés doivent
être déclarées explicitement :
- ArcGIS Experience Builder Developer Edition (p. ex. 1.17)
- ArcGIS Enterprise (p. ex. 11.3)
- Tout autre composant impliqué (Portal, SDK, dépendances clés)

Sans déclaration des versions, aucun code n'est produit et aucune validation
n'est possible. Ce n'est pas une formalité de fin de tâche : la déclaration
permet de vérifier les compatibilités en amont — signatures d'API jimu,
dépendances, breaking changes entre ExB Developer Edition et ArcGIS Enterprise.
Le code généré doit être conforme à la version déclarée : en 1.17, on utilise
les API jimu de 1.17, jamais celles d'une autre release.

**2. Environnement de travail — VDI obligatoire.**
Le développement s'effectue sur la VDI. Elle est requise pour exécuter ExB
Developer Edition et pour l'accès direct aux bases. Aucun développement ExB ni
accès base hors VDI.

**3. Validation.**
Aucun code n'est considéré comme validé sans la revue de Fateh ou Dimitry.

**4. Sécurité (règle commune — voir socle).**
Aucun credential ni donnée sensible dans le code ou les prompts. Règle
transverse définie dans le socle (CLAUDE.md / CHARTE §4), rappelée ici car elle
s'applique intégralement aux widgets ExB : pas de token, mot de passe, chaîne de
connexion, URL d'infrastructure interne ni donnée nominative en dur.

### Critères de qualité de code (non binaires — grille d'auto-vérification avant validation)

**Modulaire / non-monolithique**
- `widget.tsx` orchestre, il n'exécute pas : la logique métier sort du composant.
- Toute logique métier isolée dans un module pur, sans React, testable isolément
  et réutilisable. Exemple `geojson-export` : sérialisation GeoJSON + zip (jszip)
  + save (file-saver) forment un module indépendant du composant.
- Séparation ExB native : sous-composants UI dans `components/`, logique dans des
  hooks (`useXxx`) ou `utils/`, configuration typée dans `config.ts` (IMConfig),
  types dans `types.ts`.
- Toute logique partagée entre runtime et setting vit dans un `utils` commun,
  jamais dupliquée.

**Scalable — axe volumétrie / données**
- Ne jamais charger toutes les features d'un coup : query serveur paginée
  (`resultOffset` / `resultRecordCount`, en respectant le `maxRecordCount` du
  service). Pour l'export, batcher.
- `outFields` ciblés, `where` + filtre géométrique côté serveur, `returnGeometry`
  uniquement si nécessaire.
- Demander la SR cible (EPSG:2154 / Lambert-93) directement à la query pour
  éviter la reprojection côté client.
- Ne pas bloquer le thread UI : une sérialisation ou un zip lourds doivent être
  chunkés (ou déportés en web worker). Sinon le widget gèle sur gros volume.
- `AbortController` sur les requêtes en vol lorsque les paramètres changent
  (sélection, étendue), pour éviter races et résultats périmés.
- Nettoyage du cycle de vie `JimuMapView` : retirer les watchers/handles
  (`reactiveUtils`) à l'unmount ; pas de fuite au remount.

**Scalable — axe multi-projet (capitalisation socle)**
- Config-driven : zéro layer id, URL ou spécificité d'agence en dur.
- Le widget doit tourner sur les sept agences en ne touchant qu'à la
  configuration, jamais au code. Un widget qu'il faut forker pour passer d'une
  agence à la suivante n'est pas scalable au sens attendu.

**Bonnes pratiques**
- TypeScript réellement typé : configuration via IMConfig, résultats de query
  typés ; pas de `any` résiduel.
- API conforme à la version déclarée (lien direct avec la règle bloquante n°1).
- Règle 0 — réutiliser jimu avant de recoder : `DataSourceComponent`,
  `JimuMapViewComponent`, hooks `jimu-core` / `jimu-arcgis` plutôt que des
  réimplémentations.
- i18n : chaînes dans les fichiers `nls`, jamais en dur.
- Pas de mutation directe du state : passer par les API du store / `setState`.
- Dépendances externes maîtrisées : versions épinglées (p. ex. `file-saver`,
  `jszip`), vigilance sur le poids du bundle et la résolution webpack/symlink.
- Gestion d'erreur explicite des queries asynchrones : aucune promesse qui
  échoue en silence.

---

## Q4 — Pièges (ce que Claude fait de travers sans ce skill)

1. **Il redemande les versions en boucle** (ArcGIS Server, ExB Developer
   Edition…) au lieu de les retenir une fois déclarées.
2. **Incohérence du standard** : sur un même développement, code « propre » pour
   l'un et code que Fateh qualifie de monolithique pour l'autre — faute de norme
   partagée explicite et appliquée systématiquement.
3. **Il oublie de proposer de générer la documentation.** Claude doit toujours
   proposer de produire la doc.

---

## Q5 — Exemples concrets (validés par l'expert)

**Exemple A — Démarrage de tâche**
- Demande : « Je souhaite créer un widget pour Experience Builder qui exporte la
  sélection en GeoJSON. »
- Bonne réponse de Claude : ne produit pas de code tout de suite ; demande
  d'abord les versions (ExB Dev Edition + ArcGIS Enterprise) pour valider la
  compatibilité des API jimu ; rappelle que le dev se fait sur la VDI ; propose
  l'architecture modulaire (`widget.tsx` orchestre, module pur `geojson-export`
  avec jszip/file-saver hors React) ; termine en proposant de générer la doc.

**Exemple B — Le module geojson-export**
- Demande : « Génère le module d'export GeoJSON. »
- Bonne réponse : module pur sans React (testable isolément) ; query serveur
  paginée (`resultOffset`/`resultRecordCount`, respect du `maxRecordCount`) ;
  `outFields` ciblés, `returnGeometry` au besoin ; SR demandée directement en
  2154 à la query ; sérialisation + zip chunkés pour ne pas geler l'UI ; aucune
  URL/layer id en dur → tout en `config.ts` (IMConfig) ; dépendances épinglées
  (jszip, file-saver).

Faits d'environnement confirmés par le dépôt `nemelios_ags` :
ArcGIS Enterprise 11.3, ExB Dev Edition 1.17, stockage EPSG:2154 ; ArcGIS Server
11.3 embarque arcgispro-py3 en Python 3.11.

---

## Q6 — Hors périmètre

- **Règles SIG génériques** (SRC, validité géométrique, formats d'échange,
  confidentialité foncière) → skill `conventions-sig-tse`.
- **Hygiène TS / bonnes pratiques de code génériques** (typage strict, pas de
  promesse silencieuse, deps épinglées, pas de mutation directe du state) →
  Claude les connaît déjà ; mentionnées brièvement dans le skill, pas
  développées. Arbitrage du mainteneur (2026-06-25) : restent ici en version
  compressée, pas de skill séparé tant que la règle des 3 ne se confirme pas sur
  d'autres projets front.
- **Sécurité / credentials** → master = socle (CLAUDE.md / CHARTE §4) ; rappelée
  ici car elle s'applique aux widgets, mais la source de vérité reste le socle.
- **FME / ETL** → skill `fme-tse`.
- **Orchestration des agents** (ADR, revue, rôles) → socle geoid-socle.

---

## Q7 — Mainteneur

Co-maintenu par **Fateh et Dimitry**. Mise à jour attendue à chaque montée de
version (ArcGIS Enterprise / ExB Dev Edition), nouvelle agence, nouvelle
application métier.

### Points à confirmer ultérieurement avec Fateh
- Nombre exact d'applications métier et liste des intervenants ArcGIS (la Q1
  mentionne ces faits d'environnement, non chiffrés pendant l'interview).
- Modalités précises de lancement de la VDI (procédure pas-à-pas, si elle doit
  figurer dans le skill ou dans un CLAUDE.md projet).
