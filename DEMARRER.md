# DÉMARRER — initialiser un projet GéoID pas à pas

Ce guide explique comment créer et démarrer un projet à partir du socle
`geoid-socle`. Du poste vide au premier livrable. Garde-le ouvert à côté
de toi la première fois.

> En une ligne : **template → `claude` → `/cadrer-projet` → trancher les
> ADR → produire → revue avant de livrer.**

---

## Étape 0 — Prérequis (une seule fois par poste)

- Un terminal avec **Node.js** installé.
- **Claude Code** : `npm install -g @anthropic-ai/claude-code`, puis
  `claude` une première fois pour se connecter avec le compte Claude TSE.
- Accès au dépôt **TSE-Pole-Geomatique/geoid-socle** sur GitHub.
- **Sous Windows** : travailler dans **WSL**, et garder les dépôts dans le
  home WSL (`~/...`), jamais dans `/mnt/c/...` (plus lent, problèmes de
  permissions).

Vérifier que tout est prêt :
```bash
node --version      # doit répondre une version
claude --version    # doit répondre une version
```

---

## Étape 1 — Créer le dépôt du projet depuis le template

Sur **GitHub** :
1. Ouvrir le dépôt `geoid-socle`.
2. Bouton **Use this template** → *Create a new repository*.
3. Nommer le projet en minuscules-tirets (ex. `pipeline-rpg`,
   `widget-export-geojson`, `orion-poc`).
4. Owner = l'organisation **TSE-Pole-Geomatique**, visibilité **Private**.
5. *Create repository*.

Puis cloner en local (dans WSL) :
```bash
cd ~
git clone https://github.com/TSE-Pole-Geomatique/<mon-projet>.git
cd <mon-projet>
```

---

## Étape 2 — Lancer Claude Code et cadrer le projet

```bash
claude
```
Au premier lancement dans le dossier, accepter de faire confiance au dépôt
(c'est notre template interne). Puis, dans la session :
```
/cadrer-projet
```

L'entretien guidé couvre, par petits groupes de questions :
- **identité** (nom, famille, commanditaire) ;
- **objectif** et critères de réussite ;
- **données** (sources, millésimes, sensibilité — foncier = confidentiel) ;
- **livrables** ;
- **environnement technique avec les versions exactes** (« à vérifier »
  plutôt que deviner) ;
- **existant à réutiliser** (règle 0) ;
- **décisions actées vs à arbitrer** (chaque point ouvert → un ADR) ;
- **équipe humaine et niveaux** (le mentor s'en sert pour calibrer).

À la fin : le `CLAUDE.md` du projet et `docs/suivi-projet.md` sont
générés, et l'équipe d'agents adaptée à la famille est sélectionnée.
**Quitter puis relancer `claude`** : le nouveau CLAUDE.md et l'équipe
d'agents ne sont chargés qu'au démarrage d'une session.

> Familles et agents typiques :
> - **étude / analyse SIG** → analyste_sig, revieweur, documentaliste, mentor
> - **pipeline de données** → architecte, developpeur_etl, revieweur, documentaliste, mentor
> - **développement applicatif** → architecte, developpeur_back_geo / front_carto, revieweur, documentaliste, chef_projet, mentor
> - **pilotage / transverse** → chef_projet, documentaliste, mentor

---

## Étape 3 — Faire trancher les décisions ouvertes (ADR)

Tant qu'un point est marqué `🔧 À ARBITRER` dans le `CLAUDE.md`, les
tâches qui **dépendent de cette décision** sont bloquées — le reste
(analyses, doc, tests, maquettes) avance. L'architecte instruit, **c'est
toi qui tranches**, et la décision est actée au journal.
```
Utilise le sous-agent architecte pour instruire ADR-001 et ADR-002.
```

---

## Étape 4 — Produire

Délègue le travail substantiel aux agents. Les actions sensibles
(base de données, `git push`, réseau) demanderont ta confirmation ; les
actions irréversibles exigent ton accord écrit explicite.
```
Implémente [la tâche], conformément aux ADR actés.
```

---

## Étape 5 — Comprendre en route (réflexe à prendre)

Dès qu'une notion n'est pas claire, le mentor est là — il explique sur le
code réel du projet, et ne fait jamais à ta place. Personne ne juge.
```
Utilise le sous-agent mentor pour m'expliquer [ce fichier / cette erreur /
ce concept] — je débute sur [sujet].
```

---

## Étape 6 — Revue, puis livraison

Tout livrable **final** passe par le revieweur, puis par toi. Les
corrections retournent à l'agent qui a produit, jamais au revieweur.
```
Fais passer [le livrable] en revue par le revieweur.
```
Après ta validation :
```bash
git add . && git commit -m "..."   # message en français, décrit le pourquoi
git push                           # demande confirmation
```

---

## Étape 7 — Clôturer la session

En fin de séance utile, mettre à jour le suivi du projet :
```
/cloturer-session
```
Le chef de projet (ou l'orchestrateur) met à jour la roadmap et les
risques (`docs/suivi-projet.md`) et le journal des décisions
(`CLAUDE.md`), **après ta validation**. À lancer volontairement, pas à
chaque micro-session.

---

## En cas de mise à jour du socle

Le mode template ne propage pas les évolutions du socle tout seul. Une
fois par projet, ajouter le socle comme source :
```bash
git remote add socle https://github.com/TSE-Pole-Geomatique/geoid-socle.git
```
Puis, à chaque évolution du socle :
```bash
git fetch socle && git merge socle/main
```
Résoudre les éventuels conflits sur le `CLAUDE.md` (il est propre au
projet). La version du socle utilisée est notée dans `SOCLE_VERSION`.

---

## Mémo des commandes

| Commande | Quand |
|----------|-------|
| `/cadrer-projet` | au démarrage d'un projet |
| `/creer-skill` | (sur le dépôt du socle) pour fabriquer un skill (interview → rédaction → critique) |
| `/cloturer-session` | en fin de séance utile |
| `/revue-socle` | (sur le dépôt du socle) avant un push significatif |

## Les règles d'or (rappel)

1. **Confidentialité** : jamais de coordonnées de parcelles, d'identités
   ou de stratégies de secteurs dans ce qui sort de TSE.
2. **Validation humaine** : toute action irréversible exige ton accord.
3. **Revue avant livraison** : aucun livrable final sans le revieweur.
4. **Esprit critique** : un agent affirme avec aplomb même quand il se
   trompe — vérifie ce qui compte.
5. **Le mentor d'abord** : comprends avant de copier-coller.
