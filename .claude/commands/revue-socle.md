---
description: >
  Passer le socle geoid-socle lui-même en revue critique avant un push
  significatif (nouvel agent, nouvelle commande, amendement de la CHARTE,
  évolution des permissions). Mobilise le revieweur avec une grille
  spécifique au socle. À lancer depuis le dépôt geoid-socle.
---

# Revue du socle — /revue-socle

Le socle encadre les projets ; il doit respecter sa propre exigence.
Cette commande se lance avant tout push significatif : nouvel agent,
nouvelle commande, amendement de la CHARTE, modification des permissions.

Déléguer au `revieweur` avec la grille ci-dessous, en complément de sa
grille socle habituelle.

## Grille spécifique au socle

### Cohérence interne
- [ ] Aucune contradiction entre la CHARTE et les agents, commandes ou
      templates (chercher en particulier les durcissements : un fichier
      qui transforme « pour les demandes non triviales » en
      « systématiquement », ou « livrable de production » en « tout
      livrable »).
- [ ] Principe « une connaissance, un étage » respecté : pas de règle
      dupliquée entre CHARTE, skills, agents et templates. Toute
      duplication assumée est déclarée master/dérivé des deux côtés.
- [ ] Tout nouvel agent lit `CHARTE.md` au démarrage, comme les autres.
- [ ] Les listes d'agents par famille (commande /cadrer-projet) sont à
      jour si un agent a été ajouté, renommé ou supprimé.

### Portabilité
- [ ] Aucun chemin propre à un environnement particulier (`/mnt/...`,
      chemin de poste personnel, montage spécifique) : tout chemin
      référencé existe dans le dépôt ou est documenté comme prérequis.
- [ ] Les scripts embarqués n'ont pas de dépendance non documentée
      (stdlib uniquement, ou prérequis listés dans le README).

### Orchestration proportionnée
- [ ] Pas de délégation imposée pour les tâches triviales.
- [ ] Les exigences de revue ont un seuil de matérialité (livrables
      finaux/de production, pas les intermédiaires).
- [ ] Les boucles d'itération entre agents sont bornées (nombre maximal
      de passes avant escalade humaine).

### Sécurité et permissions
- [ ] `settings.json` valide (JSON) et cohérent : pas d'opération
      réseau ou d'installation en `allow` si des équivalentes sont en
      `ask` ; le destructif reste en `deny`.
- [ ] Le README assume les limites des garde-fous (signal, pas
      protection étanche).
- [ ] Aucun secret, aucune donnée foncière dans les exemples des
      fichiers du socle.

### Hygiène
- [ ] Pas de fichier généré commité (`__pycache__`, artefacts de build) ;
      `.gitignore` à jour.
- [ ] Tout script non trivial a un test dans `tests/`, et les tests
      passent (`python3 tests/test_*.py`).
- [ ] Le README reflète l'arborescence réelle du dépôt.

## Verdict et suite

Format de retour : celui du `revieweur` (✅ / ⚠️ bloquants / 💡 /
verdict). Un verdict REFUSÉ ou SOUS RÉSERVE bloque le push : corriger,
relancer la revue, puis pousser. Reporter au journal du dépôt (section
dédiée du README ou CHANGELOG) la date de revue et le verdict.
