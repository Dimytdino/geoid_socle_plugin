# CHANGELOG — geoid-socle

Format inspiré de Keep a Changelog. La version vit aussi dans `SOCLE_VERSION`.
Chaque projet note la version du socle utilisée dans son `CLAUDE.md`.

## 1.2.0 — 2026-08

Lot 1 des correctifs de l'**audit externe du 2026-08-20** (S-19, S-35 volet 1,
S-32, S-33, S-34). Contenu du plugin modifié → bump **mineur** aligné
(`SOCLE_VERSION`, marketplace, les deux `plugin.json` — ADR-001c) : correctifs
et ajouts, aucune rupture d'interface.

⚠️ **Étape de release à ne pas oublier** — **deux** fichiers quittent le
résiduel pour le plugin : `templates/style-doc-tse.css` et
`scripts/generer_doc_html.py` (que la 1.1.0 y avait ajouté). `sync_template.py
--check` les signalera « en trop » côté `geoid_agents_template` et **ne les
supprime jamais automatiquement** : les retirer à la main du template, sinon
les projets gardent des copies mortes.

### Corrigé
- **Hook `SessionStart` (S-33)** — `adr_ouverts()` remontait toute ligne
  contenant `🔧` ou « À ARBITRER ». Double défaut : **faux positif
  systématique** (la prose explicative du §0 du gabarit, tronquée au milieu
  d'une phrase, annoncée comme point à arbitrer à chaque session de chaque
  projet — alors que la CHARTE §5 attache à cet état un blocage de production)
  et **faux négatif** (les vrais ADR ouverts, décrits dans le tableau du §9
  sans marqueur `🔧`, jamais détectés). Nouveau contrat explicite : les lignes
  de tableau de la section « Décisions en attente » dont la cellule Statut vaut
  `À décider` / `À arbitrer` / `Ouvert`, restituées sous la forme
  `ADR-00X — sujet`. Les lignes à placeholder `{{…}}` sont ignorées.
- **Test du hook (S-33)** — `tests/test_hooks.py` validait une chaîne
  synthétique dont le format n'existait dans aucun gabarit : vert alors que le
  hook était faux sur le seul fichier qu'il rencontre en production. La fixture
  est désormais **le gabarit réellement livré**. Règle posée : *un test de hook
  prend le gabarit livré comme fixture*.
