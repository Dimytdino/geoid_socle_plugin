# ADR-001 — Transposition du socle GéoID en plugin(s) Claude Code

- **Statut** : **Accepté — option D** (décision du 2026-07-03, D. Grohan)
- **Date d'instruction** : 2026-07-03
- **Instruit par** : `architecte`
- **Version du socle concernée** : 0.4.0
- **Référence** : README §« Maintenance du socle » (« la migration en plugin restera la vraie solution »)

## 1. Contexte

Le socle est aujourd'hui diffusé **par copie git** : chaque projet du pôle est créé depuis le template GitHub, puis `/cadrer-projet` :
- génère le `CLAUDE.md` projet et `docs/suivi-projet.md` ;
- **retire** les agents skill-builder (`interviewer_skill`, `redacteur_skill`, `critique_skill` — propres au dépôt du socle) et les rôles génériques non retenus ;
- **active** la spécialisation du développeur adaptée à la famille (copie depuis `specialisations/` vers `.claude/agents/`).

Les mises à jour du socle se propagent par `git remote add socle` + `git fetch socle && git merge socle/main` — semi-automatique, avec conflits possibles et dérive de version entre projets (chaque projet note sa version dans son `CLAUDE.md`, mais rien ne force le rattrapage).

**Faits techniques donnés** (vérifiés, non rediscutés ici) :
1. Un plugin Claude Code regroupe `commands/`, `agents/`, `skills/`, `hooks/`, éventuellement un `.mcp.json` ; il est distribué via une marketplace (dépôt git avec `.claude-plugin/marketplace.json`) et installé/activé **par utilisateur ou par projet**.
2. L'activation est **tout-ou-rien** : pas d'activation partielle par famille de projet.
3. Les composants sont **préfixés** par le nom du plugin (ex. `geoid:cadrer-projet`).
4. La mise à jour passe par la marketplace (git) : plus contrôlée qu'un merge, moins souple pour des ajustements locaux par projet.
5. Un plugin **ne peut fournir ni le `settings.json`** (permissions) **ni le `CLAUDE.md`** : ceux-ci restent distribués par template/cadrage. Il en va de même de `CHARTE.md`, fichier à la racine du dépôt projet, lu par tous les agents.
6. Le mécanisme actuel « retirer au cadrage » / « activer une spécialisation » **n'a pas d'équivalent plugin**.

