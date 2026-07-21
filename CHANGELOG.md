# CHANGELOG — geoid-socle

Format inspiré de Keep a Changelog. La version vit aussi dans `SOCLE_VERSION`.
Chaque projet note la version du socle utilisée dans son `CLAUDE.md`.

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
   TSE-Pole-Geomatique/geoid_socle_pugin`, puis `/plugin install
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
6. Vérifier l'absence de doublons (`geoid:` vs commande/agent local
   homonyme) avant de reprendre le travail.

Les projets non migrés continuent de fonctionner en mode « merge »
(option A) : pas de bascule forcée. Fin de support de l'option A proposée
à l'issue du cycle **0.6.0** (ADR-001 §6).

### Publication (2026-07-21)
- PR #1 mergée sur `main` (`a4df160`) ; **tag `0.5.0`** poussé ; pré-release
  publiée en **canal `latest`**.
- **Passe de verrouillage des noms** menée (ADR-001 §7) : marketplace,
  plugins, commandes préfixées, agents, skills et frontière de découpage
  gelés (audit sans écart) ; **tag `stable` coupé** — les projets
  l'épinglent, le canal `latest` reste ouvert pour itérer le contenu.

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

- **2026-07-20** · Version 0.5.0 (bascule en plugins : marketplace `.claude-plugin/`, plugins `geoid`/`geoid-meta`, alignement strict des versions, `/cadrer-projet` réécrit, checklist de migration, README/DEMARRER/bootstrap) · **APPROUVÉ** (réserve levée). 1re passe SOUS RÉSERVE — après le déplacement `.claude/skills/` → `plugins/geoid/skills/`, l'emplacement des skills restait écrit `.claude/skills/` dans `geoid-meta:creer-skill` (workflow inopérant), les agents `redacteur_skill`/`critique_skill`, le registre et la CHARTE §3 ; corrigés (+ titres de commandes préfixés, références GitHub `geoid_socle_pugin` dans DEMARRER, section « Nettoyage » de `creer-skill` réalignée). Versions alignées 0.5.0 partout, 3 tests verts.
- **2026-07-02** · Version 0.4.0 (skills → `.claude/skills/`, agents skill-builder permanents, permissions durcies, CHARTE §5 scoppée aux dépendances, suivi projet externalisé, test d'intégrité réécrit, CI) · **APPROUVÉ** (réserves levées). 1re passe SOUS RÉSERVE — deux références périmées : README « Clôturer une session » citait encore le CLAUDE.md pour la roadmap/risques ; note master/dérivé CHARTE §3 non mise à jour après le déplacement des skills et déclaration dérivée absente du SKILL.md `conventions-sig-tse` ; corrigées (+ suggestions appliquées : bootstrap CLAUDE.md, mémo DEMARRER, tableau des couches et arborescence README, deny `cat *.env*`, CI filtrée sur main). 3 tests verts.
- **2026-06-24** · Amendement CHARTE §3 (SRC d'un format d'échange prime ; GeoJSON = 4326) + skill `conventions-sig-tse` 1.0→1.1 + bump socle 0.3.1 · **APPROUVÉ** (réserve levée). 1re passe SOUS RÉSERVE — registre des skills affichait encore « Dernière revue : — » malgré la règle « régénérer à chaque amendement » ; corrigé (registre mis à jour : version 1.1, dernière revue 2026-06). Aucune contradiction introduite (front_carto §3857 = affichage, distinct du SRC de sortie) ; 3 tests verts.
- **2026-06-19** · Ajout `scripts/generer_doc_html.py` + test, templates `fiche-outil`/`style-doc-tse.css`, skill brouillon `fme-tse`, MAJ README/registre, retrait du `.pyc` suivi · **APPROUVÉ** (2e passe). 1re passe SOUS RÉSERVE — bloquant : `test_socle_integrity.py` scannait le disque au lieu de l'index git (faux positif sur `.skill` ignoré + `.pyc` tracké) ; corrigé (filtrage `git ls-files`, `.pyc` retiré de l'index), 3 tests verts.
