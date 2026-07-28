# Skills GéoID — registre, méthode et trame de rédaction

Document de travail du pôle GéoID (TSE). Il liste les skills à créer, donne
la méthode pour les rédiger efficacement, et fournit la trame à remplir.
Mainteneur : à désigner (proposition : Responsable de Projets Identification).

---

## 1. Rappel — quand créer un skill (le test en 5 questions)

Créer un skill quand la connaissance coche la plupart de ces cases :

1. **Spécifique TSE/GéoID** — introuvable sur le web, absente de la formation de Claude
2. **Récurrente** — règle des 3 : expliquée 3 fois à Claude dans des conversations différentes
3. **Partagée** — utile à plusieurs personnes du pôle
4. **Stable** — valable des mois sans modification
5. **À application automatique** — sa valeur vient du fait qu'elle s'applique sans qu'on y pense

Anti-critères : connaissance générale d'un outil (Claude l'a déjà),
connaissance propre à un seul projet (→ CLAUDE.md du projet),
règle d'orchestration d'agents (→ socle geoid-socle),
préférence individuelle (→ préférences utilisateur).

Hiérarchie : *préférence perso < CLAUDE.md projet < skill d'organisation < socle d'agents.*
Une connaissance vit à un seul étage.

---

## 2. Registre des skills

### Skills publiés

| Skill | Version | Date | Mainteneur | Source (master) | Dernière revue |
|-------|---------|------|------------|-----------------|----------------|
| `conventions-sig-tse` | 1.1 | 2026-06 | directeur du pôle | CHARTE §3 et §4 (master ; ce skill en est la copie dérivée, à régénérer à chaque amendement de la CHARTE) | 2026-06 (amendement CHARTE §3 — SRC format d'échange / GeoJSON 4326, socle 0.3.1) |
| `fme-tse` | 0.1 (brouillon) | 2026-06 | Kilian (contenu conventionnel) | Pilote « documentation FME » (ADR-002) — partie « structure de fiche » issue de la fiche covisibilité ; conventions de nommage/emplacement/staging/journalisation **à compléter par Kilian** | À passer en `/revue-socle` |
| `environnement-arcgis-tse` | 0.1 | 2026-06 | Fateh + Dimitry | Interview Dimitry (2026-06, `/creer-skill`) ; faits d'environnement recoupés avec ADR-001 du dépôt `nemelios_ags` (Enterprise 11.3, ExB Dev Edition 1.17, EPSG:2154). **À confirmer avec Fateh** : nombre d'applications métier, liste des intervenants ArcGIS, procédure VDI pas-à-pas | 2026-06 (création, critique APPROUVÉ) |

> Les skills sources vivent dans `plugins/geoid/skills/<nom>/` : c'est à la
> fois le dossier versionné (source de vérité) et le contenu embarqué par
> le plugin `geoid` — ils sont donc actifs dans tout projet où le plugin
> est installé (diffusion par la marketplace, non plus par copie template).
> Pour les utilisateurs claude.ai (chat), le canal est distinct : packager
> avec `scripts/packager_skill.py` puis faire publier le `.skill` par
> l'admin de l'organisation. Le fichier `.skill` est un **artefact
> généré**, non versionné (cf. `.gitignore`) — re-packager à chaque
> publication.
> ⚠️ Un skill encore en brouillon (non passé en `geoid-meta:revue-socle`)
> devient actif dès que le plugin `geoid` qui l'embarque est installé et
> rechargé : n'y laisser que des contenus qu'on assume de voir appliqués.

**Quand une revue d'un skill publié est obligatoire :** amendement de la
CHARTE (pour les skills dérivés), retour d'expérience d'un pilote, erreur
récurrente détectée, changement d'outil ou de version, extension à une
nouvelle population d'utilisateurs.

### Skills à créer

### Priorité 1 — à lancer maintenant

**`catalogue-outils-geoid`**
- Contenu : inventaire des outils existants du pôle — scripts Python, modèles
  QGIS, workflows FME, applis ExB, couches de référence. Pour chacun : nom,
  ce que ça fait (1-2 lignes), entrées/sorties, où ça vit, qui maintient.
- Se déclenche quand : quelqu'un demande à créer un traitement, un script, une
  analyse — Claude vérifie d'abord si un outil existant fait le travail.
  C'est la règle 0 (« réutiliser avant de créer ») rendue exécutoire.
- Source : Kilian (modèles, workflows, scripts), Fateh (applis, plateforme),
  François (études récurrentes).
- Rédacteur : chacun sa section, consolidation par le mainteneur.
  Effort : ~½ journée d'inventaire, puis vivant. Le pilote « documentation
  FME » de Kilian en produira automatiquement la section workflows.

### Priorité 3 — phase 2 (extension aux chargés d'identification)

**`identification-fonciere-tse`**
- Contenu : critères d'analyse d'une parcelle (cahier des charges société),
  lecture des documents d'urbanisme (PLU, règlements — ce qu'on y cherche),
  structure type d'une proposition de terrain, vocabulaire agences /
  sécurisation, format des tableaux de suivi.
- Se déclenche quand : parcelle, terrain, foncier, identification, urbanisme,
  PLU, secteur, proposition de site.
- Source : Simon + 1-2 chargés d'identification volontaires.
- C'est le skill qui rend Claude utile aux 7 chargés d'identification en mode
  chat, sans aucune formation technique. Effort : ~1 journée, le plus rentable
  de la phase 2.

**`livrables-geoid`**
- Contenu : structure attendue des livrables métier — note de synthèse
  d'analyse (question, méthode, résultats, limites), habillage des cartes
  (légende, échelle, sources), tableaux de suivi. Complète les chartes
  Word/PowerPoint/Excel existantes (mise en forme) par le fond métier.
