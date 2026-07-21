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
| ADR-001a | Critères et calendrier de bascule : combien de REX pilotes, quels critères de gel de l'interface (noms de commandes/agents/skills), date butoir de migration des projets | — (débloque S-04, S-05) | **Décidé : bascule immédiate** (2026-07-20) — voir §6 |
| ADR-001b | Sort définitif des spécialisations : maintien côté cadrage vs plugins par famille — à réexaminer si les spécialisations s'enrichissent (hooks, scripts) | — | **Décidé via l'option D** : maintien côté cadrage (2026-07-03) |
| ADR-001c | Politique de version : alignement strict `SOCLE_VERSION` = version des deux plugins (recommandé) vs versionnage indépendant de `geoid-meta` | — (débloque S-06) | **Décidé : alignement strict** (2026-07-20) — voir §6 |
| ADR-001d | Périmètre des propositions MCP au cadrage : Postgres/PostGIS RO seul au départ ? conditions exactes FME Flow (2026.2) ; critères de sortie de veille pour ArcGIS Location Services | Ajout de l'étape MCP à `/cadrer-projet` ; gabarit `.mcp.json` projet ; consigne « identifiants RO, jamais en clair » dans le template | **Décidé** (2026-07-21) — voir §8 |

## 6. Décisions ADR-001a et ADR-001c (2026-07-20)

Instruites par l'`architecte`, validées par D. Grohan. Fait nouveau
déclencheur : **table rase acceptée** — pas/peu de projets aval actifs en
régime « clone » à protéger.