- **Skill `fme-tse` exécutable côté projet (S-19)** — le skill prescrivait
  `scripts/generer_doc_html.py` et citait `documentation-fme/docs/…`, aucun des
  deux atteignable depuis un dépôt projet. Application de l'**option retenue
  par l'ADR-001 §2, jamais mise en œuvre** : `generer_doc_html.py` et sa charte
  `style-doc-tse.css` vivent maintenant dans `plugins/geoid/scripts/` et sont
  invoqués `${CLAUDE_PLUGIN_ROOT}/scripts/generer_doc_html.py`. Le script est
  rendu **autoportant** (son CSS est résolu à côté de lui, non plus par rapport
  à une racine de dépôt qui n'existe pas chez les équipes). Renvoi au dépôt
  pilote retiré.
- **Contradiction entre couches (S-32)** — la règle « déléguer du trivial coûte
  plus qu'il ne rapporte » n'existait qu'au gabarit projet (couche 2), quand la
  CHARTE §6 disait « la session principale ne fait pas le travail spécialisé »
  et que la CHARTE **prime** (`CHARTE.md:6`) : le seul garde-fou
  anti-délégation-inutile perdait l'arbitrage par construction. Le seuil est
  porté dans la CHARTE §6.

### Modifié
- **Modèle explicite par agent (S-25, volet 1)** — les **13** agents portaient
  zéro `model:` et héritaient donc tous du modèle de session. Désormais écrit :
  `opus` pour `architecte`, `revieweur` et `mentor` (le mentor est la mitigation
  du risque de reprise — le dégrader serait l'économie la plus mal placée) ;
  `haiku` pour `documentaliste`, `chef_projet` et `interviewer_skill` (gros
  volume, faible exigence de raisonnement) ; `inherit` **écrit explicitement**
  ailleurs, pour que la valeur soit révisable et non subie.
  ⚠️ À surveiller à l'usage : `documentaliste` (métadonnées ISO 19115) et
  `chef_projet` — un agent dégradé qui rate une règle CHARTE coûte plus que le
  modèle économisé. Volet `allowed-tools:` sur les 4 commandes **non traité**.
- **Amorçage des délégations allégé (S-34)** — les 10 fichiers d'agents et de
  spécialisations ordonnaient tous la relecture intégrale de la CHARTE
  (~1 520 tokens) pour 3 à 5 règles réellement applicables au rôle. Ces règles
  sont désormais **inlinées** dans chaque corps d'agent (déjà chargé : coût
  marginal nul), suivies de « consulte `CHARTE.md` si un point transverse sort
  de cette liste ». **Exception assumée : le `revieweur`** garde la lecture
  intégrale, il vérifie la conformité et a besoin du texte entier.
- **Matière brute d'entretien sortie du plugin des équipes** — l'unique
  `interview-brut.md` (~2 460 tokens, consommé par les seuls agents de
  `geoid-meta`) voyageait dans `plugins/geoid/skills/` : poids mort atteignable
  par tout agent d'un projet, et matière explicitement non revue citable comme
  source. Déplacé en `docs/interviews/environnement-arcgis-tse.md` ; les
  commandes et agents `geoid-meta` pointent le nouvel emplacement.

### Ajouté
- **Trois blocs au test d'intégrité** (le socle en comptait 12, non 11) :
  **13** — tout agent des deux plugins et des spécialisations porte un
  `model:` valide (verrouille S-25) ; **14** — le seuil anti-délégation-triviale
  figure dans la CHARTE autant qu'au gabarit (verrouille S-32) ; **15** — tout
  chemin de fichier cité par un `SKILL.md` est atteignable **depuis un dépôt
  projet**, c'est-à-dire sous `${CLAUDE_PLUGIN_ROOT}/` ou dans le résiduel du
  template — vérifier son existence dans le socle ne suffit pas, et c'est
  exactement ce qui rendait S-19 invisible (verrouille S-19).
  Les trois ont été vérifiés **rouges sur l'état d'avant**.

### Arbitrages tranchés au rebasage (S-26)
- **Emplacement du générateur HTML (S-19)** — deux réponses concurrentes
  coexistaient : la 1.1.0 avait ajouté `scripts/generer_doc_html.py` au
  **résiduel**, ce lot le place dans le **plugin**. C'est la seconde qui est
  retenue : l'ADR-001 §2 (option C, reprise telle quelle par l'option D
  retenue) liste explicitement ce script parmi le contenu du plugin `geoid`.
  L'état de la 1.1.0 contredisait donc l'ADR en vigueur. `RESIDUEL_FICHIERS`
  redevient `["CHARTE.md"]` et `tests/test_sync_template.py` encode désormais
  la règle inverse : **aucun script dans le résiduel**.
- **`model:` du `chef_projet`** — `inherit`, et non `haiku` comme le proposait
  le lot. La 1.1.0 (S-24) fait de ce rôle le porteur du découpage en incréments
  et de la formulation des critères de recette : l'hypothèse « fort volume,
  faible exigence de raisonnement » ne tient plus.
- **Numérotation des blocs d'intégrité** — la 1.1.0 occupe les blocs 1→16 ;
  les trois blocs du lot deviennent **17, 18 et 19**.
- **Collision d'identifiant** — le volet « modèle explicite par agent » du lot
  était numéroté `S-25`, identifiant déjà pris par le dogfooding du suivi. Il
  devient **S-35**.
- **Puce « Référence » du skill `fme-tse`** — le lot la supprimait sans lien
  avec S-19 ; elle est conservée.

## 1.1.0 — 2026-08

