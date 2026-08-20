# GéoID — Socle commun de la bibliothèque d'agents Claude Code

Socle commun du pôle GéoID (TSE). Depuis la 0.5.0, il se diffuse par
**deux canaux complémentaires** (ADR-001, option D) : une **marketplace de
plugins Claude Code** (agents, skills, commandes) et un **dépôt template
résiduel** (charte, permissions, `CLAUDE.md`, spécialisations) dont chaque
projet part et que `/geoid:cadrer-projet` adapte.

## Architecture : marketplace + template

| Source | Fichier(s) | Contenu | Diffusion |
|--------|-----------|---------|-----------|
| **Plugin `geoid`** | `plugins/geoid/` (agents, skills, commandes) | Rôles génériques, skills d'organisation, `geoid:cadrer-projet` / `geoid:cloturer-session` | Marketplace (installée par les équipes) |
| **Plugin `geoid-meta`** | `plugins/geoid-meta/` | Outillage mainteneur : skill-builder, `geoid-meta:creer-skill` / `geoid-meta:revue-socle` | Marketplace (installée par le seul mainteneur) |
| **Template résiduel** | `CHARTE.md`, `CLAUDE.md`, `.claude/settings.json`, `templates/`, `specialisations/` | Règles transverses, permissions, squelette projet, variantes du développeur | Template GitHub + merge git |
| **Projet** | `CLAUDE.md` + `docs/suivi-projet.md` (générés) | Objectif, données, livrables, équipe d'agents retenue, ADR, journal | Généré par `/geoid:cadrer-projet` |

La CHARTE prime ; le CLAUDE.md projet ne contient que ce qui s'y ajoute.
Un plugin ne peut fournir ni `CLAUDE.md`, ni `settings.json`, ni
`CHARTE.md` : c'est la raison d'être des deux canaux (ADR-001 §4.4).

## Structure

```
geoid-socle/
├── README.md
├── CHARTE.md                        règles transverses du pôle (template résiduel)
├── CLAUDE.md                        bootstrap — remplacé par /geoid:cadrer-projet
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
│   │   ├── skills/                  skills d'organisation, chargés par Claude Code
│   │   ├── scripts/                 outillage d'équipe livré (${CLAUDE_PLUGIN_ROOT})
│   │   │   ├── generer_doc_html.py  fiche-outil HTML autoportante (Markdown → HTML)
│   │   │   └── style-doc-tse.css    charte CSS TSE, inlinée par le script
│   │   └── hooks/                   garanties exécutables (PreToolUse secrets, SessionStart)
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
│   └── fiche-outil.template.md      squelette de doc d'un outil (FME / Python / QGIS)
├── scripts/
│   ├── packager_skill.py            empaquette un skill en .skill (canal claude.ai)
│   ├── verifier_migration_plugin.py détecte les doublons plugin/local d'un projet (migration 0.5.0)
│   ├── evaluer_declenchement.py     valide les jeux d'évals de déclenchement des skills
│   └── sync_template.py             synchronise le résiduel socle → geoid_agents_template
├── evals/                           jeux de déclenchement des skills (déclencheurs / non-déclencheurs)
├── docs/                            suivi-projet, ADR (adr/), notes de décision
├── tests/                           tests d'intégrité et unitaires (stdlib)
├── requirements-dev.txt             dépendance de dev verrouillée (markdown)
└── .github/workflows/tests.yml      CI : les tests tournent à chaque push/PR
```

## Utiliser le plugin `geoid` dans un projet

> Depuis la 1.0.0 (ADR-003), **ce dépôt n'est plus le template de projet**.
> Les projets partent du dépôt dédié **`geoid_agents_template`**, et le
> plugin leur arrive **par la marketplace**, jamais par copie de fichiers.

### Le circuit socle → template → projet

```
geoid_socle_plugin  (ce dépôt = dépôt de dev + marketplace « geoid-socle »)
│
├─ plugins/geoid, plugins/geoid-meta ──────────────► publiés par la marketplace ─┐
│                                                                               │
└─ résiduel : CHARTE.md, templates/, specialisations/                           │
        │  scripts/sync_template.py --apply  (étape de release, mainteneur)     │
        ▼                                                                       │
geoid_agents_template  (dépôt GitHub marqué « template »)                       │
   .claude/settings.json y déclare la marketplace + le plugin geoid ◄────────────┘
        │  « Use this template »
        ▼
mon_projet   →  claude plugin install geoid@geoid-socle (1×/poste)
             →  claude  →  /geoid:cadrer-projet
```