- Se déclenche quand : note de synthèse, livrable, carte finale, restitution.
- Source : François + Simon. Effort : ~2 h.

### Vivier (à créer si la règle des 3 se confirme)

`postgres-tse` (schémas, conventions de nommage en base, rôles), 
`urbanisme-reglementaire` (spécificités agrivoltaïsme : loi APER, doctrine
départementale), `qgis-modeles-tse` (si le catalogue ne suffit pas),
`front-tse` (bonnes pratiques front-end génériques : TypeScript, gestion d'état,
deps — à sortir de `environnement-arcgis-tse` **uniquement si la règle des 3 se
confirme** sur d'autres projets front ; arbitrage 2026-06 : restent compressées
dans `environnement-arcgis-tse` pour l'instant).

---

## 3. Méthode de rédaction — 5 étapes, ~2 h par skill

### Étape 1 — Capturer (15 min)
Partir de conversations réelles : retrouver les 3 fois où on a expliqué la
chose à Claude. Ce qu'on a dû expliquer = le contenu du skill. Ce qu'on a
tapé comme demande = les déclencheurs.

### Étape 2 — Interviewer l'expert (30 min)
Le rédacteur n'est pas forcément l'expert. Questions à poser : quelles sont
les règles non négociables ? les pièges classiques d'un débutant ? les
exemples typiques (anonymisés) ? qu'est-ce qui change souvent (à exclure) ?

### Étape 3 — Rédiger avec Claude (30 min)
Donner à Claude la trame ci-dessous + les notes d'interview et lui demander
un premier jet. Puis couper : un skill court et précis bat un skill complet.
Viser moins de 200 lignes ; si ça dépasse 500, découper en fichiers de
référence annexes.

### Étape 4 — Tester (30 min)
Écrire 3 à 5 demandes réalistes (reprendre celles de l'étape 1) et les
soumettre dans une conversation neuve avec le skill installé :
- Le skill se déclenche-t-il ? Si non → muscler la `description`.
- La réponse applique-t-elle les règles ? Si non → clarifier le corps.
- Tester aussi une demande hors sujet : le skill ne doit PAS se déclencher.

Ces jeux de prompts ne sont pas jetables : les **figer** dans
`evals/<nom-du-skill>.eval.json` (déclencheurs + non-déclencheurs, dont au
moins un cas « frontière » où un skill voisin est attendu et un cas
hors-périmètre). La structure et la couverture sont vérifiées en CI
(`scripts/evaluer_declenchement.py`) ; le test de déclenchement réel se
rejoue à chaque revue via `--rapport`. Protocole complet et grille de
résultats : `evals/README.md`.

### Étape 5 — Publier et faire vivre (15 min)
Publication par l'admin de l'organisation Claude (propagation immédiate à
tout le pôle). Le mainteneur tient le registre ; toute personne qui constate
un manque ou une erreur le lui remonte. Révision à chaque REX de projet.

---

## 4. Trame SKILL.md à remplir

```markdown
---
name: nom-du-skill
description: "[Ce que fait le skill en 1 phrase.] Utiliser ce skill dès
  que [liste généreuse de déclencheurs : mots-clés, types de demandes,
  contextes — même si l'utilisateur ne mentionne pas explicitement X].
  [Si utile : ce que le skill ne couvre PAS, pour éviter les faux
  déclenchements.]"
---

# Titre du skill

[1-2 phrases : à quoi sert ce skill, pour qui.]

## Règles non négociables
[Les règles que Claude doit TOUJOURS appliquer. Numérotées, formulées en
impératif, vérifiables. Ex. : « Toujours déclarer le SRC ; ne jamais en
supposer un par défaut. »]

## Comment faire
[La démarche, les conventions, les valeurs par défaut. Concret : noms
exacts, chemins, versions, seuils.]

## Exemples
[1-3 exemples courts AVANT → APRÈS ou DEMANDE → BONNE RÉPONSE,
avec données anonymisées.]

## Pièges connus
[Les erreurs classiques et comment les éviter. C'est souvent la section
la plus précieuse.]

## Ce qui n'est pas couvert
[Renvois : « pour X, voir le skill Y / le CLAUDE.md du projet ».]
```

**La `description` est l'élément le plus important** : c'est elle seule qui
décide si le skill se déclenche. Les bonnes pratiques constatées :
- y mettre le QUOI et tous les QUAND (les déclencheurs ne vont jamais dans
  le corps, toujours dans la description) ;
- être volontairement insistant — les skills se déclenchent trop peu plutôt
  que trop : « utiliser dès que… même si l'utilisateur ne mentionne pas
  explicitement… » ;
- écrire les déclencheurs avec les mots que l'équipe emploie vraiment
  (« parcelle », « .fmw », « publier un service »), pas du vocabulaire
  abstrait.

---

## 5. Checklist avant publication

- [ ] La description contient le quoi + tous les déclencheurs, formulés
      avec les mots de l'équipe
- [ ] Corps < 200 lignes (500 max), pas de doc générale recopiée
- [ ] Aucune donnée confidentielle (coordonnées de parcelles, identités,
      secrets) dans les exemples
- [ ] Pas de doublon avec un autre skill, la CHARTE du socle ou un
      CLAUDE.md projet — une connaissance, un étage
- [ ] Testé sur 3-5 demandes réelles (déclenchement + application) et
      1 demande hors sujet (non-déclenchement)
- [ ] Jeu d'éval `evals/<nom>.eval.json` créé et vert
      (`python3 scripts/evaluer_declenchement.py`) — la CI refuse un skill
      publié sans éval
- [ ] Source et mainteneur identifiés dans le registre
```
