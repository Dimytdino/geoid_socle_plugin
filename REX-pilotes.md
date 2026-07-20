# REX des pilotes — geoid-socle

Grille **commune et identique** aux trois premiers pilotes, pour pouvoir
les comparer. Objectif : juger le socle à son impact réel, pas à sa
qualité théorique. À remplir au fil de l'eau et à consolider en fin de
pilote.

Mainteneur du socle : à désigner. Sponsor : directeur du pôle.

---

## 1. Les 5 indicateurs communs

| # | Indicateur | Comment le mesurer | Cible indicative |
|---|------------|--------------------|------------------|
| 1 | **Gain de temps** | Temps réel pour produire le livrable vs estimation « à la main » | Mieux qu'à la main |
| 2 | **Qualité** | Nombre de corrections relevées en revue avant validation | Décroissant d'un livrable au suivant |
| 3 | **Autonomie** | Nombre d'interventions du directeur / mainteneur pour débloquer | Le plus bas possible |
| 4 | **Capitalisation** | Nombre de pièges / règles à transformer en skill | ≥ 1 par pilote |
| 5 | **Ressenti** | Note de l'utilisateur en fin de pilote, en une phrase | utile / trop lourd / à améliorer |

Règle d'or de cette phase : **on observe avant d'enrichir le socle.**
Tout retour terrain ne devient pas une règle transverse — le filtre reste
celui de la création de skill (spécifique, récurrent, partagé, stable).

---

## 2. Validation des agents (à remplir une fois par pilote)

Au-delà des chiffres, juger si chaque agent a apporté une valeur réelle
ou seulement de la lourdeur. Un agent peut être excellent sur le papier
et inutile sur un type de projet — l'objectif est de savoir lesquels
rendre optionnels.

| Agent | A-t-il apporté une vraie valeur ? | Garder / rendre optionnel ? |
|-------|-----------------------------------|------------------------------|
| architecte | | |
| developpeur (variante) | | |
| revieweur | | |
| documentaliste | | |
| chef_projet | | |
| mentor | | |

---

## 3. REX de session (format court, à chaque séance marquante)

```
## REX session — [date] — [projet]
- Ce qui a été utile :
- Ce qui a été trop lourd :
- Ce qui a manqué au socle :
- Ce qui doit devenir un skill :
- Ce qui doit rester propre au projet :
- Décision / action :
```

================================================================

## PILOTE 1 — Kilian · documentation-fme
**Famille** : pipeline de données · **Agents** : architecte,
developpeur_etl, revieweur, documentaliste, mentor.

**Définition du succès (à valider avant de commencer)**
Le pilote est réussi si au moins 3 workflows FME existants sont
documentés avec une fiche standard, relus par Kilian, compréhensibles
par un autre membre du pôle, et si le temps ou la qualité de
documentation est nettement meilleur qu'avant.

| Indicateur | Mesure relevée |
|------------|----------------|
| 1 · Gain de temps | |
| 2 · Qualité (corrections en revue) | |
| 3 · Autonomie (interventions) | |
| 4 · Capitalisation (→ skill fme-tse ?) | |
| 5 · Ressenti | |

Point de vigilance spécifique : règle 0 — lire un vrai `.fmw` avant de
coder le parsing (structure XML propre à FME 2025.2).

================================================================

## PILOTE 2 — Fateh · widget Experience Builder (export GeoJSON)
**Famille** : développement applicatif · **Agents** : architecte,
developpeur_front_carto (+ developpeur_back_geo pour l'export),
revieweur, documentaliste, mentor.

**Définition du succès (à valider avant de commencer)**
Le widget exporte une couche en GeoJSON valide, conforme aux conventions
TSE, testé sur au moins un cas réel, et le code est compris et
maintenable par Fateh.

| Indicateur | Mesure relevée |
|------------|----------------|
| 1 · Gain de temps | |
| 2 · Qualité (corrections en revue) | |
| 3 · Autonomie (interventions) | |
| 4 · Capitalisation (→ skill environnement-arcgis-tse ?) | |
| 5 · Ressenti | |

Point de vigilance spécifique : le GeoJSON est spécifié en WGS84
(EPSG:4326) — l'export doit reprojeter depuis 2154. Vérifier la
compatibilité avec ExB Developer Edition 1.17 (pas d'API postérieure).

================================================================

## PILOTE 3 — Rim · projet Orion (POC open source web SIG)
**Famille** : développement applicatif · **Agents** : architecte,
developpeur_back_geo, developpeur_front_carto, revieweur,
documentaliste, chef_projet, mentor.

**Définition du succès (à valider avant de commencer)**
Le POC démontre la faisabilité d'une fonction web SIG cible sur une stack
open source choisie, avec une décision documentée (garder / abandonner /
itérer) à la fin.

| Indicateur | Mesure relevée |
|------------|----------------|
| 1 · Gain de temps | |
| 2 · Qualité (corrections en revue) | |
| 3 · Autonomie (interventions) | |
| 4 · Capitalisation (→ skill ?) | |
| 5 · Ressenti | |

Points de vigilance spécifiques : c'est le pilote le plus ouvert (un POC
explore) et Rim n'est pas développeuse à temps plein — surveiller qu'il
ne devienne pas le cas atypique qui fausse la comparaison. Beaucoup d'ADR
attendus (choix de stack) : les faire trancher tôt par l'architecte.

================================================================

## SYNTHÈSE TRANSVERSE (à remplir en fin des 3 pilotes)

- Tendance des 5 indicateurs sur les trois projets :
- Agents à rendre optionnels / à conserver partout :
- Skills à créer en priorité (issus de la capitalisation) :
- Irritants du socle corrigés / à corriger :
- **Décision go / no-go phase 2** (extension aux chargés d'identification) :

### Grille go / no-go phase 2
- [ ] Au moins 1 pilote terminé de bout en bout
- [ ] REX documenté pour les 3
- [ ] Au moins 3 irritants du socle corrigés
- [ ] Mainteneur officiellement nommé (+ backup)
- [ ] Données sensibles et règles d'usage clarifiées
- [ ] Support utilisateur simple rédigé pour le métier
- [ ] Skill `identification-fonciere-tse` cadré avec exemples réels