### ADR-001a — **Bascule immédiate** (candidat 0.5.0)
- Le motif dominant du séquencement en deux temps (protéger des projets
  aval en cours de migration, §4.5) tombe avec la table rase. L'interface
  réellement nouvelle est minime : les noms d'agents, skills et commandes
  existent déjà et sont éprouvés en option A ; seuls sont neufs les
  préfixes `geoid:` / `geoid-meta:` (imposés par l'outil, fait 3), les
  identifiants des deux plugins + de la marketplace, et la frontière de
  découpage entre plugins.
- Le contenu (prompts, skills, commandes) reste corrigeable après
  publication par versions mineures de la marketplace : les REX pilotes
  s'intègrent en 0.5.x **sans coût de renommage**. La bascule est donc
  découplée de la consolidation des REX (S-03).
- **Garde-fou** : publier d'abord sur un canal `latest` (pré-release) ;
  ne couper le tag `stable` — celui que les projets épinglent — qu'après
  une **passe de verrouillage des noms**.
- **À figer avant publication** : identité marketplace + identifiants de
  plugins (`geoid`, `geoid-meta`) ; noms de commandes préfixés
  (`geoid:cadrer-projet`, `geoid:cloturer-session`,
  `geoid-meta:creer-skill`, `geoid-meta:revue-socle`) ; noms d'agents ;
  identifiants/déclencheurs de skills ; frontière de découpage entre les
  deux plugins.
- **Encore mobile après publication** (versions mineures, sans
  renommage) : contenu des agents/skills/commandes ; ajouts ; tout le
  versant template (hors plugin par construction, fait 5) ; propositions
  MCP (ADR-001d).
- **Date butoir** : nouveaux projets via marketplace dès 0.5.0. Projets
  résiduels — migration via checklist (§4.2) **ou** gel/archivage en
  option A ; fin de support de l'option A proposée à l'issue du cycle
  **0.6.0** (l'enjeu R-01 du double régime étant devenu marginal).
- **Débloque** : S-04 (tranché) et S-05.

### ADR-001c — **Alignement strict des versions**
- `SOCLE_VERSION` = version `geoid` = version `geoid-meta` = tag
  marketplace. Source de vérité unique (conforme au §4.1) ; le « bump à
  vide » d'un plugin sans diff est un coût accepté (mainteneur et release
  uniques).
- **`test_socle_integrity.py`** : ajouter un bloc de cohérence de version
  — `SOCLE_VERSION` == version de la marketplace == version déclarée pour
  chaque entrée de plugin == version de chaque manifeste
  (`.claude-plugin/plugin.json` de `geoid` et `geoid-meta`) ; en option,
  entrée de tête du `CHANGELOG.md`. Un seul nombre confronté à tous les
  manifestes.
- **CLAUDE.md projet** : deux champs (la version de `geoid-meta`
  n'apparaît pas côté projet, ce plugin n'y étant pas installé) —
  `Version socle — plugin geoid : X.Y.Z (marketplace) ; template
  résiduel : X.Y.Z (dernier merge).` `/cloturer-session` signale un écart
  entre les deux champs et un retard vis-à-vis de `SOCLE_VERSION` courant.
- **Débloque** : S-06.

### Impact sur le registre des risques
- **R-01** (dérive de version en régime merge) : se referme plus tôt.
- **R-02** (gel prématuré de l'interface) : la mitigation change de
  nature — ce n'est plus le report qui couvre le risque mais le
  verrouillage délibéré des noms + le canal `latest`/`stable`.
- **R-03** (REX tardifs → bascule sine die) : disparaît (bascule
  découplée des REX).

## 7. Verrouillage des noms et coupe du tag `stable` (2026-07-21)

Passe de verrouillage prévue par l'ADR-001a (garde-fou : publier d'abord
en `latest`/pré-release, ne couper `stable` qu'après le gel des noms).
Menée sur le dépôt à l'état de la 0.5.0 (tag `0.5.0`, pré-release
publiée), audit de cohérence des identifiants effectué et sans écart.

**Interface gelée** (tout renommage ultérieur = migration de tous les
projets + de la doc ; ne se fait plus qu'en version majeure) :
- **Marketplace** : `geoid-socle`.
- **Plugins** : `geoid` (équipes), `geoid-meta` (mainteneur).
- **Commandes** : `geoid:cadrer-projet`, `geoid:cloturer-session`,
  `geoid-meta:creer-skill`, `geoid-meta:revue-socle` (l'identifiant dérive
  du nom de fichier — pas de champ `name:` divergent).
- **Agents `geoid`** : `architecte`, `developpeur`, `analyste_sig`,
  `revieweur`, `documentaliste`, `chef_projet`, `mentor`.
- **Agents `geoid-meta`** : `interviewer_skill`, `redacteur_skill`,
  `critique_skill`.
- **Skills** : `conventions-sig-tse`, `environnement-arcgis-tse`,
  `fme-tse`.
- **Frontière de découpage** : agents projet + skills du pôle +
  `cadrer`/`cloturer` dans `geoid` ; skill-builder + `creer-skill` /
  `revue-socle` dans `geoid-meta`.

Hors gel (les spécialisations `developpeur_back_geo` /
`developpeur_front_carto` / `developpeur_etl` vivent dans le template
résiduel, pas dans l'interface plugin — renommables sans impact
marketplace).

**Encore mobile** malgré le gel des noms : le **contenu** des
agents/skills/commandes, les ajouts, le versant template, les propositions
MCP (ADR-001d). Le gel porte sur les identifiants, pas sur le texte.

**Conséquence** : le tag **`stable`** est coupé, marquant l'interface gelée.
Le canal `latest` reste ouvert pour itérer le contenu en 0.5.x sans coût de
renommage.

**Note pratique (2026-07-21)** — vérifié contre la doc Claude Code : le
`stable`/`latest` est un **modèle conventionnel**, pas un canal
auto-sélectionné par l'outil. En pratique, `/plugin marketplace add <repo>`
récupère l'état de `main`, et la version réellement installée est celle du
champ `version` des entrées de `marketplace.json`. Les tags `stable` /
`0.5.x` sont donc des **repères d'historique** (et une base de pin explicite
par `ref` si un jour on en a besoin) ; ils ne changent pas ce que reçoit une
équipe qui ajoute la marketplace. Choix acté : rester simple — `main` fait
foi pour ce que les équipes installent.

**Impact risque** : **R-02** (gel prématuré de l'interface) — fermé : le
gel est désormais délibéré et documenté, l'interface est majoritairement
éprouvée depuis l'option A, et le canal `latest` absorbe les itérations de
contenu.

## 8. Décision ADR-001d (2026-07-21) — périmètre MCP au cadrage

Instruite par l'`architecte` (recherche factuelle multi-sources, faits
datés/sourcés), validée par D. Grohan. Dernier point ouvert de l'ADR-001 :
il est désormais clos.

**Faits vérifiés (2026-07-21)** :
- Le serveur MCP Postgres « de référence » (`modelcontextprotocol`) est
  **archivé (2025-05-29)**, non maintenu et historiquement vulnérable à
  l'injection SQL → écarté. Des alternatives maintenues avec read-only
  paramétrable existent (`crystaldba/postgres-mcp` mode `restricted`,
  Supabase, Neon, HenkDz). PostGIS étant du SQL, un serveur SQL générique
  read-only suffit ; les serveurs « spatial-aware » dédiés sont immatures.
- **FME Flow comme serveur MCP** est officiel, natif et GA, mais **requiert
  FME 2026.2** (source primaire `fme.safe.com`) ; le transformer MCPCaller
  dès 2026.1 ; inclus sans surcoût, auth OAuth 2.0.
- **ArcGIS Location Services MCP (Esri)** : réel mais **en bêta** (endpoint
  distant hébergé Esri, clé API, facturation à la consommation, pas de GA) ;
  Early Adopter annoncé le 2026-06-29.

**Décisions** :
1. **Périmètre proposé au cadrage** (le cadrage propose, l'utilisateur
   valide ; jamais dans le plugin) :
   - **Étude / analyse** : **PostGIS lecture seule**, serveur par défaut
     **`crystaldba/postgres-mcp`** (`--access-mode=restricted`), avec un
     **rôle PostgreSQL dédié read-only**.
   - **Pipeline** : **FME Flow MCP**, **conditionné à FME ≥ 2026.2 vérifié
     au cadrage**. Fait d'environnement : le pôle est en **FME 2025.2** au
     2026-07 → FME MCP **non proposé** jusqu'à montée de version (point à
     rouvrir alors).
   - **Développement / pilotage** : aucun MCP par défaut.
