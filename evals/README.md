<!-- ════════════════════════════════════════════════════════════════
     evals/ — évaluations de déclenchement des skills GéoID (S-13)
     Outillage mainteneur du socle : ces jeux ne sont PAS embarqués par
     le plugin geoid (comme tests/ et scripts/), ils ne changent donc pas
     le contenu publié → pas de bump de version.
     ════════════════════════════════════════════════════════════════ -->

# Évals de déclenchement des skills

Un skill ne vaut que par sa `description` : c'est **elle seule** qui décide
s'il s'active (cf. `skills-geoid-registre-et-methode.md` §4). Ces évals
figent, pour chaque skill publié, deux jeux de prompts :

- **déclencheurs** — le skill **doit** s'activer ;
- **non-déclencheurs** — il **ne doit pas** s'activer, pour deux raisons
  distinctes qu'on teste toutes les deux :
  - *frontière* : un skill **voisin** est attendu à la place
    (champ `skill_attendu`) — teste le **sur-déclenchement** ;
  - *hors-périmètre* : **aucun** skill n'est attendu (pas de `skill_attendu`).

Le risque le plus fréquent est le **sous-déclenchement** (le skill dort alors
qu'il devrait parler) : d'où des déclencheurs volontairement variés, y compris
sans le vocabulaire « évident » (pas de « SRC », pas de « fiche »…).

## Fichiers

Un fichier par skill publié : `evals/<nom-du-skill>.eval.json`.

```json
{
  "skill": "<nom, = celui du dossier plugins/geoid/skills/<nom>>",
  "version_skill_evaluee": "1.1",
  "note": "contexte libre (facultatif)",
  "declencheurs":     [ { "prompt": "…", "pourquoi": "…" } ],
  "non_declencheurs": [ { "prompt": "…", "pourquoi": "…",
                          "skill_attendu": "<autre skill>"  } ]
}
```

`skill_attendu` est **facultatif** : présent = cas frontière, absent = cas
hors-périmètre.

## Deux passes : structure (auto) puis déclenchement réel (manuel)

Le déclenchement réel dépend d'un LLM avec le skill installé ; il n'est donc
**pas testable hors ligne**. On sépare donc :

### 1. Validation de structure — automatique, en CI

```bash
python3 scripts/evaluer_declenchement.py            # sortie 1 si un défaut
```

Contrôle : un fichier par skill publié (pas d'orphelin), champ `skill`
cohérent, seuils de couverture (≥ 5 déclencheurs, ≥ 3 non-déclencheurs), les
**deux** types de non-déclencheurs présents, `skill_attendu` visant un skill
publié réel, aucun prompt en double. Verrouillé par
`tests/test_evaluer_declenchement.py` (lancé en CI).

### 2. Test de déclenchement réel — manuel, à chaque revue de skill

```bash
python3 scripts/evaluer_declenchement.py --rapport   # prompts à copier-coller
```

Protocole (méthode §4, étape 4) :

1. Ouvrir une conversation **neuve** avec le plugin `geoid` installé et rechargé.
2. Coller chaque **déclencheur** : le skill attendu doit s'activer et sa règle
   doit s'appliquer. S'il ne se déclenche pas → **muscler la `description`**
   (ajouter le déclencheur manquant), pas le corps.
3. Coller chaque **non-déclencheur** : le skill ne doit pas s'activer ; sur un
   cas *frontière*, c'est le `skill_attendu` qui doit parler. S'il se déclenche
   à tort → resserrer la `description` (préciser le « Ne couvre pas… »).
4. Consigner le résultat dans la grille ci-dessous et, si un correctif de
   `description` en découle, le porter puis re-tester.

### Grille de résultats (à dater à chaque passe)

| Date | Skill | Déclencheurs OK | Non-décl. OK | Correctif `description` | Testeur |
|------|-------|-----------------|--------------|-------------------------|---------|
| —    | conventions-sig-tse | / | / | — | — |
| —    | environnement-arcgis-tse | / | / | — | — |
| —    | fme-tse | / | / | — | — |

> `fme-tse` et `environnement-arcgis-tse` sont en **0.1 (brouillon)** : ces
> évals servent de base d'entrée au passage `geoid-meta:revue-socle` (S-13
> alimente S-12).

## Ajouter un skill

À la création d'un skill (`geoid-meta:creer-skill`), ajouter son
`evals/<nom>.eval.json` **dans la même PR** : la CI refuse un skill publié sans
jeu d'éval.
