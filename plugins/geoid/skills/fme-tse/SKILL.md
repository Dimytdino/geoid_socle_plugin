---
name: fme-tse
description: "Conventions FME du pôle GéoID (TSE) et structure type d'une fiche de documentation d'outil. Utiliser ce skill dès qu'une tâche touche un workflow FME : analyser, documenter, reprendre, maintenir ou déployer un `.fmw` ; comprendre un flux de données ou un traitement ETL ; lire ou décrire des transformers (FeatureReader, Bufferer, PythonCaller, FeatureWriter…), du code Python embarqué, des paramètres publiés, des connexions nommées ; déployer sur FME Server / FME Flow ; lister les dépendances Python d'un workflow. Se déclenche sur les mots de l'équipe : FME, .fmw, workflow, flux de données, ETL, PythonCaller, transformer, FME Server, FME Flow, « documenter un workflow », « reprendre un workflow », « rendre un workflow maintenable ». Utiliser MÊME SI l'utilisateur ne dit pas explicitement « documentation » ou « fiche » : produire la doc d'un outil FME suit toujours la fiche-outil. Ne couvre PAS les règles SIG génériques (SRC, validité géométrique, formats, confidentialité foncière → skill conventions-sig-tse) ni l'orchestration des agents (ADR, revue, rôles → socle geoid-socle)."
---

# FME TSE — pôle GéoID

Comment documenter, reprendre et déployer un workflow FME chez TSE, et
quelle **structure de fiche** suivre pour qu'un outil soit transmissible.
Cible : toute personne qui reprend un `.fmw` sans son auteur, ou qui en
rédige la documentation. Cohérent avec `conventions-sig-tse` (règles SIG).

## Règles non négociables

1. **Toute documentation d'outil FME suit la fiche-outil.** Le gabarit
   faisant autorité est `templates/fiche-outil.template.md` (dépôt
   `geoid-socle`). Ne pas réinventer un plan : partir du template, le
   remplir, retirer les sections non pertinentes plutôt que d'en ajouter
   d'ad hoc.
2. **Un workflow n'est pas documenté tant que ses entrées ET sorties ne
   sont pas toutes décrites** (sources, formats, noms de fichiers,
   dictionnaire des champs produits).
3. **Les dépendances Python sont listées avec leur statut** (obligatoire /
   optionnelle / à valider par test) et leur version si identifiable. Une
   version inconnue se note « à vérifier », jamais inventée.
4. **Distinguer explicitement parti pris / limite / question ouverte** dans
   la fiche. Ne jamais présenter une hypothèse non confirmée comme un fait.
5. **Ne pas documenter le Python ligne à ligne** : décrire le rôle, les
   entrées/sorties et les dépendances du script, pas son détail interne.
6. **Signaler les écarts Windows vs FME Server / Flow** dès qu'ils sont
   identifiés (typiquement `$(FME_MF_DIR)`, chemins de poste personnels).
7. **Une erreur repérée dans le workflow se signale, ne se corrige pas**
   dans le code depuis la doc (cf. CHARTE).

## Comment faire

La fiche-outil s'organise en trois niveaux, portés par
`templates/fiche-outil.template.md` (le détail des sections y vit, pas
ici — une connaissance, un étage) :

- **Fiche d'identité (en-tête normalisé)** — bloc stable et autosuffisant,
  destiné à être moissonné par le futur catalogue des outils GéoID : nom
  de l'outil, type, fichier source / version, auteur d'origine, mainteneur,
  source faisant autorité, statut, date de dernière revue, SRC de travail.
- **Noyau commun de sections** — applicable à tout outil : vue d'ensemble
  (objectif + entrées/sorties synthétiques), prérequis et environnement,
  paramètres d'entrée, paramètres de sortie (avec dictionnaire des champs),
  guide de reprise, partis pris / limites, glossaire.
- **Variantes par type d'outil** — sections spécifiques FME à ajouter quand
  l'outil est un `.fmw` : transformers clés (rôle fonctionnel, dans l'ordre
  du flux), transformers désactivés à ne pas réactiver sans vérification,
  code Python embarqué et dépendances, déploiement FME Server / FME Flow.
  Un outil non-FME (script, modèle QGIS) garde le noyau, sans ces variantes.

Conventions de rédaction :
- **Points d'attention** en encart `> **⚠️ …**` : SRC, millésimes de
  données, persistance des sorties, paramètres codés en dur, writers à
  chemins personnels, doublons de PythonCaller.