2. **Esri ArcGIS Location Services** : **hors périmètre par défaut**,
   maintenu en veille (S-08). **Critères de sortie de veille** : (a) passage
   en GA annoncé par Esri ; (b) modèle de coût/quotas clair et compatible
   budget ; (c) besoin projet réel (géocodage/routing) ; (d) clé API gérée
   comme secret (variable d'environnement). Réévaluation à chaque signal.
3. **Sécurité (non négociable, CHARTE §4)** : identifiants **read-only**
   uniquement (rôle dédié, moindre privilège) ; **jamais de secret en
   clair** dans `.mcp.json` → **variables d'environnement** (`${VAR}`, que
   Claude Code interpole) ; le fichier versionné ne porte que des
   placeholders.
4. **Mise en œuvre** (portée par S-07) : étape « 2 bis — Serveurs MCP »
   ajoutée à `geoid:cadrer-projet` ; gabarit
   `templates/mcp.projet.template.json` ; consigne de sécurité MCP dans le
   template `CLAUDE.projet` ; livrés en **0.5.1** (contenu itéré sur le
   canal `latest`, sans renommage — les noms restent gelés, ADR §7).

**Impact risque** : **R-05** (identifiants en clair dans `.mcp.json`) —
mitigé et refermable : gabarit sans secret + `${VAR}` + rôle RO + consigne
au template et dans le cadrage. Reste à surveiller à l'usage (R-05 → en voie
de fermeture).