**Contrainte de calendrier** : les REX des projets pilotes sont attendus. Un plugin publie une interface (noms préfixés de commandes, d'agents, déclencheurs de skills) qui entrera dans les habitudes et la documentation des équipes : la renommer après coup coûte cher. Le gel de cette interface ne doit donc pas précéder les retours pilotes.

## 2. Options

### Option A — Statu quo : diffusion par template + merge git

**Avantages**
- Zéro travail immédiat ; mécanisme documenté (README, DEMARRER) et éprouvé.
- Élagage fin par projet : retrait des skill-builder, sélection des rôles, activation d'une seule spécialisation — exactement le comportement voulu par le cadrage actuel.
- Tout est distribué par le même canal : agents, commandes, skills, `settings.json`, `CHARTE.md`, templates.
- Compatible avec la contrainte REX : rien à geler.

**Inconvénients**
- Propagation manuelle et par projet (`fetch` + `merge`) : dérive de version quasi certaine dès 3-4 projets actifs ; conflits de merge récurrents (le `CLAUDE.md` diverge par construction).
- Chaque projet porte une copie modifiable des agents : une correction locale « rapide » casse silencieusement l'uniformité du pôle.
- Aucune visibilité centrale sur qui utilise quelle version.

**Coût de réversibilité** : nul — c'est l'état de départ.

### Option B — Mono-plugin `geoid` contenant tout

Un seul plugin embarquant agents génériques, agents skill-builder, les trois spécialisations, les quatre commandes et les skills du pôle.

**Avantages**
- Un seul artefact à versionner, installer, mettre à jour ; le plus simple côté mainteneur.
- Mise à jour centralisée pour tous les projets.

**Inconvénients**
- L'activation tout-ou-rien **contredit frontalement le design du cadrage** :
  - les agents skill-builder — méta, réservés au dépôt du socle — deviennent délégables dans tous les projets d'équipe (`/creer-skill` et `/revue-socle` aussi) ;
  - les **trois** spécialisations du développeur coexistent partout, alors que le cadrage en active une seule : la délégation automatique (pilotée par les `description`) peut router une tâche vers `developpeur_back_geo` dans un projet ETL ;
  - les rôles non retenus par famille restent présents.
- Le compte d'agents visibles double dans chaque projet ; bruit pour des équipes en montée en compétences (objectif CHARTE §7).

**Coût de réversibilité** : moyen. Scinder le plugin après publication change les préfixes perçus (`geoid:creer-skill` → `geoid-meta:creer-skill`) et impose une double migration des projets.

### Option C — Deux plugins : `geoid` (équipes) + `geoid-meta` (mainteneur)

- **`geoid`** (installé/activé sur les projets d'équipe) : agents projet (`architecte`, `developpeur`, `analyste_sig`, `revieweur`, `documentaliste`, `chef_projet`, `mentor`), skills du pôle (`conventions-sig-tse`, `environnement-arcgis-tse`, `fme-tse`), commandes `/cadrer-projet` et `/cloturer-session`, et le script `generer_doc_html.py` (outillage d'équipe).
- **`geoid-meta`** (installé par le seul mainteneur du socle) : agents skill-builder, `/creer-skill`, `/revue-socle`, packageur `.skill`.
- Le dépôt template **subsiste, réduit** : `CHARTE.md`, `CLAUDE.md` bootstrap, `settings.json`, `templates/`, `specialisations/`, `DEMARRER.md` — tout ce qu'un plugin ne peut pas fournir (fait 5) reste diffusé par template + `/cadrer-projet`.

**Avantages**
- Sépare les deux publics réels : le problème « retirer les skill-builder au cadrage » **disparaît** — `geoid-meta` n'est simplement pas installé chez les équipes. L'étape correspondante de `/cadrer-projet` est supprimée, pas émulée.
- Mises à jour du cœur (agents, skills, commandes) centralisées et tracées par la marketplace ; fin des merges sur `.claude/agents/` et `.claude/skills/`.
- Les agents ne sont plus des copies modifiables par projet : l'uniformité du pôle est garantie techniquement (cohérent avec la note de conception du README : préférer les garanties techniques aux consignes).
- Le template résiduel continue de porter permissions et CHARTE, qui doivent rester versionnés et amendables par projet (dérogations actées au journal).

**Inconvénients**
- Deux canaux de diffusion à synchroniser (marketplace + template résiduel) : une évolution qui touche à la fois un agent (plugin) et la CHARTE (template) demande deux propagations.
- Le tout-ou-rien subsiste **à l'intérieur** de `geoid` : les rôles génériques non retenus par famille restent présents partout. Le cadrage ne peut plus les supprimer ; la table « Équipe d'agents » (§5 du `CLAUDE.md`) devient **normative** et l'orchestrateur ne doit déléguer qu'aux agents listés. C'est une consigne, plus une garantie — régression assumée et à documenter.
- Ajustement local d'un agent pour un projet : impossible dans le plugin (c'est aussi une vertu) ; passe par une surcharge dans `.claude/agents/` du projet, à encadrer.
- Sort des spécialisations à régler (voir option D).

**Coût de réversibilité** : faible vers A (désinstaller les plugins, re-merger le template complet) ; faible vers B (fusion des deux plugins, mais renommage des préfixes `geoid-meta:*`).

### Option D — Option C + spécialisations maintenues côté cadrage (variante recommandée)

Identique à C, avec un traitement explicite des spécialisations : elles **restent dans le dépôt template** (`specialisations/`) et `/cadrer-projet` continue de copier **la seule retenue** dans `.claude/agents/` du projet.