- **Exemples anonymisés** : identifiants de projet/poste neutralisés
  (`<identifiant_projet>`), aucune donnée foncière (cf. CHARTE et
  `conventions-sig-tse`).
- **Génération HTML** : produire le `.html` autoportant avec le script livré
  par le plugin — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generer_doc_html.py
  --source FICHE.md --output FICHE.html` (dépendance : `pip install markdown` ;
  la charte visuelle TSE voyage avec le script et n'est pas à fournir). Ne pas
  utiliser pandoc ni de framework front. Sans le plugin, la règle reste : un
  seul fichier `.html`, CSS inliné, aucune dépendance externe.

## Conventions à compléter

Les règles ci-dessous relèvent de l'expert FME du pôle (Kilian) et ne sont
pas encore tranchées. Elles sont posées ici pour être complétées, pas
inventées.

- **Nommage des workflows** — **À COMPLÉTER par Kilian** : convention de
  nom des `.fmw` (préfixe, casse, indication de version/millésime).
- **Emplacement de référence des `.fmw`** — **À COMPLÉTER par Kilian** :
  dépôt / chemin de la version faisant autorité d'un workflow.
- **Règle staging → production** — **À COMPLÉTER par Kilian** : circuit de
  validation avant déploiement FME Server / Flow (test, recette, prod).
- **Journalisation et traçabilité des millésimes** — **À COMPLÉTER par
  Kilian** : comment consigner la date d'exécution et le millésime des
  données sources (ex. IGN) avec les livrables produits.

## Exemples

Demande : « documente ce workflow `.fmw` de calcul de visibilité »
Bonne réponse : appliquer la fiche-outil
(`templates/fiche-outil.template.md`) — remplir la fiche d'identité
(nom, version, mainteneur, statut, SRC), dérouler le noyau (vue
d'ensemble, prérequis, paramètres entrée/sortie + dictionnaire des
champs), conserver les variantes FME (transformers clés, transformers
désactivés, code Python + dépendances avec versions, déploiement Flow),
expliciter partis pris / limites / questions ouvertes, puis générer le
HTML via `${CLAUDE_PLUGIN_ROOT}/scripts/generer_doc_html.py`.

Demande : « j'hérite d'un workflow FME, par où commencer pour le
reprendre ? »
Bonne réponse : ouvrir la fiche-outil si elle existe ; sinon la créer.
Lister d'abord entrées et sorties, repérer les transformers désactivés
et les PythonCaller actifs (risque de double exécution), vérifier les
connexions nommées et l'accès réseau, puis cartographier les dépendances
Python. Signaler à l'orchestrateur toute anomalie repérée.

Demande : « ce workflow tourne sur mon poste, je veux le mettre sur FME
Flow »
Bonne réponse : avant tout, traiter la persistance des sorties
(`$(FME_MF_DIR)` est temporaire et supprimé en fin de job sur Flow),
recréer les connexions nommées sur le serveur, vérifier la présence des
bibliothèques Python côté serveur, retirer les chemins de poste
personnels. La règle staging → production reste **à compléter par Kilian**.

## Pièges connus

- **Deux PythonCaller actifs** : un calcul exécuté deux fois. Vérifier
  lequel est le script de production avant d'en activer un autre.
- **Seuils codés en dur dans le Python** (distances, hauteurs) non exposés
  comme paramètres publiés : à repérer et à signaler dans la fiche.
- **`$(FME_MF_DIR)` sur FME Server / Flow** : répertoire temporaire détruit
  en fin de job → livrables perdus sans mécanisme de publication.
- **Chemins de poste personnels** (`C:\Users\...`) dans des writers
  désactivés : non portables, à corriger avant réactivation.
- **Millésime IGN non tracé** : données WMS téléchargées à l'exécution →
  deux runs à dates éloignées peuvent différer. Consigner la date.
- **`pip` système ≠ Python de FME** : installer les paquets via le
  gestionnaire de packages Python de FME Workbench, pas le pip de l'OS.
- **Shapefile en sortie** : noms de champs tronqués à 10 caractères,
  accents mal gérés (voir aussi `conventions-sig-tse`).

## Ce qui n'est pas couvert

- Règles SIG générales — SRC (Lambert-93 / EPSG:2154), validité
  géométrique, formats d'échange, confidentialité foncière, traçabilité
  des sources → skill `conventions-sig-tse`.
- Orchestration des agents, ADR, revue, rôles → socle `geoid-socle`.
- Conventions FME conventionnelles non tranchées (nommage, emplacement,
  staging, journalisation) → section « Conventions à compléter » ci-dessus,
  **à compléter par Kilian**.
