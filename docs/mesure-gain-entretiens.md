<!-- ════════════════════════════════════════════════════════════════
     docs/mesure-gain-entretiens.md — kit d'entretien de mesure (S-03)
     Prépare l'action #2 de l'audit du 2026-07-30 : instrumenter le gain
     réel du socle à partir des deux pilotes aboutis (FME, ArcGIS).
     À remplir en entretien (1 h/personne), puis reporter les chiffres
     dans REX-pilotes.md (grille des 5 indicateurs).
     ════════════════════════════════════════════════════════════════ -->

# Kit d'entretien — mesure du gain réel du socle

**Pourquoi maintenant.** L'audit (30/07/2026) conclut « continuer », mais
souligne que le **gain n'est pas mesuré** alors que deux pilotes ont abouti.
L'information n'est plus dans le code : **elle est dans la mémoire de Kilian
et de Fateh, et elle se dégrade** (5-6 semaines déjà écoulées). Deux
entretiens d'une heure suffisent à transformer une conviction en dossier.

**Seuil de rentabilité (référence audit).** Entretien ~25 j/an, ~20 projets/an
→ le socle est rentable dès **~1,25 jour économisé par projet**. C'est le
chiffre à confronter aux réponses ci-dessous.

**Mode d'emploi.** 1 entretien par pilote (~1 h). Remplir les champs `……`,
puis reporter dans `REX-pilotes.md` (tableau du pilote + synthèse). Ne pas
chercher la précision comptable : un ordre de grandeur assumé vaut mieux
qu'une case vide.

**Les 3 questions (identiques pour tous)**
1. **Temps** — Combien de temps as-tu réellement passé pour produire le
   livrable ? Combien aurais-tu estimé **sans** le dispositif (à la main) ?
2. **Qualité** — Combien de corrections sont sorties de la relecture
   (revieweur / toi) avant validation ?
3. **Ressenti** — En une phrase : utile / trop lourd / à améliorer ?

---

## Entretien 1 — Kilian · pilote `documentation-fme`

**Livrable constaté (audit)** : ~720 lignes de documentation générées depuis
un vrai `.fmw`, avec rendu HTML et schéma. Pilote **abouti**.

| # | Indicateur | Réponse à recueillir | Valeur |
|---|-----------|----------------------|--------|
| 1 | Gain de temps | temps réel : `……`  ·  estimé sans dispositif : `……`  → **économie : `……`** | |
| 2 | Qualité | nombre de corrections en revue : `……` | |
| 3 | Autonomie | nombre d'interventions mainteneur/directeur pour débloquer : `……` | |
| 4 | Capitalisation | pièges/règles → skill : `fme-tse` **déjà créé** ✓ ; autres à extraire : `……` | |
| 5 | Ressenti | (utile / trop lourd / à améliorer) : `……` | |

Note libre (verbatim marquant, irritant, manque) : `……`

---

## Entretien 2 — Fateh · pilote widget Experience Builder (export GeoJSON)

**Livrable constaté (audit)** : widget ExB d'export GeoJSON, ~327 lignes de
code. Pilote **abouti**. Repère audit : le projet a représenté ~9 jours de
travail → il suffit d'**1 jour économisé (11 %)** pour dépasser le seuil.

| # | Indicateur | Réponse à recueillir | Valeur |
|---|-----------|----------------------|--------|
| 1 | Gain de temps | temps réel : `……`  ·  estimé sans dispositif : `……`  → **économie : `……`** | |
| 2 | Qualité | nombre de corrections en revue : `……` | |
| 3 | Autonomie | nombre d'interventions mainteneur/directeur pour débloquer : `……` | |
| 4 | Capitalisation | pièges/règles → skill : `environnement-arcgis-tse` **déjà créé** ✓ ; autres : `……` | |
| 5 | Ressenti | (utile / trop lourd / à améliorer) : `……` | |

Note libre : `……`

---

## Entretien 3 (optionnel, allégé) — Rim · projet `Orion`

Pilote **le moins avancé** (dépôt avec un seul « Initial commit ») —
anticipé (POC ouvert, ressource à temps partiel). À ne mener que si utile ;
ne doit **pas** fausser la comparaison (cas atypique, cf. `REX-pilotes.md`).

| # | Indicateur | Valeur |
|---|-----------|--------|
| 1 | Gain de temps | `……` |
| 2 | Qualité | `……` |
| 5 | Ressenti | `……` |

---

## Synthèse — le chiffre qui tranche le dossier

À remplir une fois les entretiens faits :

- Économie moyenne constatée par projet : **`……` jour(s)**
- Seuil de rentabilité : **1,25 jour / projet**
- **Verdict** : `……`  (≥ seuil → dossier clos favorablement ; < seuil → analyser pourquoi)

> Reporter ensuite les valeurs dans `REX-pilotes.md` (tableaux par pilote +
> section « SYNTHÈSE TRANSVERSE »), qui reste la grille de référence (S-03).
> Point de rendez-vous audit : **revue à 30 jours** — l'indicateur « gain de
> temps » doit être écrit, et le mainteneur + suppléant nommés.
