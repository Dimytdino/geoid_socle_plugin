<!-- ════════════════════════════════════════════════════════════════
     CLAUDE.md — dépôt du socle GéoID (développement + marketplace)
     Ce n'est PAS un projet cadré : ne pas lancer /cadrer-projet ici.
     Depuis la 1.0.0 (ADR-003), ce dépôt n'est plus le template de projet.
     ════════════════════════════════════════════════════════════════ -->

# Socle GéoID — dépôt de développement

Ce dépôt **est le socle** du pôle GéoID (TSE) : il développe les plugins
`geoid` (équipes) et `geoid-meta` (mainteneur), publiés via la **marketplace**
`geoid-socle`, et il tient à jour le contenu « résiduel » repris par le
template de projet.

Règles applicables aux sessions dans ce dépôt :
1. **Lire `CHARTE.md`** — les règles transverses du pôle s'appliquent ici
   comme partout (confidentialité foncière, validation des actions
   irréversibles, revue avant livraison, réutiliser avant de créer).
2. **`DEMARRER.md`** décrit comment travailler sur le socle (clone, tests,
   versionnage) et comment créer un projet.
3. **Avant tout push significatif** : lancer les tests d'intégrité
   (`python3 tests/test_socle_integrity.py` et les autres suites `tests/`)
   et, si pertinent, `geoid-meta:revue-socle`.
4. **Versionnage — alignement strict (ADR-001c)** : `SOCLE_VERSION` = version
   de la marketplace = version de chaque `plugin.json`. Le test d'intégrité
   le vérifie.
5. **Suivi** : `docs/suivi-projet.md` (roadmap, risques, journal des
   décisions) ; ADR dans `docs/adr/`.

**Créer un projet GéoID** ne se fait pas ici : partir du dépôt dédié
**`geoid_agents_template`** (« Use this template »). Le plugin `geoid` s'y
installe automatiquement et apporte les agents (`architecte`, `developpeur`,
`analyste_sig`, `revieweur`, `documentaliste`, `chef_projet`, `mentor`), les
skills et les commandes `geoid:` du pôle. Les agents skill-builder
(`interviewer_skill`, `redacteur_skill`, `critique_skill`) vivent dans
`geoid-meta`, réservé au mainteneur du socle.
