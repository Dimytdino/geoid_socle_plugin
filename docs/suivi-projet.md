<!-- ════════════════════════════════════════════════════════════════
     docs/suivi-projet.md — geoid-socle (le socle lui-même)
     Suivi opérationnel du dépôt du socle : roadmap, risques, revues,
     journal des décisions. Volontairement HORS du CLAUDE.md : ce
     fichier grossit avec le projet et n'a pas à occuper le contexte
     de chaque session — les agents le lisent à la demande (clôture
     de session, reporting).
     Créé le 2026-07-03 via /cloturer-session (le socle n'étant pas un
     projet cadré, ce fichier n'est pas issu de /cadrer-projet).
     Famille : pilotage / transverse (CHARTE §1).
     ════════════════════════════════════════════════════════════════ -->

# Suivi du projet — geoid-socle

Tenu à jour par le `chef_projet` (ou l'orchestrateur s'il n'est pas
activé), notamment via `/cloturer-session`. L'humain valide ce qui
entre ici (cf. CHARTE §4 et §5).

Version courante du socle : **0.4.0** (commit `64a12c1`, mergé sur
`main` en `5e5a832`, poussé le 2026-07-03 — PR #1 et #2, tests
d'intégrité 5/5 verts).

## 1. Roadmap / backlog

| ID | Tâche | Priorité | Responsable / agent | Statut | Échéance |
|----|-------|----------|---------------------|--------|----------|
| S-01 | Commit, merge et push de la 0.4.0 (durcissement post-audit) | Haute | mainteneur | Terminé | 2026-07-03 |
| S-02 | Instruction de l'ADR-001 (transposition en plugins) | Haute | architecte | Terminé | 2026-07-03 |
| S-03 | Réception et consolidation des REX pilotes (grille `REX-pilotes.md`, 3 pilotes) | Haute | équipe pilotes / mainteneur | En cours | prochaine échéance |
| S-04 | Trancher ADR-001a : critères et calendrier de bascule (nombre de REX, critères de gel de l'interface, date butoir de migration) | Haute | architecte + D. Grohan | Bloqué (attend S-03) | après REX |
| S-05 | Publication marketplace + plugins `geoid`/`geoid-meta`, tag 0.5.0, réécriture `/cadrer-projet`, checklist de migration | Haute | mainteneur / developpeur | Bloqué (ADR-001a) | — |
| S-06 | Trancher ADR-001c : politique de version `SOCLE_VERSION` vs marketplace (puis extension de `test_socle_integrity.py`, mentions de version dans le CLAUDE.md projet) | Moyenne | architecte + D. Grohan | Bloqué (lié à la bascule) | avant premier tag marketplace |
| S-07 | Trancher ADR-001d : périmètre MCP au cadrage (PostGIS RO — étude/analyse ; FME Flow MCP conditionné à FME 2026.2 — pipeline ; puis étape MCP dans `/cadrer-projet`, gabarit `.mcp.json`, consigne « identifiants RO, jamais en clair ») | Moyenne | architecte + D. Grohan | À faire | — |
| S-08 | Veille ArcGIS Location Services MCP (bêta Esri du 2026-06-29) : critères de sortie de veille | Basse | mainteneur | En cours | — |
| S-09 | Propager la 0.4.0 aux projets existants (`git fetch socle && git merge socle/main` + migration du suivi, cf. CHANGELOG 0.4.0) | Haute | mainteneur / équipes | À faire | — |
| S-10 | Re-packager et faire republier `conventions-sig-tse.skill` dans claude.ai (master/dérivé) | Moyenne | mainteneur | À faire | — |
| S-11 | Activer le sandbox OS (`settings.json`, bubblewrap) après test sur un poste WSL2 | Moyenne | mainteneur | À faire | — |
| S-12 | Arbitrer le statut des skills brouillons dans `.claude/skills/` (actifs dès versionnés — à confirmer) | Basse | mainteneur | À faire | — |
| S-13 | Construire les évaluations de déclenchement des skills (jeux de prompts déclencheurs / non-déclencheurs) | Basse | mainteneur | À faire | — |
| S-14 | Supprimer la branche `charte-0.3.1-src-format-echange` (intégrée à main) | Basse | mainteneur | À faire | — |

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R-01 | Dérive de version du socle entre projets pendant le statu quo (diffusion par merge, option A maintenue jusqu'aux REX) | Élevée | Moyen | Bascule plugins actée (ADR-001, cible 0.5.0) ; en attendant, suivre la propagation 0.4.0 (S-09) | Ouvert |
| R-02 | Gel prématuré de l'interface plugin (noms préfixés de commandes/agents/skills) avant retours pilotes → renommage coûteux dans tous les projets | Moyenne | Élevé | Séquencement en deux temps acté par l'ADR-001 : publication seulement après intégration des REX ; critères de gel à fixer (ADR-001a) | Maîtrisé |
| R-03 | REX pilotes tardifs ou incomplets → bascule 0.5.0 repoussée sine die, prolongation du régime « merge » | Moyenne | Moyen | Grille REX commune déjà en place (`REX-pilotes.md`) ; relance des pilotes par le chef de projet | Ouvert |
| R-04 | Post-bascule : désynchronisation des deux canaux de diffusion (marketplace vs template résiduel — CHARTE, settings, spécialisations) | Moyenne | Moyen | Extension du test d'intégrité (ADR-001c) ; signalement de décalage de versions par `/cloturer-session` (ADR-001 §4.1) | Ouvert |
| R-05 | MCP au cadrage : chaînes de connexion ou identifiants en clair dans le `.mcp.json` projet (violation CHARTE §4) | Faible | Élevé | Cadrer dans ADR-001d : identifiants lecture seule + variables d'environnement, consigne explicite dans le template | Ouvert |

## 3. Suivi des revues

Les passages `/revue-socle` sont journalisés dans `CHANGELOG.md`,
section « Suivi des revues du socle » (source unique — non dupliquée
ici, règle 0). Dernier passage : **2026-07-02**, périmètre 0.4.0,
verdict **APPROUVÉ** (réserves levées).

## 4. Journal des décisions

> **Dérogation à la CHARTE §5 (emplacement)** : le journal des décisions
> vit normalement dans le `CLAUDE.md` du projet. Dans ce dépôt, le
> `CLAUDE.md` racine est le **bootstrap « non cadré »** recopié dans
> chaque projet créé depuis le template : y loger le journal du socle le
> ferait fuiter dans tous les projets. Il est donc tenu ici. Dérogation
> actée le 2026-07-03.

| Date | Sujet | Décision | Justification |
|------|-------|----------|---------------|
| 2026-07-03 | Diffusion du socle (ADR-001) | **Option D acceptée** : deux plugins — `geoid` (équipes) et `geoid-meta` (mainteneur) ; statu quo (option A) jusqu'aux REX pilotes, puis bascule (version candidate 0.5.0) | L'activation tout-ou-rien d'un plugin est incompatible avec l'élagage par famille du cadrage ; la séparation des publics supprime le retrait des skill-builder au cadrage. Détail : `docs/adr/ADR-001-transposition-plugins.md` |
| 2026-07-03 | Spécialisations du développeur (ADR-001b) | Maintien côté template + cadrage : `/cadrer-projet` continue de copier la seule spécialisation retenue | Le tout-ou-rien plugin ne sait pas activer une spécialisation par projet ; trois plugins par famille = coût disproportionné pour trois fichiers Markdown (tranché via l'option D) |
| 2026-07-03 | Référence de structuration plugin | **Superpowers** retenu comme référence pour la future transposition ; `caveman` et `career-ops` écartés | Analyse comparative de trois dépôts externes menée en session |
| 2026-07-03 | MCP dans le socle | Aucun MCP configuré dans le socle lui-même ; candidats proposés au cadrage projet (ADR-001d) : Postgres/PostGIS lecture seule (étude/analyse), FME Flow MCP conditionné au passage FME 2026.2 (pipeline), ArcGIS Location Services MCP en veille | Les chaînes de connexion sont propres à chaque projet ; le tout-ou-rien du plugin imposerait tous les MCP partout (ADR-001 §4.3) |

## 5. 🔧 À arbitrer (points ouverts)

Source de vérité : tableau §5 de
`docs/adr/ADR-001-transposition-plugins.md` (avec la colonne « Tâches
bloquées »). Ouverts au 2026-07-03 :

- **ADR-001a** — critères et calendrier de bascule (après REX pilotes) → bloque S-04/S-05.
- **ADR-001c** — politique de version `SOCLE_VERSION` vs marketplace → bloque S-06.
- **ADR-001d** — périmètre des propositions MCP au cadrage → bloque S-07.

Conformément à la CHARTE §5, seules les tâches listées ci-dessus sont
bloquées ; le reste du backlog avance.