Deux canaux, deux natures : ce qu'un plugin **peut** fournir (agents, skills,
commandes, hooks) passe par la marketplace ; ce qu'il **ne peut pas** fournir
(`CHARTE.md`, `CLAUDE.md`, `.claude/settings.json`, `templates/`,
`specialisations/`) passe par le template (ADR-001 §4.4).

### Prérequis

- Claude Code installé et connecté ;
- accès à l'organisation GitHub **`TSE-Pole-Geomatique`** (dépôts privés :
  `gh auth login` ou une clé SSH fonctionnelle — la marketplace est résolue
  par git, donc l'accès au dépôt du socle est nécessaire).

### Chemin nominal — nouveau projet

1. Créer un dépôt depuis le template **`geoid_agents_template`**
   (GitHub → *Use this template* → Owner `TSE-Pole-Geomatique`, Private) —
   il fournit `CHARTE.md`, le `CLAUDE.md` bootstrap,
   `.claude/settings.json`, `templates/` et `specialisations/`.
2. Cloner. Au premier lancement de `claude`, Claude Code demande de **faire
   confiance au dossier** : c'est cette réponse qui rend le
   `.claude/settings.json` du dépôt actif (marketplace + plugin déclarés).
3. **Installer le plugin une fois par poste**, au scope `user` :
   ```bash
   claude plugin install geoid@geoid-socle --scope user   # --scope user est le défaut
   claude plugin list                                     # doit afficher geoid 1.1.0, scope user
   ```
   ⚠️ Ne pas compter sur la seule déclaration du template : `enabledPlugins`
   **active** le plugin, il ne garantit pas qu'une copie installée soit
   rattachée à ce projet. Cas rencontré : une session où `enabledPlugins`
   était bien lu mais où **ni les commandes, ni les agents `geoid:*`, ni les
   skills** ne se chargeaient, parce que la seule copie installée était au
   scope `local` d'un **autre** dépôt (et en 0.5.2). Voir « Diagnostic ».
4. **Relancer `claude`** : une installation de plugin ne prend effet qu'au
   démarrage suivant.
5. Lancer **`/geoid:cadrer-projet`** — les commandes de plugin sont
   **préfixées par le nom du plugin** : `/cadrer-projet` seul ne résout pas ;
   taper `/cadrer` dans le menu `/` suffit à la trouver. Entretien guidé,
   génération du `CLAUDE.md` et de `docs/suivi-projet.md`. La composition
   d'équipe retenue est inscrite au **§5 normatif** du CLAUDE.md
   (l'orchestrateur ne délègue qu'à ces agents) ; la seule spécialisation
   retenue est copiée dans `.claude/agents/` du projet.
6. **Quitter et relancer `claude`** : CLAUDE.md et spécialisation sont
   chargés au démarrage de la session, pas à chaud.
7. Si des points `🔧 À ARBITRER` existent : faire instruire les ADR par
   l'`architecte` avant les tâches qui en dépendent (le reste avance).

