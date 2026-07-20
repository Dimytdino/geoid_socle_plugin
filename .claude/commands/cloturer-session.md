---
description: >
  Clôturer une session de travail : le chef de projet met à jour la
  roadmap / le backlog et les risques (docs/suivi-projet.md) et le
  journal des décisions (CLAUDE.md) à partir de ce qui a été produit
  pendant la session. À lancer volontairement en fin de séance, quand
  la session a fait avancer le projet.
---

# Clôturer la session — /cloturer-session

Tu fais le point de fin de séance et tu confies la mise à jour du suivi
au `chef_projet`. À ne lancer que si la session a produit quelque chose
qui mérite d'être tracé — sinon, répondre que rien ne justifie une mise
à jour et s'arrêter.

## Étape 1 — Synthèse de la session
Établis un résumé court et factuel de ce qui s'est passé dans la session :
- ce qui a été produit ou modifié (livrables, fichiers, décisions) ;
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
- dans **`docs/suivi-projet.md`** : la roadmap / le backlog (statuts
  À faire / En cours / En revue / Terminé / Bloqué, nouvelles tâches
  identifiées) et le registre des risques si un point bloquant est
  apparu ;
- dans le **CLAUDE.md** : le journal des décisions — toute décision actée
  pendant la session, au format
  `| AAAA-MM-JJ | sujet | décision | justification |`.

Il ne touche qu'à ces sections de suivi : il ne réécrit pas l'objectif,
la stack ou les conventions du projet. (Projet cadré avant le socle
0.4.0, sans `docs/suivi-projet.md` ? Le créer depuis
`templates/suivi-projet.template.md` en y déplaçant les sections
Roadmap / Risques / Suivi des revues du CLAUDE.md.)

## Étape 3 — Validation humaine
Présente à l'utilisateur un récapitulatif des modifications proposées
(suivi et journal) **avant de les enregistrer** : la roadmap est un
document de référence, l'humain valide ce qui y entre (cf. CHARTE —
l'humain décide).
- Si l'utilisateur valide : enregistrer les modifications.
- S'il amende : appliquer ses corrections puis enregistrer.

## Étape 4 — Commit (optionnel)
Proposer — sans l'imposer — de commiter la mise à jour :
```bash
git add CLAUDE.md docs/suivi-projet.md && git commit -m "Suivi : mise a jour roadmap (cloture de session)"
```
Le push reste à la main de l'utilisateur.

## Bornes
- Une seule passe : pas de boucle. Si le `chef_projet` manque
  d'information, il le signale, il n'invente pas d'avancement.
- Aucune modification hors des sections de suivi du CLAUDE.md.
- Pas d'action irréversible sans confirmation (CHARTE §4).
