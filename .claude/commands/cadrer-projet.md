---
description: >
  Mener l'entretien de cadrage d'un nouveau projet GéoID, générer son
  CLAUDE.md à partir du template et activer les agents pertinents.
---

# Cadrage d'un projet GéoID

Tu vas cadrer ce projet en suivant strictement les étapes ci-dessous.
Lis d'abord `CHARTE.md` (elle s'applique intégralement et n'a pas à être
recopiée dans le CLAUDE.md du projet) et `templates/CLAUDE.projet.template.md`.

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
Propose la composition d'équipe selon la famille (l'utilisateur valide) :
- **Étude / analyse** : `analyste_sig`, `revieweur`, `documentaliste`,
  `mentor` (+ `architecte` si choix structurants de méthode/données).
- **Pipeline de données** : `architecte`, `developpeur_etl`, `revieweur`,
  `documentaliste`, `mentor` (+ `chef_projet` si multi-jalons).
- **Développement applicatif** : `architecte`, `developpeur_back_geo`,
  `developpeur_front_carto` (si interface), `revieweur`, `documentaliste`,
  `chef_projet`, `mentor`.
- **Pilotage / transverse** : `chef_projet`, `documentaliste`, `mentor`.

Puis applique :
- copie les spécialisations retenues depuis `specialisations/` vers
  `.claude/agents/` ;
- supprime de `.claude/agents/` les agents génériques non retenus
  (`mentor` reste toujours), ainsi que les agents skill-builder
  (`interviewer_skill`, `redacteur_skill`, `critique_skill` — les skills
  se créent dans le dépôt du socle, pas dans les projets) ;
- si une spécialisation du développeur est active, supprime le
  `developpeur` générique sauf besoin résiduel identifié.

⚠️ Ces changements d'équipe ne prennent **pas** effet dans la session en
cours : les agents sont chargés au démarrage de Claude Code. C'est prévu
par l'étape 4 (relance).

## Étape 3 — Génération du CLAUDE.md et du suivi
Remplace le `CLAUDE.md` du dépôt par
`templates/CLAUDE.projet.template.md` rempli avec les réponses de
l'entretien, et crée `docs/suivi-projet.md` depuis
`templates/suivi-projet.template.md` (roadmap initiale = premières
tâches identifiées pendant l'entretien). Règles :
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