**Pilotage par incréments métier recettables, et hygiène du contexte projet**
(S-24). Deux dérives constatées sur un projet réel (`orion_agents`) : un
pilotage décrit en tâches et jalons, qui laissait passer des sprints 100 %
techniques non démontrables par le métier ; et un `CLAUDE.md` en croissance
monotone (184 lignes) parce que rien, dans le cycle de vie d'un projet, n'en
retirait jamais de contenu. Version mineure : contenu du plugin `geoid` et
gabarits modifiés, aucune rupture d'interface (noms gelés, ADR-001 §7).
Alignement strict des versions maintenu (ADR-001c).

### Ajouté
- **Discipline d'incrément dans le gabarit projet** : bloc « Incrément en
  cours » (§2, deux lignes : l'incrément et son critère de recette) et **cap
  de travail** au §0 — rattacher ce qu'on fait à l'incrément en cours, une
  obligation qui incombe à l'orchestrateur quand le `chef_projet` n'est pas
  activé au §5 (il est optionnel en familles étude et pipeline).
- **`templates/suivi-projet.template.md`** : tableau des incréments en tête
  (valeur métier, critère de recette observable, démo, statut jusqu'à
  `Recetté`), backlog rattaché à un incrément, et une table **« Recettes
  prononcées »** distincte du suivi des revues — la revue dit « conforme »,
  la recette dit « le métier en veut ».
- **Question obligatoire au cadrage** (`geoid:cadrer-projet`, point 2 bis) :
  premier incrément recettable — quoi, pour qui, sous quel délai, et
  qu'observera-t-on pour dire que c'est bon ; avec la consigne de reformuler
  quand la réponse est un moyen technique.
- **Critère de recettabilité** dans la grille socle du `revieweur`.
- **Étape 2 bis de dégraissage** dans `geoid:cloturer-session` : la seule
  passe du cycle où du contenu peut *sortir* du CLAUDE.md, vers `docs/`, et
  jamais sans l'accord de l'utilisateur.
- **Avertissement d'hygiène au démarrage** (`hooks/injecter_contexte.py`,
  non bloquant) : CLAUDE.md au-delà de **180 lignes**, ou porteur de sections
  qui n'ont pas à occuper le contexte permanent (glossaire, état
  d'avancement, roadmap, historique, comptes rendus, risques, revues).
- **Tests** : 4 cas d'hygiène dans `tests/test_hooks.py` ; blocs 15
  (la discipline d'incrément présente aux six endroits du socle) et 16
  (seuil identique entre hook, gabarit et les deux commandes, et marge du
  gabarit vierge) dans `tests/test_socle_integrity.py`.

### Modifié
- **Agent `chef_projet` réécrit** autour de l'incrément, désormais sa
  responsabilité première : découpage **vertical** (un résultat utilisable de
  bout en bout plutôt qu'une couche terminée), critère de recette obligatoire
  — pas de critère écrit, pas d'incrément —, leviers de redécoupage quand
  c'est trop gros, transposition aux familles sans interface (étude,
  pipeline), et KPI de **valeur livrée** avant KPI d'activité. Garde-fou
  explicite sur le cycle 100 % technique : possible, signalé, jamais l'état
  par défaut ; la dette se finance à l'intérieur d'un incrément porteur.
- **Bloc d'hygiène en tête du gabarit CLAUDE** avec son critère de tri :
  *une ligne reste ici si elle change une décision dans n'importe quelle
  session* ; sinon elle part dans `docs/`, lu à la demande.

### Publication
**Faite le 2026-08-23.** PR #23 fusionnée sur `main` (protégée depuis le
2026-08-03), CI verte ; tag `1.1.0` poussé et **release pleine** GitHub
(`latest`). Template **resynchronisé** — `geoid_agents_template` PR #2 :
gabarits `templates/` à jour et `scripts/generer_doc_html.py` entré au
résiduel, donc les nouveaux projets partent directement en 1.1.0.

