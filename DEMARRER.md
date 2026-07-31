# DÉMARRER — socle GéoID (dépôt de développement)

Ce dépôt est le **socle** du pôle GéoID : il développe le plugin `geoid`
(et `geoid-meta`) publié via la **marketplace**, et il maintient le contenu
« résiduel » repris par le template de projet.

> **Ce dépôt n'est plus un template de projet** (décision ADR-003). Pour
> créer un projet, on part désormais du dépôt dédié `geoid_agents_template`
> (voir ci-dessous). Le socle reste le dépôt de dev + la marketplace.

---

## Créer un projet GéoID  → dépôt `geoid_agents_template`

Le parcours de création/prise en main d'un projet vit **dans le template** :

1. Sur GitHub, ouvrir **`TSE-Pole-Geomatique/geoid_agents_template`**.
2. **Use this template** → *Create a new repository* (Owner = TSE-Pole-Geomatique, Private).
3. Cloner. Le `.claude/settings.json` du template déclare la marketplace et
   **active** `geoid`, mais l'activation n'installe pas : faire une fois par
   poste `claude plugin install geoid@geoid-socle --scope user`, vérifier
   avec `claude plugin list` (version = `SOCLE_VERSION`, scope `user`), puis
   relancer `claude` — une installation ne prend effet qu'au démarrage
   suivant. Enfin `/geoid:cadrer-projet` (les commandes de plugin sont
   préfixées par le nom du plugin).

Le guide pas à pas complet (prérequis, cadrage, production, revue, clôture,
règles d'or) est le **`DEMARRER.md` du dépôt `geoid_agents_template`**. Il
n'est pas dupliqué ici pour éviter la dérive entre deux copies.

---

## Travailler sur le socle (mainteneur)

```bash
cd ~
git clone https://github.com/TSE-Pole-Geomatique/geoid_socle_plugin.git
cd geoid_socle_plugin
claude
```

- Outillage mainteneur : plugin **`geoid-meta`** (commandes
  `geoid-meta:creer-skill`, `geoid-meta:revue-socle`).
- Tests d'intégrité avant push :
  ```bash
  python3 tests/test_socle_integrity.py
  python3 tests/test_packager_skill.py
  python3 tests/test_generer_doc_html.py
  python3 tests/test_verifier_migration_plugin.py
  python3 tests/test_evaluer_declenchement.py
  python3 tests/test_sync_template.py
  ```
- Versionnage : **alignement strict** (ADR-001c) — `SOCLE_VERSION` = version
  de la marketplace = version de chaque `plugin.json`. Le bloc de cohérence
  du test d'intégrité le vérifie.
- Suivi opérationnel : `docs/suivi-projet.md` (roadmap, risques, journal des
  décisions) ; ADR : `docs/adr/`.

---

## Comment le socle se diffuse et se met à jour

Deux canaux (ADR-001 §4.4) :

- **Plugin `geoid`** (agents, skills, commandes, hooks) — par la
  **marketplace**. Publication d'une nouvelle version = merge sur `main`
  (+ tag de repère, cf. CHANGELOG). Côté poste, `autoUpdate` rafraîchit le
  clone de la marketplace ; la copie installée du plugin, elle, peut rester
  en arrière — d'où le contrôle `claude plugin list` (version attendue =
  `SOCLE_VERSION`) et, si besoin, `claude plugin update geoid@geoid-socle`
  puis relance de `claude`. Cas piégeux observé : plusieurs copies d'un même
  plugin coexistent par scope (`user` / `project` / `local`) ; une copie
  `local` rattachée à un autre dépôt affiche *enabled* sans rien charger
  dans le projet courant (voir README, « Diagnostic »).
- **Résiduel** (CHARTE, `templates/`, `specialisations/`) — le socle en est
  la **source de vérité** ; il est répercuté dans `geoid_agents_template`,
  d'où les projets le reçoivent (copie au départ, `git merge` ensuite).
  Répercussion via `scripts/sync_template.py`, à lancer sur un clone du
  template au moment d'un release :
  ```bash
  python3 scripts/sync_template.py --check <clone_geoid_agents_template>   # détecte la dérive
  python3 scripts/sync_template.py --apply <clone_geoid_agents_template>   # recopie le résiduel
  ```
  Puis committer/pousser dans le clone (sens unidirectionnel : le socle fait foi).

Le `.claude/settings.json` **n'est pas** dans ce résiduel : celui du template
est **propre au projet** (permissions + déclaration du plugin) et diffère de
celui du socle (permissions mainteneur). Un durcissement de permissions
destiné aux projets se porte **à la main** sur le `settings.json` du template
(ADR-003 ; décision de ne pas le synchroniser, pour ne pas écraser la version
projet).

---

## Mémo des commandes (mainteneur)

| Commande | Quand |
|----------|-------|
| `geoid-meta:creer-skill` | fabriquer un skill (interview → rédaction → critique) |
| `geoid-meta:revue-socle` | avant un push significatif |
| `geoid:cadrer-projet` / `geoid:cloturer-session` | (côté projet) — voir le template |

## Rappels transverses

Les règles du pôle s'appliquent au socle comme aux projets : voir
**`CHARTE.md`** (confidentialité foncière, validation des actions
irréversibles, revue avant livraison, réutiliser avant de créer).