**Avantages**
- Préserve le comportement « une spécialisation active par projet », que le tout-ou-rien plugin ne sait pas faire ; pas de concurrence de délégation entre trois développeurs spécialisés.
- La spécialisation copiée devient de fait un fichier projet : elle peut être affinée localement (stack exacte du projet), ce qui correspond à son usage réel.
- Évite la sous-variante « un plugin par famille » (`geoid-etl`, `geoid-back`, `geoid-front` activés par projet) : techniquement possible (activation par projet, fait 1), mais trois artefacts supplémentaires à versionner pour trois fichiers Markdown — coût de maintenance disproportionné tant que les spécialisations tiennent chacune dans un fichier. À réexaminer si elles grossissent (hooks, scripts propres).

**Inconvénients**
- Les mises à jour des spécialisations continuent de se propager par merge du template, pas par le plugin — hétérogénéité assumée et documentée.
- Le `developpeur` générique (tronc commun dont héritent les spécialisations) vit dans le plugin alors que la spécialisation vit dans le projet : un décalage de version entre les deux est possible ; le cadrage devra noter la version du socle à la copie.

**Coût de réversibilité** : faible — basculer plus tard les spécialisations en plugins par famille ne casse ni les noms d'agents ni le contenu.

## 3. Décision recommandée

**Option D** (deux plugins `geoid` / `geoid-meta`, spécialisations maintenues côté template + cadrage) **comme architecture cible**, avec un **séquencement en deux temps** :

1. **Maintenant → fin des REX pilotes** : rester en option A (statu quo). Aucun gel d'interface avant les retours ; les corrections issues des pilotes (comme le fut CHARTE §3 / GeoJSON en 0.3.1) s'intègrent au fil de l'eau dans le template.
2. **Après intégration des REX** : publier la marketplace et les deux plugins (candidat naturel : version 0.5.0 du socle), réécrire `/cadrer-projet` en conséquence, migrer les projets actifs.

Justification : B est écarté car il contredit le design d'élagage du cadrage (fait 6) et pollue la délégation automatique dans tous les projets. A seul ne tient pas à l'échelle (dérive de version, merges répétés) — le README l'acte déjà. C sans traitement des spécialisations laisse le point le plus incompatible avec le tout-ou-rien sans réponse ; D le règle avec le mécanisme existant (règle 0 : réutiliser le cadrage plutôt que créer trois plugins).

## 4. Conséquences

### 4.1 Gestion de version (`SOCLE_VERSION` vs marketplace)
- `SOCLE_VERSION` reste la **source de vérité unique** ; le `CHANGELOG.md` reste unique. Les deux plugins publient la **même version**, alignée sur `SOCLE_VERSION` (le dépôt du socle devient lui-même la marketplace : un seul dépôt, un seul tag par release).
- `tests/test_socle_integrity.py` doit vérifier la cohérence `SOCLE_VERSION` ↔ versions déclarées dans `marketplace.json` / manifestes des plugins.
- Les projets notent désormais **deux états** dans leur `CLAUDE.md` : version du plugin `geoid` installée (mise à jour marketplace) et version du template résiduel mergée (CHARTE, settings, spécialisations). Le compte rendu de `/cloturer-session` peut signaler un décalage.

### 4.2 Migration des projets existants
- Par projet : installer/activer `geoid`, puis **supprimer de `.claude/`** les copies locales des agents génériques, commandes et skills désormais fournis par le plugin — sinon doublons (`/cadrer-projet` local non préfixé coexistant avec `geoid:cadrer-projet`) et divergence garantie.
- Conserver : `CLAUDE.md`, `settings.json` (et `.local.json`), `docs/`, la spécialisation copiée au cadrage, `CHARTE.md`.
- Fournir une **checklist de migration** dans le CHANGELOG (comme pour 0.4.0), et idéalement un script de vérification (détection des doublons plugin/local).
- Les projets non migrés continuent de fonctionner en mode A — pas de bascule forcée, mais une date butoir à fixer pour éviter le double régime prolongé.