Le guide pas à pas complet (production, revue, clôture, règles d'or) vit
dans le `DEMARRER.md` du dépôt `geoid_agents_template`.

### Ce que déclare le template — et ce que ça ne garantit pas

Deux clés dans le `.claude/settings.json` du projet (déjà présentes dans le
template) : c'est le seul point d'attache entre un projet et le socle.

```json
{
  "extraKnownMarketplaces": {
    "geoid-socle": {
      "source": {
        "source": "github",
        "repo": "TSE-Pole-Geomatique/geoid_socle_plugin"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "geoid@geoid-socle": true
  }
}
```

Ce que ça fait : enregistre la marketplace `geoid-socle`, la rafraîchit au
démarrage (`autoUpdate` porte sur la **marketplace**, pas sur la copie
installée du plugin) et **active** `geoid` pour ce projet.

Ce que ça ne fait pas de façon fiable : **installer** le plugin. D'où
l'installation explicite au scope `user` à l'étape 3 — faite une fois, elle
vaut pour tous les projets du poste, et la déclaration du template continue
de jouer son rôle (choisir *quel* plugin est actif dans *quel* dépôt).

Le dépôt du socle étant privé, l'accès GitHub reste nécessaire : sans lui la
marketplace ne se résout pas et **aucune** commande `geoid:` n'apparaît.

### Vérifier que le plugin est actif

```bash
claude plugin list      # version + scope + statut, hors session
```

Attendu : `geoid@geoid-socle`, version = `SOCLE_VERSION`, scope `user`,
statut *enabled*. Puis, en session :

- les commandes `/geoid:cadrer-projet` / `/geoid:cloturer-session` sont
  proposées à la frappe de `/` ;
- les agents sont invocables sous leur nom préfixé (`geoid:architecte`,
  `geoid:revieweur`, …) ;
- le hook `SessionStart` du plugin injecte son rappel de contexte en début
  de session : s'il est absent, le plugin n'est pas chargé.

### Diagnostic — « le plugin est activé mais rien ne se charge »

`claude plugin list` affiche **une ligne par scope**, et un même plugin peut
exister en plusieurs exemplaires (`user`, `project`, `local`) à des versions
différentes. Symptôme typique : statut *enabled*, mais aucune commande ni
aucun agent dans la session, parce que la copie installée est rattachée à un
autre dépôt (scope `local`) ou périmée.

| Constat dans `claude plugin list` | Correctif |
|---|---|
| aucune ligne `geoid@geoid-socle` | `claude plugin install geoid@geoid-socle --scope user` |
| version < `SOCLE_VERSION` | `claude plugin update geoid@geoid-socle` |
| seule copie en scope `local` d'un autre dépôt | installer au scope `user` ; le cas échéant, se placer dans ce dépôt et `claude plugin uninstall geoid@geoid-socle --scope local` |

Dans tous les cas : **relancer `claude`** pour que le changement prenne
effet. Repère de contenu attendu en 1.1.0 : `commands/cadrer-projet.md` et
`cloturer-session.md`, les 7 agents, les 3 skills métier, les hooks
(`bloquer_secrets.py`, `injecter_contexte.py` — absents des versions 0.5.x) et
`scripts/generer_doc_html.py` (absent des versions ≤ 1.0.0).

### Projet existant, non issu du template

1. **Ajouter les deux clés** ci-dessus au `.claude/settings.json` du projet
   (versionné, donc valable pour toute l'équipe) ;
2. **installer le plugin** au scope `user` — une fois par poste :
   `claude plugin install geoid@geoid-socle --scope user` ;
3. relancer `claude`, puis vérifier avec `claude plugin list`.

Si la marketplace n'est pas connue du poste et qu'on veut l'enregistrer sans
passer par le `settings.json` : `/plugin marketplace add
TSE-Pole-Geomatique/geoid_socle_plugin` en session (ou `claude plugin
marketplace add`). À réserver aux essais : l'attache par `settings.json`
versionné est ce qui rend le rattachement reproductible pour l'équipe.

Si le projet contenait des copies locales des agents/skills du socle
(situation d'avant la 0.5.0), les supprimer : sinon elles font doublon avec
la version du plugin. Contrôle outillé, lancé **dans le dépôt du projet** :

```bash
python3 scripts/verifier_migration_plugin.py
```

Il détecte les doublons plugin/local restants et vérifie l'en-tête de
version à deux champs du `CLAUDE.md`. Checklist complète : section 0.5.0 du
`CHANGELOG.md`.

### Travailler au quotidien

| Besoin | Geste |
|--------|-------|
| Décision de conception, ADR | déléguer à l'agent `architecte` (lecture seule) |
| Implémentation | `developpeur` (+ la spécialisation retenue au cadrage) |
| Étude / croisement de couches | `analyste_sig` |
| Livrable « terminé » | `revieweur` — verdict avant livraison |
| Comprendre plutôt que produire | `mentor` |
| Fin de séance | `/geoid:cloturer-session` |

Les skills métier (`conventions-sig-tse`, `environnement-arcgis-tse`,
`fme-tse`) n'ont pas à être appelés : leur `description` les fait charger
automatiquement dès que la tâche touche leur domaine (les jeux d'`evals/`
du socle verrouillent ce déclenchement).

### Mettre à jour un projet

- **Plugin `geoid`** (agents, skills, commandes, hooks) : `autoUpdate`
  rafraîchit la **marketplace**, ce qui ne suffit pas toujours à faire
  avancer la copie installée. Contrôle : `claude plugin list` (version =
  `SOCLE_VERSION` attendu) ; sinon `claude plugin update geoid@geoid-socle`
  puis relancer `claude`.
- **Résiduel** (`CHARTE.md`, `templates/`, `specialisations/`) : par merge
  git depuis le dépôt template, alimenté par le socle à chaque release —
  une fois `git remote add template
  https://github.com/TSE-Pole-Geomatique/geoid_agents_template.git`, puis
  `git fetch template && git merge template/main` à chaque évolution
  (résoudre les conflits sur le `CLAUDE.md`, propre au projet).
- Après une mise à jour, actualiser la **ligne de version à deux champs**
  de l'en-tête du `CLAUDE.md` : version du plugin `geoid` installé et
  version du résiduel mergé.

## Clôturer une session

En fin de séance, lancer **`/geoid:cloturer-session`** : le `chef_projet` met à
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
  `python3 scripts/packager_skill.py`,
  `python3 plugins/geoid/scripts/generer_doc_html.py`).
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
- **Tests** (sept, `python3 tests/<nom>.py` avant push) : `test_socle_integrity`,
  `test_packager_skill`, `test_generer_doc_html`, `test_verifier_migration_plugin`,
  `test_evaluer_declenchement`, `test_sync_template`, `test_hooks`. La CI
  (`.github/workflows/tests.yml`) les rejoue à chaque push/PR, avec la
  dépendance `markdown` installée (`requirements-dev.txt`) pour qu'aucun
  test ne soit ignoré en silence.
- **Outillage documentation** : `plugins/geoid/scripts/generer_doc_html.py`
  produit une fiche-outil HTML autoportante depuis un Markdown (gabarit
  `templates/fiche-outil.template.md`, charte `style-doc-tse.css` livrée à
  côté du script). C'est de l'**outillage d'équipe embarqué dans le plugin**
  (ADR-001 §2) : côté projet il s'invoque
  `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generer_doc_html.py --source FICHE.md
  --output FICHE.html [--diagram SCHEMA.svg]`, et le skill `fme-tse` s'y
  réfère sous cette forme. Seule dépendance tierce du socle :
  `pip install markdown` (le reste est stdlib).
- **Avant tout push significatif** (nouvel agent, nouvelle commande,
  amendement de la CHARTE, permissions) : lancer `/geoid-meta:revue-socle` — le
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
    (skill-builder, `/geoid-meta:revue-socle`, `/geoid-meta:creer-skill`), installé par le seul
    mainteneur.

  Ces composants se propagent **par mise à jour de la marketplace**, plus
  par merge git. Les manifestes (`plugin.json`) et les entrées de la
  marketplace portent la même version que `SOCLE_VERSION` (alignement
  strict, ADR-001c — verrouillé par `test_socle_integrity.py`).
- **Ce qui reste hors plugin** (un plugin ne peut pas les fournir) :
  `CHARTE.md`, `CLAUDE.md`, `settings.json`/permissions, `templates/` et
  `specialisations/`. Ils se propagent **par template + `/geoid:cadrer-projet`** :
  le socle en est la source de vérité, une release le répercute dans
  `geoid_agents_template` (`python3 scripts/sync_template.py --check|--apply
  <clone_du_template>`, unidirectionnel), et les projets le reçoivent par
  merge git depuis le template (voir « Mettre à jour un projet »). Le
  durcissement des permissions n'est donc **pas** propagé par la
  marketplace, et le `settings.json` du template — propre au projet — se
  met à jour à la main (ADR-003).
- **Migrer un projet existant** vers le mode plugin : voir « Projet
  existant, non issu du template » ci-dessus et la checklist de la section
  0.5.0 du `CHANGELOG.md`.

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
