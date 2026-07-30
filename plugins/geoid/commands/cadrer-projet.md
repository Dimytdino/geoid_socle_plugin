---
description: >
  Mener l'entretien de cadrage d'un nouveau projet GéoID, générer son
  CLAUDE.md à partir du template et activer les agents pertinents.
---

# Cadrage d'un projet GéoID — geoid:cadrer-projet

Tu vas cadrer ce projet en suivant strictement les étapes ci-dessous.
Lis d'abord `CHARTE.md` (elle s'applique intégralement et n'a pas à être
recopiée dans le CLAUDE.md du projet) et `templates/CLAUDE.projet.template.md`.

Les agents du pôle sont fournis par le plugin `geoid` (installé via la
marketplace) : ils sont invocables sous la forme `@geoid:<agent>`. Ce
cadrage ne les copie pas dans le projet ; il définit, au §5 du CLAUDE.md,
la table **normative** des agents que l'orchestrateur est autorisé à
mobiliser (voir Étape 2).

## Étape 1 — Entretien
Pose les questions par petits groupes (pas tout d'un coup), reformule les
réponses pour validation. Sujets à couvrir :

1. **Identité** : nom du projet ; famille (étude / pipeline de données /
   développement applicatif / pilotage — cf. CHARTE §1) ; commanditaire et
   parties prenantes.
2. **Objectif** : problème à résoudre, résultat attendu, critères de
   réussite mesurables, échéance éventuelle.
3. **Données** : sources mobilisées (avec millésimes si connus), données
   produites, sensibilité (foncier ? → rappeler CHARTE §4), volumétries.
4. **Livrables** : liste, format, destinataires.
5. **Existant** : scripts, couches, outils ou conventions à réutiliser
   (règle 0).
6. **Environnement technique** — à documenter précisément, **versions
   incluses** ; le code généré doit être compatible avec l'existant :
   - langages et versions (ex. Python 3.x exact, et où il s'exécute) ;
   - bases de données et versions (Postgres, PostGIS) ;
   - plateforme SIG et versions (ArcGIS Enterprise, Experience Builder,
     QGIS, FME…) ;
   - bibliothèques/paquets disponibles ou imposés (GeoPandas, psycopg…),
     et le gestionnaire autorisé (pip, conda, environnement verrouillé ?) ;
   - environnements (dev / recette / prod), OS des serveurs, accès réseau
     (proxy, machines isolées) ;
   - outils de versionnage et CI le cas échéant.
   Si l'utilisateur ne connaît pas une version, noter `à vérifier` plutôt
   que de supposer — et le signaler dans le compte rendu final.
7. **Décisions** : choix déjà actés (stack, outils, méthodes — avec leur
   justification) vs points à arbitrer → chaque point ouvert devient une
   ligne `🔧 À ARBITRER` avec un identifiant ADR-00X.
8. **Équipe humaine** : qui travaillera sur le projet, et niveau de chacun
   sur les technos concernées (utile au `mentor` et au calibrage des
   explications). Objectif d'apprentissage explicite ? Le noter.
9. **Contraintes** : sécurité, accès, dépendances à d'autres équipes.

## Étape 2 — Sélection des agents
Propose la composition d'équipe selon la famille (l'utilisateur valide).
Les agents génériques ci-dessous sont fournis par le plugin `geoid` et
invocables sous la forme `@geoid:<agent>` ; les `developpeur_*` sont des
spécialisations copiées dans le projet (voir plus bas), invocables sans
préfixe.
- **Étude / analyse** : `analyste_sig`, `revieweur`, `documentaliste`,
  `mentor` (+ `architecte` si choix structurants de méthode/données).
- **Pipeline de données** : `architecte`, `developpeur_etl`, `revieweur`,
  `documentaliste`, `mentor` (+ `chef_projet` si multi-jalons).
- **Développement applicatif** : `architecte`, `developpeur_back_geo`,
  `developpeur_front_carto` (si interface), `revieweur`, `documentaliste`,
  `chef_projet`, `mentor`.
- **Pilotage / transverse** : `chef_projet`, `documentaliste`, `mentor`.

Puis applique :
- **La composition retenue devient la table normative du §5** du CLAUDE.md
  (Étape 3). Tous les agents du plugin `geoid` restent techniquement
  invocables : on ne peut pas les retirer d'un plugin. C'est donc le §5 qui
  fait foi — l'orchestrateur ne délègue **qu'aux** agents qui y figurent
  (renforcé au §0 du template). Il n'y a plus de suppression d'agents
  génériques sur disque, ni de retrait des agents skill-builder : ces
  derniers vivent dans le plugin `geoid-meta`, non installé chez les
  équipes, donc absents des projets par construction.
- **Spécialisation du développeur** : copie la seule spécialisation
  retenue depuis `specialisations/` (dépôt template résiduel, présent dans
  le projet) vers `.claude/agents/` du projet. Elle devient un agent local
  du projet (invocable `@<nom>`, sans préfixe `geoid:`) et peut être
  affinée à la stack exacte du projet. Si une spécialisation est retenue,
  ne liste pas le `developpeur` générique au §5 sauf besoin résiduel
  identifié.

⚠️ La spécialisation copiée ne prend **pas** effet dans la session en
cours : les agents locaux sont chargés au démarrage de Claude Code. C'est
prévu par l'étape 4 (relance).

## Étape 2 bis — Serveurs MCP du projet (`.mcp.json`) — ADR-001d
Selon la famille, **propose** (l'utilisateur valide) la configuration de
serveurs MCP dans le `.mcp.json` **du projet** — jamais dans le plugin :
les chaînes de connexion sont propres au projet. C'est le point le plus
sensible du cadrage ; la CHARTE §4 s'applique intégralement.

Propositions par famille :
- **Étude / analyse** → **PostGIS en lecture seule**. Serveur recommandé :
  `crystaldba/postgres-mcp` en mode `--access-mode=restricted` (transactions
  read-only + garde-fous anti-écriture + timeouts). Exiger un **rôle
  PostgreSQL dédié read-only** (CONNECT + USAGE + SELECT), jamais un compte
  applicatif ou d'administration. Le gabarit lit la connexion depuis la
  variable d'environnement **`POSTGIS_RO_URI`** (jamais écrite dans le
  fichier versionné).
- **Pipeline de données** → **FME Flow MCP**, **uniquement si la version FME
  du projet est ≥ 2026.2** (« FME Flow as an MCP Server » n'existe pas
  avant ; le transformer MCPCaller dès 2026.1). Le vérifier explicitement
  au cadrage — ne pas supposer. Au 2026-07 le pôle est en **FME 2025.2** :
  dans ce cas, **ne pas proposer** FME MCP et noter un point `🔧 À ARBITRER`
  à rouvrir après montée de version. Auth OAuth 2.0, transport distant.
- **Développement applicatif / pilotage** → aucun MCP proposé par défaut.
- **ArcGIS Location Services (Esri)** → **hors périmètre par défaut** (bêta,
  pas de GA, coût à la consommation). Maintenu en veille (suivi S-08) ; ne
  le configurer que si un besoin projet réel le justifie **et** que la clé
  API est gérée comme un secret (variable d'environnement).

Règles de sécurité (non négociables, CHARTE §4) :
- **Jamais de secret en clair** dans `.mcp.json` : identifiants et chaînes
  de connexion via **variables d'environnement** (`${VAR}`, interpolées par
  Claude Code). Le fichier versionné ne contient que des placeholders.
- **Lecture seule / moindre privilège** : rôle dédié RO, aucun scope large.
- Partir du gabarit `templates/mcp.projet.template.json` ; n'y garder que
  les serveurs validés ; consigner le choix au journal des décisions.

Comme les agents, un serveur MCP configuré n'est actif qu'au **redémarrage**
de Claude Code (étape 4).

## Étape 3 — Génération du CLAUDE.md et du suivi
Remplace le `CLAUDE.md` du dépôt par
`templates/CLAUDE.projet.template.md` rempli avec les réponses de
l'entretien, et crée `docs/suivi-projet.md` depuis
`templates/suivi-projet.template.md` (roadmap initiale = premières
tâches identifiées pendant l'entretien). Règles :
- renseigne la ligne de version en en-tête (ADR-001c) : version du plugin
  `geoid` installée (indiquée par `/plugin`, ou injectée au démarrage de
  session par le hook `geoid` — ne PAS chercher un `SOCLE_VERSION`, absent
  d'un dépôt projet) et version du template résiduel mergée (dernier merge du
  dépôt template dans le projet) ;
- reporte la composition validée à l'Étape 2 dans la table `§5 Équipe
  d'agents` : elle est **normative** (l'orchestrateur ne délègue qu'aux
  agents qui y figurent) ;
- ne recopie pas la CHARTE : référence-la ;
- chaque décision déjà actée va directement au journal des décisions ;
- chaque point ouvert apparaît en `🔧 À ARBITRER` avec son ADR-00X **et
  la liste des tâches qu'il bloque** (le reste avance) ;
- le suivi (roadmap, risques, revues) va dans `docs/suivi-projet.md`,
  jamais dans le CLAUDE.md ;
- reste factuel et concis : le CLAUDE.md est lu à chaque session, chaque
  ligne doit mériter sa place.

## Étape 4 — Restitution et relance
Termine par un compte rendu : équipe d'agents activée, décisions actées,
ADR en attente (et recommandation de les faire instruire par
l'`architecte` en premier), prochaine étape conseillée.

Demande ensuite explicitement à l'utilisateur de **quitter et relancer
Claude Code** : le nouveau `CLAUDE.md` et l'équipe d'agents ajustée ne
sont chargés qu'au démarrage d'une session. Le cadrage n'est terminé
qu'après cette relance.
