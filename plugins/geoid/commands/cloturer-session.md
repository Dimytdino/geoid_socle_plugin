---
description: >
  Clôturer une session de travail : le chef de projet met à jour les
  incréments, la roadmap / le backlog et les risques
  (docs/suivi-projet.md), l'incrément en cours et le journal des
  décisions (CLAUDE.md), et propose de dégraisser le CLAUDE.md de ce qui
  n'a plus à occuper le contexte. À lancer volontairement en fin de
  séance, quand la session a fait avancer le projet.
---

# Clôturer la session — /cloturer-session

Tu fais le point de fin de séance et tu confies la mise à jour du suivi
au `chef_projet`. À ne lancer que si la session a produit quelque chose
qui mérite d'être tracé — sinon, répondre que rien ne justifie une mise
à jour et s'arrêter.

## Étape 1 — Synthèse de la session
Établis un résumé court et factuel de ce qui s'est passé dans la session :
- ce qui a été produit ou modifié (livrables, fichiers, décisions) ;
- **où en est l'incrément en cours** (§2 du CLAUDE.md) : a-t-il avancé,
  est-il prêt à être montré, son critère de recette est-il atteint ? Si
  la session n'a rien fait avancer d'un incrément métier, le dire
  franchement plutôt que de le masquer derrière une liste de tâches ;
- les ADR tranchés, le cas échéant ;
- ce qui a été commencé mais non terminé ;
- les points bloquants apparus.
Si rien de significatif n'a été produit, le dire et arrêter là.

## Étape 2 — Mise à jour par le chef de projet
Délègue au `chef_projet` :
```
Utilise le sous-agent chef_projet pour mettre à jour le CLAUDE.md à
partir de cette synthèse de session : [coller la synthèse de l'étape 1].
```
Si le `chef_projet` n'est pas activé sur ce projet (familles étude ou
pilotage léger), l'orchestrateur fait lui-même la mise à jour des
sections de suivi, selon les mêmes règles ci-dessous.
Le `chef_projet` met à jour :
- dans **`docs/suivi-projet.md`** : le **tableau des incréments**
  (statuts À faire / En cours / En recette / Recetté / Abandonné, et la
  table des recettes prononcées si une recette a eu lieu), la roadmap /
  le backlog (statuts À faire / En cours / En revue / Terminé / Bloqué,
  nouvelles tâches identifiées — chacune rattachée à un incrément) et le
  registre des risques si un point bloquant est apparu ;
- dans le **CLAUDE.md** : le bloc **« Incrément en cours »** du §2 si
  l'incrément a changé (recetté → on passe au suivant), et le journal des
  décisions — toute décision actée pendant la session, au format
  `| AAAA-MM-JJ | sujet | décision | justification |`.

Si le tableau des incréments est vide ou absent alors que le projet
produit des livrables, il le signale : c'est le symptôme d'un pilotage
par tâches. Il propose alors un découpage en incréments à valider.

Il ne touche qu'à ces sections de suivi : il ne réécrit pas l'objectif,
la stack ou les conventions du projet. (Projet cadré avant le socle
0.4.0, sans `docs/suivi-projet.md` ? Le créer depuis
`templates/suivi-projet.template.md` en y déplaçant les sections
Roadmap / Risques / Suivi des revues du CLAUDE.md.)

## Étape 2 bis — Dégraissage du CLAUDE.md
Le CLAUDE.md est lu **en entier à chaque session** : sans passe de
retrait, il ne fait que grossir. Le `chef_projet` (ou l'orchestrateur)
vérifie sa taille et son contenu, et **propose** — sans jamais supprimer
d'office — de déplacer vers `docs/` ce qui n'a plus à occuper le contexte
permanent :
- au-delà de ~180 lignes, signaler la dérive et proposer une coupe ;
- ce qui n'y a jamais sa place : glossaire, état d'avancement, historique
  de sprints, roadmap ou backlog, comptes rendus de session, tutoriels,
  recopie de la CHARTE ou d'un skill du plugin `geoid` ;
- critère de tri : *une ligne reste si elle change une décision dans
  n'importe quelle session*.
Le contenu déplacé n'est pas perdu : il part dans un fichier de `docs/`
(par exemple `docs/glossaire.md`), et le CLAUDE.md n'en garde qu'un
renvoi d'une ligne. Rien n'est retiré sans l'accord de l'utilisateur
(étape 3). Si le fichier est déjà court et bien rangé, le dire en une
phrase et passer à l'étape suivante.

## Étape 3 — Validation humaine
Présente à l'utilisateur un récapitulatif des modifications proposées
(suivi, journal, et les déplacements vers `docs/` de l'étape 2 bis)
**avant de les enregistrer** : la roadmap est un document de référence,
l'humain valide ce qui y entre — et ce qui en sort (cf. CHARTE —
l'humain décide).
- Si l'utilisateur valide : enregistrer les modifications.
- S'il amende : appliquer ses corrections puis enregistrer.
- Un déplacement refusé n'est pas re-proposé dans la foulée.

## Étape 4 — Commit (optionnel)
Proposer — sans l'imposer — de commiter la mise à jour :
```bash
git add CLAUDE.md docs/ && git commit -m "Suivi : mise a jour increments et roadmap (cloture de session)"
```
Le push reste à la main de l'utilisateur.

## Bornes
- Une seule passe : pas de boucle. Si le `chef_projet` manque
  d'information, il le signale, il n'invente pas d'avancement.
- Aucune modification du CLAUDE.md hors des sections de suivi
  (incrément en cours, journal des décisions) — à l'exception des
  déplacements vers `docs/` validés à l'étape 2 bis, qui **déplacent**
  du contenu sans le réécrire ni le résumer.
- Pas d'action irréversible sans confirmation (CHARTE §4).
