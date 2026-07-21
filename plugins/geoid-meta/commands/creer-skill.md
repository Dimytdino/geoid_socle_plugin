---
description: >
  Créer un nouveau skill GéoID de façon structurée : interview de
  l'expert, rédaction du SKILL.md, critique et validation. Orchestre
  les agents interviewer_skill, redacteur_skill et critique_skill en
  séquence. Produit un SKILL.md prêt pour relecture humaine et
  packaging.
---

# Créer un skill GéoID — geoid-meta:creer-skill

Tu orchestres la création d'un skill en trois étapes séquentielles.
Tu ne fais pas le travail des agents : tu délègues, tu transmets les
artefacts d'une étape à l'autre, et tu décides si on avance ou si on
itère.

## Avant de commencer
Cette commande s'exécute dans le dépôt du socle (`geoid-socle`) : les
skills sont des actifs du pôle, ils se créent et se versionnent ici,
dans `plugins/geoid/skills/` (ils sont embarqués par le plugin `geoid`
publié par la marketplace) — pas dans les dépôts projet. Pour tester un
skill fraîchement créé, réinstaller/recharger le plugin `geoid` (les
composants d'un plugin ne sont chargés qu'au démarrage).

Les trois agents skill-builder (`interviewer_skill`, `redacteur_skill`,
`critique_skill`) font partie des agents permanents du socle — aucune
activation à faire (les agents copiés sur disque en cours de session ne
seraient de toute façon chargés qu'au redémarrage).

Lire la CHARTE et le registre des skills
(`skills-geoid-registre-et-methode.md`, à la racine du dépôt ; s'il est
absent, demander à l'utilisateur quel skill il veut créer). Vérifier dans
`plugins/geoid/skills/` qu'aucun skill existant ne couvre déjà ce périmètre.

## Étape 1 — Interview (agent : interviewer_skill)

Déléguer à `interviewer_skill` :
```
Utilise le sous-agent interviewer_skill pour interviewer [prénom de
l'expert] sur le skill [nom]. Produis le fichier interview-brut.md
dans `plugins/geoid/skills/[nom-du-skill]/`.
```

Attendre la fin de l'interview et la production de `interview-brut.md`.
Relire le fichier : si une des 7 questions n'a pas de réponse exploitable,
demander à l'`interviewer_skill` de relancer l'expert sur ce point avant
de passer à l'étape 2.

## Étape 2 — Rédaction (agent : redacteur_skill)

Déléguer à `redacteur_skill` :
```
Utilise le sous-agent redacteur_skill pour rédiger le SKILL.md du skill
[nom] à partir du fichier plugins/geoid/skills/[nom-du-skill]/interview-brut.md.
Produis plugins/geoid/skills/[nom-du-skill]/SKILL.md.
```

Vérifier le résumé du rédacteur (nombre de lignes, déclencheurs, points
signalés). Si le rédacteur signale un manque d'information sur un point,
relancer l'`interviewer_skill` sur ce point spécifique avant de continuer.

## Étape 3 — Critique (agent : critique_skill)

Déléguer à `critique_skill` :
```
Utilise le sous-agent critique_skill pour valider le fichier
plugins/geoid/skills/[nom-du-skill]/SKILL.md en le comparant à plugins/geoid/skills/[nom-du-skill]/interview-brut.md.
```

Selon le verdict :
- **APPROUVÉ** → passer à l'étape 4.
- **APPROUVÉ SOUS RÉSERVE** → transmettre les points 🟡 au
  `redacteur_skill` pour correction, puis relancer la critique.
  Maximum 2 itérations ; au-delà, escalader à l'humain.
- **REFUSÉ** → transmettre les points 🔴. Si le problème vient d'un
  manque dans l'interview (règles insuffisantes, exemples absents),
  relancer l'`interviewer_skill` sur les points concernés, puis
  repasser par la rédaction.

## Étape 4 — Packaging et transmission à l'humain

```bash
python3 scripts/packager_skill.py plugins/geoid/skills/[nom-du-skill]/
```

Le fichier `.skill` produit est prêt pour installation par l'admin de
l'organisation Claude. Le dossier `plugins/geoid/skills/[nom-du-skill]/` (SKILL.md et
interview-brut.md) est commité dans le dépôt du socle : c'est la source
de vérité, le `.skill` n'en est que l'emballage.

## Étape 5 — Mise à jour du registre

Mettre à jour `skills-geoid-registre-et-methode.md` :
- déplacer le skill créé du registre « à créer » vers une section
  « Skills publiés » (nom, date, mainteneur, version) ;
- si l'interview a révélé un besoin de skill connexe (Q6 : « hors
  périmètre »), l'ajouter au vivier du registre.

Une connaissance, un étage : si le skill créé recouvre un contenu de la
CHARTE ou d'un autre skill, le signaler à l'utilisateur pour arbitrage
du mainteneur — ne pas laisser deux sources de vérité coexister.

## Compte rendu final

Produire un compte rendu selon la CHARTE §5 :
- Skill créé (nom, nombre de lignes, nombre de déclencheurs)
- Iterations (combien de passes rédaction/critique)
- Points signalés par la critique et comment ils ont été résolus
- Ce qui reste à faire par l'humain validateur :
  - Commiter `plugins/geoid/skills/[nom-du-skill]/` et le registre mis à jour dans le
    dépôt du socle
  - Relire le SKILL.md en 5 min (est-il fidèle à ce que l'expert sait ?)
  - Tester les 5 prompts suivants dans une conversation neuve avec le
    skill installé :
    [lister ici 5 prompts tirés de Q2 de l'interview]
  - Tester 1 prompt hors périmètre (le skill ne doit PAS se déclencher)
  - Valider ou demander une itération supplémentaire

## Nettoyage
Aucun : les agents skill-builder vivent dans le plugin `geoid-meta`,
installé par le seul mainteneur du socle. Ils sont absents des dépôts
**projet** par construction (`geoid-meta` n'y est pas installé) — plus
aucun retrait à faire au cadrage.
