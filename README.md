# GéoID — Socle commun de la bibliothèque d'agents Claude Code

Dépôt **template** du pôle GéoID (TSE). Chaque nouveau projet du pôle part
de ce squelette : il embarque la charte transverse, une équipe d'agents
génériques, des spécialisations activables et une commande de cadrage qui
génère la configuration propre au projet.

## Architecture en deux couches

| Couche | Fichier(s) | Contenu |
|--------|-----------|---------|
| **1 — Socle** (ce dépôt) | `CHARTE.md`, `.claude/agents/`, `.claude/skills/`, `specialisations/`, `.claude/commands/`, `.claude/settings.json` | Règles transverses du pôle, rôles génériques, skills d'organisation, garde-fous |
| **2 — Projet** | `CLAUDE.md` + `docs/suivi-projet.md` (générés) | Objectif, données, livrables, équipe d'agents retenue, ADR, journal des décisions ; suivi opérationnel à part |

La CHARTE prime ; le CLAUDE.md projet ne contient que ce qui s'y ajoute.

## Structure

```
geoid-socle/
├── README.md
├── CHARTE.md                        règles transverses du pôle (couche 1)
├── CLAUDE.md                        bootstrap — remplacé par /cadrer-projet
├── .claude/
│   ├── settings.json                permissions : mode default + garde-fous
│   ├── agents/                      rôles génériques
│   │   ├── architecte.md            décisions de conception, ADR (lecture seule)
│   │   ├── developpeur.md           tronc commun développement
│   │   ├── analyste_sig.md          études et analyses géographiques
│   │   ├── revieweur.md             revue avant livraison (ne produit pas)
│   │   ├── documentaliste.md        métadonnées, dictionnaires, doc, changelog
│   │   ├── chef_projet.md           backlog, risques, KPI, reporting
│   │   ├── mentor.md                pédagogie — explique, ne fait jamais à la place
│   │   └── *_skill.md               interviewer/redacteur/critique — /creer-skill
│   │                                (retirés des projets au cadrage)
│   ├── commands/                    /cadrer-projet, /creer-skill,
│   │                                /cloturer-session, /revue-socle
│   └── skills/                      skills d'organisation — sources versionnées
│                                    ET chargées par Claude Code (actives ici
│                                    et dans tout projet créé du template)
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

1. Créer un dépôt depuis ce template (GitHub → *Use this template*).
2. `cd <projet> && claude`
3. Lancer **`/cadrer-projet`** : entretien guidé, génération du
   `CLAUDE.md` et de `docs/suivi-projet.md`, sélection des agents
   pertinents (les spécialisations retenues sont copiées dans
   `.claude/agents/`, les rôles inutiles retirés — le `mentor` reste
   toujours).
4. **Quitter et relancer `claude`** : CLAUDE.md et agents sont chargés
   au démarrage de la session, pas à chaud.
5. Si des points `🔧 À ARBITRER` existent : faire instruire les ADR par
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

- **Version** : voir `SOCLE_VERSION` et `CHANGELOG.md`. Chaque projet note
  dans son `CLAUDE.md` la version du socle utilisée.
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
- **Propager une mise à jour du socle vers un projet existant** (le mode
  template ne le fait pas tout seul) — une fois par projet :
  `git remote add socle <url-du-depot-geoid-socle>`, puis à chaque mise à
  jour : `git fetch socle && git merge socle/main` (résoudre les conflits
  éventuels sur le CLAUDE.md, qui est propre au projet). C'est
  semi-automatique ; la migration en plugin restera la vraie solution.
- Quand plusieurs projets seront actifs, envisager la migration du socle
  en **plugin Claude Code** installé centralement, pour que les mises à
  jour se propagent sans copie.

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