Reste — **côté postes, pas côté socle** : les postes déjà équipés doivent
faire `claude plugin update geoid@geoid-socle` puis relancer `claude`.
L'étape de dégraissage et la discipline d'incrément ne s'appliquent qu'une
fois le plugin réinstallé (vérification : `claude plugin list`).

Au passage, hors périmètre de cette version : les deux décisions du
2026-08-03 annoncées « socle **et** template » n'avaient été appliquées
qu'au socle — corrigé (`geoid_agents_template` PR #3 : `Bash(cat:*)` retiré
de l'`allow`, bloc `sandbox` inerte supprimé), et le tag `stable`, orphelin
et 42 commits en arrière, a été supprimé. Voir S-27 et S-28 au suivi.

## 1.0.0 — 2026-07
**Première version officiellement supportée du socle** (décision du
2026-07-30). Passage en `1.0.0` de la version qui allait être publiée
(ex-`0.5.2`) : le socle est validé à l'usage (audit du 2026-07-30 — deux
pilotes aboutis), le **template de projet dédié** est en place (ADR-003 —
dépôt `geoid_agents_template`), et un **mainteneur est nommé** (Dimitry
Grohan ; suppléant à désigner). Alignement strict des versions maintenu
(ADR-001c). Identifiants d'interface toujours gelés (ADR-001 §7).

### Modifié
- **Skill `conventions-sig-tse` 1.1 → 1.2** : section « Ce qui n'est pas
  couvert » — renvois « (à venir) » retirés (`environnement-arcgis-tse` et
  `fme-tse` existent désormais). Sync CHARTE §3-§4 (master) revérifiée : à
  jour. Aucune règle modifiée.
- **Modèle de démarrage projet** (ADR-003) : le dépôt du socle n'est plus un
  template ; création de projet via `geoid_agents_template` (marketplace et
  plugin **déclarés** en `settings.json`). `DEMARRER.md`, `README.md` et le
  `CLAUDE.md` bootstrap réalignés.
  > **Rectificatif du 2026-07-31** : cette entrée annonçait une
  > « installation automatique » du plugin. C'est inexact — `enabledPlugins`
  > *active* le plugin mais n'installe pas de copie rattachée au projet, et
  > une session peut démarrer sans aucune commande `/geoid:…` ni agent.
  > Le chemin nominal comporte désormais une installation explicite
  > (`claude plugin install geoid@geoid-socle --scope user`, une fois par
  > poste), vérifiable par `claude plugin list`. Voir README §« Diagnostic ».

### Publication (à faire — mainteneur)
- Pousser le tag `1.0.0` + release.
- **claude.ai** : re-packager (`scripts/packager_skill.py`) et faire
  republier le `.skill` de `conventions-sig-tse` par l'admin de
  l'organisation (canal distinct de la marketplace ; artefact non versionné).

