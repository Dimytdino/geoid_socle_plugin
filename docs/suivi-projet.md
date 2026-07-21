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

Version courante du socle (publiée) : **0.5.0** (bascule en plugins — PR #1
mergée sur `main` en `a4df160` le 2026-07-21, tag `0.5.0` poussé, pré-release
canal `latest`, tag `stable` coupé après verrouillage des noms).
Marketplace `geoid-socle` → plugins `geoid` / `geoid-meta`.

**0.5.1 en préparation** (S-07, périmètre MCP au cadrage — ADR-001d) : étape
MCP dans `geoid:cadrer-projet`, gabarit `.mcp.json`, consigne de sécurité au
template. Itération de contenu sur le canal `latest` (noms gelés). Reste :
revue socle + commit/PR + tag `0.5.1`. Tests d'intégrité verts (10 blocs).

## 1. Roadmap / backlog

| ID | Tâche | Priorité | Responsable / agent | Statut | Échéance |
|----|-------|----------|---------------------|--------|----------|
| S-01 | Commit, merge et push de la 0.4.0 (durcissement post-audit) | Haute | mainteneur | Terminé | 2026-07-03 |
| S-02 | Instruction de l'ADR-001 (transposition en plugins) | Haute | architecte | Terminé | 2026-07-03 |
| S-03 | Réception et consolidation des REX pilotes (grille `REX-pilotes.md`, 3 pilotes) | Haute | équipe pilotes / mainteneur | En cours | prochaine échéance |
| S-04 | Trancher ADR-001a : critères et calendrier de bascule | Haute | architecte + D. Grohan | Terminé (bascule immédiate, ADR-001 §6) | 2026-07-20 |
| S-05 | Publication marketplace + plugins `geoid`/`geoid-meta`, tag 0.5.0, réécriture `/cadrer-projet`, checklist de migration | Haute | mainteneur / developpeur | Terminé (2026-07-21) — PR #1 mergée, tag `0.5.0` + pré-release `latest`, noms verrouillés, tag `stable` coupé (ADR-001 §7) | 2026-07-21 |
| S-06 | Trancher ADR-001c : politique de version | Moyenne | architecte + D. Grohan | Terminé (alignement strict, ADR-001 §6) — mise en œuvre (bloc test d'intégrité, mentions de version CLAUDE.md) portée par S-05 | 2026-07-20 |
| S-07 | Trancher ADR-001d : périmètre MCP au cadrage (PostGIS RO — étude/analyse ; FME Flow MCP conditionné à FME 2026.2 — pipeline ; puis étape MCP dans `/cadrer-projet`, gabarit `.mcp.json`, consigne « identifiants RO, jamais en clair ») | Moyenne | architecte + D. Grohan | Terminé (2026-07-21) — ADR-001d tranché (ADR-001 §8) ; étape MCP + gabarit + consigne livrés en 0.5.1 | 2026-07-21 |
| S-08 | Veille ArcGIS Location Services MCP (bêta Esri du 2026-06-29) : critères de sortie de veille | Basse | mainteneur | En cours | — |
| S-09 | Migrer les projets existants vers le mode plugin (checklist CHANGELOG 0.5.0 : install marketplace, suppression des doublons `.claude/` locaux, en-tête de version, relance) — outil `scripts/verifier_migration_plugin.py` fourni. La propagation par merge (0.4.0) est supersédée sauf pour le template résiduel (CHARTE, settings, spécialisations) | Haute | mainteneur / équipes | À faire — outil de vérification livré (2026-07-21) ; migration par projet à mener | — |
| S-10 | Re-packager et faire republier `conventions-sig-tse.skill` dans claude.ai (master/dérivé) | Moyenne | mainteneur | À faire | — |
| S-11 | Activer le sandbox OS (`settings.json`, bubblewrap) après test sur un poste WSL2 | Moyenne | mainteneur | À faire | — |
| S-12 | Arbitrer le statut des skills brouillons dans `plugins/geoid/skills/` (actifs dès que le plugin est installé/rechargé — à confirmer) | Basse | mainteneur | À faire | — |
| S-13 | Construire les évaluations de déclenchement des skills (jeux de prompts déclencheurs / non-déclencheurs) | Basse | mainteneur | À faire | — |
| S-14 | Supprimer la branche `charte-0.3.1-src-format-echange` (intégrée à main) | Basse | mainteneur | À faire | — |

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R-01 | Dérive de version du socle entre projets pendant le statu quo (diffusion par merge) | Élevée | Moyen | Bascule immédiate actée (ADR-001a, cible 0.5.0) : referme le risque plus tôt. Fin de support option A visée après le cycle 0.6.0 | En voie de fermeture |
| R-02 | Gel de l'interface plugin (préfixes `geoid:`/`geoid-meta:`, découpage) avant stabilisation → renommage coûteux | Moyenne | Élevé | Verrouillage des noms mené et documenté (ADR-001 §7, 2026-07-21) ; tag `stable` coupé ; canal `latest` ouvert pour itérer le contenu en 0.5.x sans renommage ; noms majoritairement éprouvés depuis l'option A | Fermé (2026-07-21) |
| R-03 | REX pilotes tardifs ou incomplets → bascule repoussée sine die | Moyenne | Moyen | Bascule découplée des REX (ADR-001a) : les REX s'intègrent en 0.5.x par versions mineures. Risque levé | Fermé (2026-07-20) |
| R-04 | Post-bascule : désynchronisation des deux canaux de diffusion (marketplace vs template résiduel — CHARTE, settings, spécialisations) | Moyenne | Moyen | Extension du test d'intégrité (ADR-001c) ; signalement de décalage de versions par `/cloturer-session` (ADR-001 §4.1) | Ouvert |
| R-05 | MCP au cadrage : chaînes de connexion ou identifiants en clair dans le `.mcp.json` projet (violation CHARTE §4) | Faible | Élevé | ADR-001d tranché (§8) : gabarit `.mcp.json` sans secret + placeholders `${VAR}` + rôle BD read-only + consigne au template et dans le cadrage. Test d'intégrité (bloc 10) vérifie l'absence d'identifiant en dur dans le gabarit | En voie de fermeture (à surveiller à l'usage) |

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
| 2026-07-20 | Calendrier de bascule (ADR-001a) | **Bascule immédiate** (candidat 0.5.0) : publication marketplace + plugins sans attendre les REX ; canal `latest` puis tag `stable` après verrouillage des noms ; fin de support option A visée après 0.6.0 | Fait nouveau : table rase (pas de projets aval à protéger) → le motif dominant du séquencement tombe ; interface neuve minime (préfixes imposés) ; contenu corrigeable par versions mineures. Détail : ADR-001 §6 |
| 2026-07-20 | Politique de version (ADR-001c) | **Alignement strict** : `SOCLE_VERSION` = version `geoid` = version `geoid-meta` = tag marketplace ; bloc de cohérence ajouté à `test_socle_integrity.py` ; CLAUDE.md projet porte deux champs (plugin `geoid` / template résiduel) | Source de vérité unique (ADR-001 §4.1) ; garantie vérifiable par le test d'intégrité ; « bump à vide » d'un plugin accepté (mainteneur/release uniques). Détail : ADR-001 §6 |
| 2026-07-21 | Verrouillage des noms + coupe du tag `stable` (ADR-001a) | **Noms gelés** : marketplace `geoid-socle`, plugins `geoid`/`geoid-meta`, commandes préfixées, agents, skills, frontière de découpage (liste : ADR-001 §7). Tag `stable` coupé ; canal `latest` ouvert pour le contenu | Audit de cohérence sans écart ; noms majoritairement éprouvés en option A ; le gel porte sur les identifiants, pas sur le contenu (itérable en 0.5.x). Ferme R-02. Détail : ADR-001 §7 |
| 2026-07-21 | Périmètre MCP au cadrage (ADR-001d) | Cadrage propose (utilisateur valide) : **PostGIS RO** (`crystaldba/postgres-mcp` restricted, rôle BD dédié) en étude/analyse ; **FME Flow MCP** conditionné à **FME ≥ 2026.2** (pôle en 2025.2 → non proposé pour l'instant) en pipeline ; **Esri** hors périmètre (bêta, veille S-08, critères de sortie définis). Sécurité : RO + `${VAR}`, jamais de secret en clair. Livré en 0.5.1 (étape MCP `cadrer-projet`, gabarit `.mcp.json`, consigne template) | Faits vérifiés (serveur PG de référence archivé/vulnérable → écarté ; FME Flow MCP GA mais requiert 2026.2 ; Esri en bêta sans GA). Dernier point ADR-001 clos. Détail : ADR-001 §8 |

## 5. 🔧 À arbitrer (points ouverts)

Source de vérité : tableau §5 de
`docs/adr/ADR-001-transposition-plugins.md` (avec la colonne « Tâches
bloquées »). **Aucun point ADR-001 ouvert au 2026-07-21** : l'ADR-001 est
entièrement instruit.

Clos :
- **ADR-001** (option D), **ADR-001b** (spécialisations côté cadrage) — 2026-07-03.
- **ADR-001a** (bascule immédiate) → débloque S-04, S-05 ; **ADR-001c**
  (alignement strict des versions) → débloque S-06 — 2026-07-20 (ADR-001 §6).
- **ADR-001d** (périmètre MCP au cadrage) → débloque S-07 — 2026-07-21
  (ADR-001 §8).

Conformément à la CHARTE §5, le backlog avance sans point bloquant ADR.
