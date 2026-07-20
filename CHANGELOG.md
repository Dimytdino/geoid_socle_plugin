# CHANGELOG — geoid-socle

Format inspiré de Keep a Changelog. La version vit aussi dans `SOCLE_VERSION`.
Chaque projet note la version du socle utilisée dans son `CLAUDE.md`.

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

- **2026-07-02** · Version 0.4.0 (skills → `.claude/skills/`, agents skill-builder permanents, permissions durcies, CHARTE §5 scoppée aux dépendances, suivi projet externalisé, test d'intégrité réécrit, CI) · **APPROUVÉ** (réserves levées). 1re passe SOUS RÉSERVE — deux références périmées : README « Clôturer une session » citait encore le CLAUDE.md pour la roadmap/risques ; note master/dérivé CHARTE §3 non mise à jour après le déplacement des skills et déclaration dérivée absente du SKILL.md `conventions-sig-tse` ; corrigées (+ suggestions appliquées : bootstrap CLAUDE.md, mémo DEMARRER, tableau des couches et arborescence README, deny `cat *.env*`, CI filtrée sur main). 3 tests verts.
- **2026-06-24** · Amendement CHARTE §3 (SRC d'un format d'échange prime ; GeoJSON = 4326) + skill `conventions-sig-tse` 1.0→1.1 + bump socle 0.3.1 · **APPROUVÉ** (réserve levée). 1re passe SOUS RÉSERVE — registre des skills affichait encore « Dernière revue : — » malgré la règle « régénérer à chaque amendement » ; corrigé (registre mis à jour : version 1.1, dernière revue 2026-06). Aucune contradiction introduite (front_carto §3857 = affichage, distinct du SRC de sortie) ; 3 tests verts.
- **2026-06-19** · Ajout `scripts/generer_doc_html.py` + test, templates `fiche-outil`/`style-doc-tse.css`, skill brouillon `fme-tse`, MAJ README/registre, retrait du `.pyc` suivi · **APPROUVÉ** (2e passe). 1re passe SOUS RÉSERVE — bloquant : `test_socle_integrity.py` scannait le disque au lieu de l'index git (faux positif sur `.skill` ignoré + `.pyc` tracké) ; corrigé (filtrage `git ls-files`, `.pyc` retiré de l'index), 3 tests verts.