### 4.3 `/cadrer-projet` réécrit
- **Supprimé** : retrait des agents skill-builder (ils ne sont plus là) ; suppression des rôles génériques non retenus (impossible dans un plugin).
- **Conservé** : génération `CLAUDE.md` + `docs/suivi-projet.md` ; copie de la spécialisation retenue ; relance de Claude Code en fin de cadrage.
- **Renforcé** : la table « Équipe d'agents » (§5) devient normative — ajouter au §0 (orchestration) du template projet : « ne délègue qu'aux agents listés au §5 », puisque tous les agents du plugin restent techniquement invocables.
- **Ajouté — propositions MCP par famille** : le cadrage propose (l'utilisateur valide) la configuration de serveurs MCP dans le `.mcp.json` **du projet** — pas dans le plugin, car les chaînes de connexion sont propres au projet et le tout-ou-rien imposerait tous les MCP partout :
  - famille **étude/analyse** : Postgres/PostGIS en **lecture seule** (identifiants RO uniquement, cohérent avec CHARTE §4 et le principe d'isolation du README — jamais de secret en clair, variables d'environnement) ;
  - famille **pipeline** : FME Flow MCP, **conditionné au passage en FME 2026.2** (à vérifier à chaque cadrage, pas supposé) ;
  - **ArcGIS Location Services MCP** : en veille, non proposé par défaut tant que non évalué.

### 4.4 Ce qui reste hors plugin (rappel des invariants)
`CLAUDE.md`, `settings.json`/permissions, `CHARTE.md`, templates et spécialisations restent diffusés par le template + cadrage (fait 5). Le durcissement des permissions de la 0.4.0 n'est donc **pas** propagé par la marketplace : toute évolution de `settings.json` continue d'exiger un merge — à mentionner dans la doc de maintenance.

### 4.5 REX pilotes avant gel
Les noms publiés (`geoid:cadrer-projet`, noms d'agents, déclencheurs de skills) sont l'interface du pôle : ils ne sont gelés qu'après intégration des retours pilotes. Tout renommage post-publication = migration de tous les projets + de la documentation ; c'est le coût principal qui justifie le séquencement en deux temps.

### 4.6 Documentation
`README.md` et `DEMARRER.md` sont à réécrire au moment de la bascule (installation marketplace remplace « Use this template » pour la partie agents ; le template reste l'étape 1 pour le squelette projet). `/revue-socle` s'applique à la PR de transposition (push significatif par excellence).

## 5. 🔧 À ARBITRER — points restants

| ADR | Sujet | Tâches bloquées en attendant | Statut |
|-----|-------|------------------------------|--------|
| ADR-001 | Choix de l'architecture de diffusion (A/B/C/**D recommandée**) et principe du séquencement en deux temps | — (les tâches restent conditionnées au calendrier ADR-001a : statu quo jusqu'aux REX pilotes) | **Décidé : option D** (2026-07-03) |
| ADR-001a | Critères et calendrier de bascule : combien de REX pilotes, quels critères de gel de l'interface (noms de commandes/agents/skills), date butoir de migration des projets | Publication de la marketplace ; tag 0.5.0 ; checklist de migration des projets existants | À décider (dépend d'ADR-001) |
| ADR-001b | Sort définitif des spécialisations : maintien côté cadrage vs plugins par famille — à réexaminer si les spécialisations s'enrichissent (hooks, scripts) | — | **Décidé via l'option D** : maintien côté cadrage (2026-07-03) |
| ADR-001c | Politique de version : alignement strict `SOCLE_VERSION` = version des deux plugins (recommandé) vs versionnage indépendant de `geoid-meta` | Premier tag de la marketplace ; extension de `test_socle_integrity.py` ; format des mentions de version dans le CLAUDE.md projet | À décider |
| ADR-001d | Périmètre des propositions MCP au cadrage : Postgres/PostGIS RO seul au départ ? conditions exactes FME Flow (2026.2) ; critères de sortie de veille pour ArcGIS Location Services | Ajout de l'étape MCP à `/cadrer-projet` ; gabarit `.mcp.json` projet ; consigne « identifiants RO, jamais en clair » dans le template | À décider |
