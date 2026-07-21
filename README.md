# GéoID — Socle commun de la bibliothèque d'agents Claude Code

Socle commun du pôle GéoID (TSE). Depuis la 0.5.0, il se diffuse par
**deux canaux complémentaires** (ADR-001, option D) : une **marketplace de
plugins Claude Code** (agents, skills, commandes) et un **dépôt template
résiduel** (charte, permissions, `CLAUDE.md`, spécialisations) dont chaque
projet part et que `/cadrer-projet` adapte.

## Architecture : marketplace + template

| Source | Fichier(s) | Contenu | Diffusion |
|--------|-----------|---------|-----------|
| **Plugin `geoid`** | `plugins/geoid/` (agents, skills, commandes) | Rôles génériques, skills d'organisation, `geoid:cadrer-projet` / `geoid:cloturer-session` | Marketplace (installée par les équipes) |
| **Plugin `geoid-meta`** | `plugins/geoid-meta/` | Outillage mainteneur : skill-builder, `geoid-meta:creer-skill` / `geoid-meta:revue-socle` | Marketplace (installée par le seul mainteneur) |
| **Template résiduel** | `CHARTE.md`, `CLAUDE.md`, `.claude/settings.json`, `templates/`, `specialisations/` | Règles transverses, permissions, squelette projet, variantes du développeur | Template GitHub + merge git |
| **Projet** | `CLAUDE.md` + `docs/suivi-projet.md` (générés) | Objectif, données, livrables, équipe d'agents retenue, ADR, journal | Généré par `/cadrer-projet` |

La CHARTE prime ; le CLAUDE.md projet ne contient que ce qui s'y ajoute.
Un plugin ne peut fournir ni `CLAUDE.md`, ni `settings.json`, ni
`CHARTE.md` : c'est la raison d'être des deux canaux (ADR-001 §4.4).

## Structure

```
geoid-socle/
├── README.md
├── CHARTE.md                        règles transverses du pôle (template résiduel)
├── CLAUDE.md                        bootstrap — remplacé par /cadrer-projet
├── .claude-plugin/
│   └── marketplace.json             la marketplace : publie geoid et geoid-meta
├── plugins/
│   ├── geoid/                       PLUGIN équipes (installé par les projets)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                  rôles génériques
│   │   │   ├── architecte.md        décisions de conception, ADR (lecture seule)
│   │   │   ├── developpeur.md       tronc commun développement
│   │   │   ├── analyste_sig.md      études et analyses géographiques
│   │   │   ├── revieweur.md         revue avant livraison (ne produit pas)
│   │   │   ├── documentaliste.md    métadonnées, dictionnaires, doc, changelog
│   │   │   ├── chef_projet.md       backlog, risques, KPI, reporting
│   │   │   └── mentor.md            pédagogie — explique, ne fait jamais à la place
│   │   ├── commands/                geoid:cadrer-projet, geoid:cloturer-session
│   │   └── skills/                  skills d'organisation, chargés par Claude Code
│   └── geoid-meta/                  PLUGIN mainteneur (skills du socle)
│       ├── .claude-plugin/plugin.json
│       ├── agents/                  interviewer/redacteur/critique_skill
│       └── commands/                geoid-meta:creer-skill, geoid-meta:revue-socle
├── .claude/
│   └── settings.json                permissions : mode default + garde-fous (hors plugin)
├── specialisations/                 variantes du développeur, activées au cadrage
│   ├── developpeur_back_geo.md      PostGIS, APIs, chemin d'écriture
│   ├── developpeur_front_carto.md   interfaces carto, édition client
│   └── developpeur_etl.md           FME, pipelines, qualité de données
├── templates/
│   ├── CLAUDE.projet.template.md    squelette de la couche 2 (court, lu à chaque session)
│   ├── suivi-projet.template.md     roadmap/risques/revues → docs/suivi-projet.md
│   ├── fiche-outil.template.md      squelette de doc d'un outil (FME / Python / QGIS)
│   └── style-doc-tse.css            charte CSS TSE pour les fiches HTML
├── scripts/
│   ├── packager_skill.py            empaquette un skill en .skill (canal claude.ai)
│   └── generer_doc_html.py          génère une fiche-outil HTML autoportante (Markdown → HTML)
├── tests/                           tests d'intégrité et unitaires (stdlib)
├── requirements-dev.txt             dépendance de dev verrouillée (markdown)
└── .github/workflows/tests.yml      CI : les tests tournent à chaque push/PR
```