## 0.5.1 — 2026-07
Périmètre MCP au cadrage tranché (ADR-001d — dernier point ouvert de
l'ADR-001, désormais clos). Itération de **contenu** sur le canal `latest` :
les identifiants d'interface restent gelés (ADR-001 §7), aucun renommage.

### Ajouté
- **Étape « 2 bis — Serveurs MCP »** dans `geoid:cadrer-projet` : le cadrage
  propose (l'utilisateur valide) la configuration de serveurs MCP dans le
  `.mcp.json` **du projet**, par famille.
  - Étude/analyse : **PostGIS lecture seule** via `crystaldba/postgres-mcp`
    (`--access-mode=restricted`) + rôle PostgreSQL dédié read-only.
  - Pipeline : **FME Flow MCP** conditionné à **FME ≥ 2026.2** vérifié au
    cadrage (le pôle est en FME 2025.2 au 2026-07 → non proposé pour l'instant).
  - Esri ArcGIS Location Services : **hors périmètre** (bêta), en veille (S-08).
- **Gabarit `templates/mcp.projet.template.json`** : `.mcp.json` d'exemple
  avec placeholders `${VAR}`, sans aucun secret en clair.
- Consigne de sécurité MCP dans le template `CLAUDE.projet` (lecture seule,
  identifiants en variables d'environnement — CHARTE §4).

### Sécurité
- Règle actée (ADR-001d, CHARTE §4) : jamais de secret en clair dans
  `.mcp.json` ; identifiants **read-only** via **variables d'environnement**
  (`${VAR}`). Mitige R-05.

## 0.5.0 — 2026-07
Transposition du socle en **plugins Claude Code** (ADR-001, option D ;
bascule immédiate tranchée le 2026-07-20, ADR-001 §6). Le dépôt devient
lui-même la marketplace. Les agents, skills et commandes du pôle ne sont
plus diffusés par copie git mais installés/activés par la marketplace ;
CHARTE, `settings.json`, `CLAUDE.md`, templates et spécialisations restent
diffusés par le template résiduel (un plugin ne peut pas les fournir —
ADR-001 §4.4).

### Ajouté
- **Marketplace** `.claude-plugin/marketplace.json` : deux plugins publiés
  par le dépôt du socle.
- **Plugin `geoid`** (`plugins/geoid/`) — équipes projet : agents
  (`architecte`, `developpeur`, `analyste_sig`, `revieweur`,
  `documentaliste`, `chef_projet`, `mentor`), skills du pôle
  (`conventions-sig-tse`, `environnement-arcgis-tse`, `fme-tse`) et
  commandes `geoid:cadrer-projet`, `geoid:cloturer-session`.
- **Plugin `geoid-meta`** (`plugins/geoid-meta/`) — mainteneur du socle :
  agents skill-builder (`interviewer_skill`, `redacteur_skill`,
  `critique_skill`) et commandes `geoid-meta:creer-skill`,
  `geoid-meta:revue-socle`. Non installé chez les équipes : le retrait des
  skill-builder au cadrage disparaît par construction.
- **Bloc de cohérence de version** dans `test_socle_integrity.py`
  (ADR-001c, alignement strict) : `SOCLE_VERSION` = version de la
  marketplace = version de chaque manifeste `plugin.json`.

### Modifié
- **`/cadrer-projet` réécrit** (ADR-001 §4.3) : plus de suppression
  d'agents génériques ni de retrait des skill-builder sur disque ; la
  composition d'équipe retenue devient la **table normative du §5** du
  CLAUDE.md (tous les agents du plugin restant techniquement invocables,
  c'est le §5 qui fait foi) ; renfort au §0 du template « ne délègue qu'aux
  agents du §5 » ; copie de la seule spécialisation retenue conservée.
- **Template CLAUDE projet** : nouvelle ligne d'en-tête à **deux champs**
  de version (ADR-001c) — plugin `geoid` (marketplace) et template
  résiduel (dernier merge) ; `/cloturer-session` signale un écart.
- **Agents, skills et commandes déplacés** de `.claude/` vers
  `plugins/geoid/` et `plugins/geoid-meta/`. Le socle lui-même conserve
  `.claude/settings.json` (permissions, hors plugin).

### Migration des projets existants (checklist)
Par projet, une fois `geoid` disponible dans la marketplace :
1. **Installer la marketplace puis le plugin** : `/plugin marketplace add
   TSE-Pole-Geomatique/geoid_socle_plugin`, puis `/plugin install
   geoid@geoid-socle`. (Le mainteneur du socle installe en plus
   `geoid-meta`.)
2. **Supprimer de `.claude/` les copies locales** désormais fournies par le
   plugin — agents génériques (`.claude/agents/`), commandes
   (`.claude/commands/cadrer-projet.md`, `cloturer-session.md`) et skills
   du pôle (`.claude/skills/`). Sinon doublons : un `/cadrer-projet` local
   non préfixé coexisterait avec `geoid:cadrer-projet`, et les fichiers
   divergeraient silencieusement.
3. **Conserver** : `CLAUDE.md`, `settings.json` (+ `.local.json`), `docs/`,
   la spécialisation du développeur copiée au cadrage
   (`.claude/agents/developpeur_*.md`), `CHARTE.md`.
4. **Mettre à jour l'en-tête du `CLAUDE.md`** : renseigner la ligne à deux
   champs de version (plugin `geoid` installé / template résiduel mergé) ;
   vérifier que le §5 (équipe d'agents) est bien traité comme normatif.
5. **Relancer Claude Code** : plugin et CLAUDE.md ne sont pris en compte
   qu'au démarrage.
6. **Vérifier** avec `python3 scripts/verifier_migration_plugin.py` (à
   lancer dans le dépôt du projet) : il liste les doublons plugin/local
   restants et contrôle l'en-tête de version du `CLAUDE.md` (sortie non
   nulle tant que la migration est incomplète). Le lancer jusqu'à
   « migration propre » avant de reprendre le travail.

Les projets non migrés continuent de fonctionner en mode « merge »
(option A) : pas de bascule forcée. Fin de support de l'option A proposée
à l'issue du cycle **0.6.0** (ADR-001 §6).

### Publication (2026-07-21)
- PR #1 mergée sur `main` (`a4df160`) ; **tag `0.5.0`** poussé ; pré-release
  publiée en **canal `latest`**.
- **Passe de verrouillage des noms** menée (ADR-001 §7) : marketplace,
  plugins, commandes préfixées, agents, skills et frontière de découpage
  gelés (audit sans écart) ; **tag `stable` coupé** (repère d'interface
  gelée). En pratique les équipes installent l'état de `main` via
  `/plugin marketplace add` ; les tags sont des repères d'historique, pas un
  canal auto-sélectionné (ADR-001 §7, note pratique).

### À faire après cette version
- Intégrer les REX pilotes (S-03) au fil de l'eau en 0.5.x (contenu
  itérable sans coût de renommage, les noms étant gelés).
- Trancher ADR-001d (périmètre MCP au cadrage) → étape MCP de
  `geoid:cadrer-projet`, gabarit `.mcp.json`.
- Propager aux projets existants (S-09) via la checklist de migration
  ci-dessus.

## 0.4.0 — 2026-07
Durcissement issu d'un audit externe du socle (exécutabilité réelle des
skills et agents, permissions, contexte permanent). Faits vérifiés sur la
documentation Claude Code avant chaque changement.

### Ajouté
- **CI GitHub Actions** (`.github/workflows/tests.yml`) : les trois tests
  tournent à chaque push/PR ; `markdown` installé (`requirements-dev.txt`)
  pour que le test HTML ne soit jamais ignoré en silence.
- **`templates/suivi-projet.template.md`** : roadmap, registre des risques
  et suivi des revues sortent du CLAUDE.md projet (contexte permanent) vers
  `docs/suivi-projet.md`, lu à la demande.
- Squelette **sandbox OS** (bubblewrap, désactivé) dans `settings.json` —
  à activer après test sur un poste pour une frontière technique réelle.

### Modifié
- **Skills déplacés dans `.claude/skills/`** : c'était le point le plus
  trompeur du socle — `skills/` à la racine n'était jamais chargé par
  Claude Code, et les skills publiés dans claude.ai ne se propagent pas au
  CLI (canaux séparés). Ils sont désormais actifs dans le socle et dans
  tout projet créé du template. Le packaging `.skill` reste le canal
  claude.ai.
- **Agents skill-builder permanents** dans `.claude/agents/` : les agents
  copiés sur disque en cours de session ne sont chargés qu'au redémarrage —
  `/creer-skill` ne fait plus d'activation à chaud ; `/cadrer-projet` les
  retire des dépôts projet et exige une **relance de Claude Code** après
  cadrage (le CLAUDE.md généré n'est lu qu'au démarrage).
- **Permissions durcies** : `defaultMode` repasse de `acceptEdits` à
  `default` (acceptEdits se choisit par session) ; `python`/`python3`
  arbitraires et `git add`/`git commit` ne sont plus auto-autorisés (seuls
  les scripts du socle — tests, packageur, générateur de doc — le
  restent) ; `deny` étendu (`.env*`, `*.key`, credentials, `~/.ssh`,
  `~/.aws`). Le test d'intégrité verrouille ces choix.
- **Blocage ADR scoppé aux dépendances** (CHARTE §5) : un point
  `🔧 À ARBITRER` ne bloque plus que les tâches qui dépendent de la
  décision (colonne « Tâches bloquées » du tableau ADR) — analyses, doc,
  tests et maquettes avancent.
- `revieweur` : usage de `Bash` explicitement borné à la vérification
  (consigne assumée comme non garantie techniquement, cf. README).

### Corrigé
- `test_socle_integrity.py` : faux positif sur le registre (un skill
  publié mentionné en prose dans le vivier était compté « à créer ») —
  parsing structuré : tableau « Skills publiés » + titres en gras
  uniquement.

### Migration des projets existants
- `git fetch socle && git merge socle/main`, puis créer
  `docs/suivi-projet.md` depuis le template en y déplaçant les sections
  Roadmap (§10), Risques (§11) et Suivi des revues (§12) du CLAUDE.md ;
  le Journal des décisions devient §11 (géré par `/cloturer-session` au
  premier passage).
- Les skills du pôle deviennent actifs dans les projets après le merge
  (dossier `.claude/skills/`).

### À faire après cette version
- Commiter et pousser la 0.4.0 (branche dédiée + PR vers main — la CI
  tournera à la première PR).
- Re-packager et faire republier `conventions-sig-tse.skill` dans
  claude.ai (note master/dérivé ajoutée au SKILL.md).
- Activer le sandbox (`settings.json`) après test sur un poste WSL2
  (bubblewrap).
- Arbitrer le statut des skills brouillons dans `.claude/skills/`
  (actifs dès versionnés — assumé au registre, à confirmer).
- Propager aux projets : `git fetch socle && git merge socle/main`,
  puis migration du suivi (cf. ci-dessus).
- Construire les évaluations de déclenchement des skills (jeux de
  prompts déclencheurs / non-déclencheurs).

## 0.3.1 — 2026-06
### Corrigé (issu du REX des pilotes)
- **CHARTE §3** : ajout de la règle « le SRC d'un format d'échange prime sur
  le SRC de stockage » — GeoJSON (RFC 7946) impose EPSG:4326. Corrige la
  cause racine d'un bug du pilote `widget_export_geojson` (GeoJSON exporté
  en 2154/3857 « par conformité CHARTE », alors que le format impose le
  WGS84). Le point de vigilance écrit dans le REX n'avait pas suffi.
- **Skill `conventions-sig-tse`** (copie dérivée régénérée en conséquence) :
  nouvelle règle non négociable n°3, piège « GeoJSON exporté en 2154/3857 »,
  exemple d'export GeoJSON.

### À faire après cette version
- Repasser `/revue-socle` (amendement de la CHARTE = push significatif).
- Re-packager et republier le skill `conventions-sig-tse` (master/dérivé).
- Propager aux projets : `git fetch socle && git merge socle/main`.

## 0.3.0 — 2026-06
### Ajouté
- Commande `/cloturer-session` (mise à jour roadmap/risques/journal en fin de séance).
- Commande `/revue-socle` (revue du socle avant push significatif).
- Sections Roadmap, Registre des risques et Suivi des revues dans le template projet.
- `SOCLE_VERSION`, `CHANGELOG.md` et `tests/test_socle_integrity.py`.
- Section « Skills publiés » dans le registre.

### Modifié
- Orchestration proportionnée (délégation du substantiel, traitement direct du trivial ; revue des livrables finaux seulement).
- CHARTE/skill en master/dérivé explicite ; compromis langue (identifiants anglais, métier français).
- `pip install` passé en `ask`.
- `.skill` traité comme artefact généré, non versionné.

### Migration depuis une version sans ces sections
- Ajouter au `CLAUDE.md` des projets existants les sections Roadmap (§10), Registre des risques (§11) et Suivi des revues (§12).
- Renuméroter le Journal des décisions en §13.

## Suivi des revues du socle

Journal des passages `/revue-socle` (date · périmètre · verdict).

- **2026-07-21** · Version 0.5.1 (S-07 / ADR-001d — périmètre MCP au cadrage : étape « 2 bis » de `geoid:cadrer-projet`, gabarit `templates/mcp.projet.template.json`, consigne sécurité MCP au template) · **APPROUVÉ** (aucun bloquant). Point sécurité vérifié : gabarit sans secret (`${VAR}`), read-only à double détente (mode `restricted` + rôle BD dédié), consigne cohérente sur les 4 sources normatives (cadrage, template, ADR §8, CHARTE §4) ; versions alignées 0.5.1, 10 blocs d'intégrité + 3 tests verts. Deux durcissements suggérés appliqués (garde du bloc 10 élargie au-delà de `env` ; variable `POSTGIS_RO_URI` nommée dans la doc de cadrage).
- **2026-07-20** · Version 0.5.0 (bascule en plugins : marketplace `.claude-plugin/`, plugins `geoid`/`geoid-meta`, alignement strict des versions, `/cadrer-projet` réécrit, checklist de migration, README/DEMARRER/bootstrap) · **APPROUVÉ** (réserve levée). 1re passe SOUS RÉSERVE — après le déplacement `.claude/skills/` → `plugins/geoid/skills/`, l'emplacement des skills restait écrit `.claude/skills/` dans `geoid-meta:creer-skill` (workflow inopérant), les agents `redacteur_skill`/`critique_skill`, le registre et la CHARTE §3 ; corrigés (+ titres de commandes préfixés, références GitHub `geoid_socle_pugin` dans DEMARRER, section « Nettoyage » de `creer-skill` réalignée). Versions alignées 0.5.0 partout, 3 tests verts.
- **2026-07-02** · Version 0.4.0 (skills → `.claude/skills/`, agents skill-builder permanents, permissions durcies, CHARTE §5 scoppée aux dépendances, suivi projet externalisé, test d'intégrité réécrit, CI) · **APPROUVÉ** (réserves levées). 1re passe SOUS RÉSERVE — deux références périmées : README « Clôturer une session » citait encore le CLAUDE.md pour la roadmap/risques ; note master/dérivé CHARTE §3 non mise à jour après le déplacement des skills et déclaration dérivée absente du SKILL.md `conventions-sig-tse` ; corrigées (+ suggestions appliquées : bootstrap CLAUDE.md, mémo DEMARRER, tableau des couches et arborescence README, deny `cat *.env*`, CI filtrée sur main). 3 tests verts.
- **2026-06-24** · Amendement CHARTE §3 (SRC d'un format d'échange prime ; GeoJSON = 4326) + skill `conventions-sig-tse` 1.0→1.1 + bump socle 0.3.1 · **APPROUVÉ** (réserve levée). 1re passe SOUS RÉSERVE — registre des skills affichait encore « Dernière revue : — » malgré la règle « régénérer à chaque amendement » ; corrigé (registre mis à jour : version 1.1, dernière revue 2026-06). Aucune contradiction introduite (front_carto §3857 = affichage, distinct du SRC de sortie) ; 3 tests verts.
- **2026-06-19** · Ajout `scripts/generer_doc_html.py` + test, templates `fiche-outil`/`style-doc-tse.css`, skill brouillon `fme-tse`, MAJ README/registre, retrait du `.pyc` suivi · **APPROUVÉ** (2e passe). 1re passe SOUS RÉSERVE — bloquant : `test_socle_integrity.py` scannait le disque au lieu de l'index git (faux positif sur `.skill` ignoré + `.pyc` tracké) ; corrigé (filtrage `git ls-files`, `.pyc` retiré de l'index), 3 tests verts.