## Démarrer un projet

1. Créer un dépôt depuis ce template (GitHub → *Use this template*) —
   il fournit `CHARTE.md`, le `CLAUDE.md` bootstrap, `settings.json`,
   `templates/` et `specialisations/`.
2. `cd <projet> && claude`
3. Installer le plugin d'équipe depuis la marketplace :
   `/plugin marketplace add TSE-Pole-Geomatique/geoid_socle_pugin`, puis
   `/plugin install geoid@geoid-socle`. Les agents, skills et commandes du
   pôle deviennent disponibles (préfixés `geoid:`).
4. Lancer **`/cadrer-projet`** : entretien guidé, génération du
   `CLAUDE.md` et de `docs/suivi-projet.md`. La composition d'équipe
   retenue est inscrite au **§5 normatif** du CLAUDE.md (l'orchestrateur ne
   délègue qu'à ces agents) ; la seule spécialisation retenue est copiée
   dans `.claude/agents/` du projet.
5. **Quitter et relancer `claude`** : plugin, CLAUDE.md et spécialisation
   sont chargés au démarrage de la session, pas à chaud.
6. Si des points `🔧 À ARBITRER` existent : faire instruire les ADR par
   l'`architecte` avant les tâches qui en dépendent (le reste avance).

## Clôturer une session

En fin de séance, lancer **`/cloturer-session`** : le `chef_projet` met à
jour la roadmap et les risques (`docs/suivi-projet.md`) et le journal des
décisions (`CLAUDE.md`) à partir de ce qui a été produit, après
validation humaine. À lancer
volontairement quand la session a fait avancer le projet — pas
automatiquement, pour garder le contrôle de ce qui entre au suivi.

## Apprendre en faisant

Le `mentor` s'invoque à tout moment (« utilise le sous-agent mentor pour
m'expliquer… ») : concepts, code du projet, décisions, messages d'erreur.
Il explique et fait pratiquer, il ne produit jamais à votre place — c'est
voulu, et c'est ce qui fait progresser.

## Permissions

`.claude/settings.json` est versionné et s'applique à tous :
- mode `default` : les éditions de fichiers et les commandes non listées
  demandent confirmation. Pour une session explicitement dédiée à de
  l'implémentation, passer en `acceptEdits` **volontairement**
  (Maj+Tab en session, ou `defaultMode` dans `.claude/settings.local.json`) ;
- `allow` : lecture seule (ls, cat, grep, find, git diff/log/status,
  ogrinfo) et outillage borné du socle (`pytest`, `python3 tests/…`,
  `python3 scripts/packager_skill.py`, `python3 scripts/generer_doc_html.py`).
  **Volontairement absent : `python` / `python3` arbitraire** — un
  interpréteur généraliste contourne tous les autres garde-fous ; il
  demande donc confirmation à chaque fois ;
- `ask` : opérations engageantes (git add/commit/push, pip install, psql,
  ogr2ogr, curl/wget) ;
- `deny` : destructif (rm -rf, DROP/TRUNCATE) et lecture de secrets
  (`.env`, clés, credentials, `~/.ssh`, `~/.aws`).

⚠️ Honnêteté sur les limites : les patterns `deny`/`ask` sur Bash sont une
friction de premier niveau et un signal d'intention, **pas une protection
étanche**. La frontière technique réelle est double :
1. **Isolation des environnements** : jamais de credentials de production
   dans un environnement où les agents travaillent ; identifiants en
   lecture seule ou de dev/recette uniquement.
2. **Sandbox OS** (bubblewrap sous Linux/WSL2) : un squelette de
   configuration est présent dans `settings.json` (`"sandbox"`,
   désactivé). L'activer (`"enabled": true`) après un test sur un poste :
   il confine alors les commandes Bash (écriture limitée, réseau
   restreint aux domaines listés, secrets illisibles) au niveau de l'OS,
   pas seulement du prompt.

Ajuster localement via `.claude/settings.local.json` (non versionné) —
sans y réintroduire de passe-droit large type `Bash(git *)`.
Le mode `bypassPermissions` est réservé aux environnements isolés
(conteneur/VM) et peut être interdit par les réglages d'organisation.

## Maintenance du socle

- **Version** : voir `SOCLE_VERSION` et `CHANGELOG.md`. Depuis la 0.5.0,
  `SOCLE_VERSION` = version des deux plugins = version de la marketplace
  (alignement strict). Chaque projet note dans l'en-tête de son `CLAUDE.md`
  **deux champs** : version du plugin `geoid` installé (marketplace) et
  version du template résiduel mergé.
- **Tests** : `python3 tests/test_packager_skill.py`,
  `python3 tests/test_socle_integrity.py` et
  `python3 tests/test_generer_doc_html.py` avant push. La CI
  (`.github/workflows/tests.yml`) les rejoue à chaque push/PR, avec la
  dépendance `markdown` installée (`requirements-dev.txt`) pour qu'aucun
  test ne soit ignoré en silence.
- **Outillage documentation** : `scripts/generer_doc_html.py` produit une
  fiche-outil HTML autoportante depuis un Markdown (gabarit
  `templates/fiche-outil.template.md`, charte `templates/style-doc-tse.css`).
  Seule dépendance tierce du socle : `pip install markdown` (le reste est
  stdlib). Usage : `python3 scripts/generer_doc_html.py --source FICHE.md
  --output FICHE.html [--diagram SCHEMA.svg]`.
- **Avant tout push significatif** (nouvel agent, nouvelle commande,
  amendement de la CHARTE, permissions) : lancer `/revue-socle` — le
  socle passe par sa propre exigence de revue. Un verdict non APPROUVÉ
  bloque le push.

- Toute évolution de la CHARTE ou d'un agent générique se fait **ici**,
  par pull request.
- **Diffusion depuis la 0.5.0 : deux canaux** (ADR-001, option D). Le dépôt
  du socle est **lui-même la marketplace** (`.claude-plugin/marketplace.json`)
  et publie deux plugins :
  - **`geoid`** (`plugins/geoid/`) — agents, skills et commandes du pôle,
    installés par les équipes projet ;
  - **`geoid-meta`** (`plugins/geoid-meta/`) — outillage du mainteneur
    (skill-builder, `/revue-socle`, `/creer-skill`), installé par le seul
    mainteneur.

  Ces composants se propagent **par mise à jour de la marketplace**, plus
  par merge git. Les manifestes (`plugin.json`) et les entrées de la
  marketplace portent la même version que `SOCLE_VERSION` (alignement
  strict, ADR-001c — verrouillé par `test_socle_integrity.py`).
- **Ce qui reste hors plugin** (un plugin ne peut pas les fournir) :
  `CHARTE.md`, `CLAUDE.md`, `settings.json`/permissions, `templates/` et
  `specialisations/`. Ils continuent de se propager **par template +
  `/cadrer-projet`**, donc par merge git : `git remote add socle
  <url-du-depot-geoid-socle>` une fois, puis `git fetch socle && git merge
  socle/main` à chaque évolution (résoudre les conflits sur le `CLAUDE.md`,
  propre au projet). Le durcissement des permissions n'est donc **pas**
  propagé par la marketplace.
- **Migrer un projet existant** vers le mode plugin : suivre la checklist
  de la section 0.5.0 du `CHANGELOG.md` (installer la marketplace,
  supprimer les copies locales devenues des doublons, renseigner la ligne
  de version à deux champs, relancer Claude Code).

## Conventions de contribution

- Fiches d'agent : frontmatter `name` / `description` / `tools` ; le
  `description` détermine la délégation automatique — le soigner.
- `tools` en lecture seule pour les rôles qui ne doivent pas produire
  (`architecte`, `mentor`) : c'est une garantie technique, pas une
  contrainte. Exception assumée : le `revieweur` garde `Bash` pour
  exécuter les tests des livrables qu'il juge — sa non-production est
  donc une consigne, pas une garantie (documenté dans sa fiche).
- Toute nouvelle spécialisation suit le pattern « hérite du tronc commun
  `developpeur` + ajoute son périmètre ».
- Note de conception : les agents les plus solides sont ceux dont les
  **outils** diffèrent (`revieweur`, `mentor`, `architecte` en lecture
  seule — la séparation est garantie techniquement). `chef_projet` et
  `documentaliste` se justifient par la discipline de format de sortie,
  pas par leurs outils : ils sont optionnels par famille de projet, et
  leur maintien sera réévalué au premier retour d'expérience.
