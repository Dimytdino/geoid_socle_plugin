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

**0.5.1** (S-07, périmètre MCP au cadrage — ADR-001d) publiée le 2026-07-21 :
PR #4 mergée (`ff0b9e0`), tag `0.5.1` + pré-release canal `latest` (étape MCP
dans `geoid:cadrer-projet`, gabarit `.mcp.json`, consigne de sécurité au
template). Itération de contenu, noms gelés — `stable` reste à 0.5.0.
Tests d'intégrité verts (10 blocs).

**0.5.2** (S-10, régénération du skill dérivé `conventions-sig-tse` 1.1 → 1.2)
préparée le 2026-07-29 : renvois « (à venir) » retirés, sync CHARTE §3-§4
revérifiée. Bump de contenu (alignement strict ADR-001c). **À publier par le
mainteneur** : tag `0.5.2` + pré-release `latest`, et re-packaging/republication
du `.skill` sur claude.ai. Noms gelés — `stable` reste à 0.5.0.

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
| S-09 | Migrer les projets existants vers le mode plugin | Haute | mainteneur / équipes | Sans objet (2026-07-21) — aucun projet aval à migrer (table rase confirmée, cf. ADR-001a). Outillage conservé (checklist CHANGELOG 0.5.0 + `scripts/verifier_migration_plugin.py`) au cas où un ancien clone referait surface | — |
| S-10 | Re-packager et faire republier `conventions-sig-tse.skill` dans claude.ai (master/dérivé) | Moyenne | mainteneur | Prêt (2026-07-29) — sync CHARTE §3-§4 revérifiée (à jour) ; skill régénéré 1.1 → 1.2 (renvois « (à venir) » périmés retirés) ; `.skill` re-packagé via `scripts/packager_skill.py` (artefact local, non versionné) ; bump socle 0.5.2 (contenu plugin). **Reste l'action mainteneur/admin** : pousser tag `0.5.2` + pré-release `latest`, et faire publier le `.skill` sur claude.ai par l'admin de l'organisation | — |
| S-11 | Activer le sandbox OS (`settings.json`, bubblewrap) après test sur un poste WSL2 | Moyenne | mainteneur | Bloqué (2026-07-21) — `bubblewrap` non installable sur le poste courant (droits admin/sudo indisponibles). Squelette prêt dans `settings.json` ; reste `apt install bubblewrap` + test du confinement + `enabled:true`, sur un poste avec droits admin (ou via l'IT). Ne PAS passer `enabled:true` sans bwrap (`failIfUnavailable:false` → sandbox silencieusement inopérant) | — |
| S-12 | Arbitrer le statut des skills brouillons dans `plugins/geoid/skills/` (actifs dès que le plugin est installé/rechargé — à confirmer) | Basse | mainteneur | Terminé (2026-07-29) — prémisse **confirmée** (doc Claude Code : skills de plugin tous actifs à l'install, aucune désactivation par skill ; `skillOverrides` ne s'applique pas aux skills de plugin). Arbitrage **Option A** : on assume l'état actif — les deux 0.1 reclassés « actif — complétion en cours » (contenu jugé sûr, manques explicitement étiquetés « à compléter/à confirmer »), règle posée dans le registre. Complétions restant côté experts : nommage/emplacement/staging/journalisation FME (Kilian), infos d'environnement ArcGIS (Fateh) — suivies au registre, hors S-12 | 2026-07-29 |
| S-13 | Construire les évaluations de déclenchement des skills (jeux de prompts déclencheurs / non-déclencheurs) | Basse | mainteneur | Terminé (2026-07-28) — harnais `evals/` : un jeu par skill publié (`<nom>.eval.json`, déclencheurs + non-déclencheurs frontière/hors-périmètre), validateur `scripts/evaluer_declenchement.py` (structure + couverture, mode `--rapport` pour le test manuel), test CI `tests/test_evaluer_declenchement.py` (5ᵉ test), protocole `evals/README.md`. Outillage mainteneur (hors plugin) → pas de bump de version. Reste à jouer le test de déclenchement RÉEL en conversation (grille `evals/README.md`) | 2026-07-28 |
| S-14 | Supprimer la branche `charte-0.3.1-src-format-echange` (intégrée à main) | Basse | mainteneur | Terminé (2026-07-21) — la branche visée n'existait plus (historique recréé) ; nettoyage de la branche résiduelle mergée `bascule-plugins-0.5.0` (distant + local) et purge des refs de suivi. Seul `main` subsiste | 2026-07-21 |

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R-01 | Dérive de version du socle entre projets pendant le statu quo (diffusion par merge) | Élevée | Moyen | Bascule immédiate faite (0.5.0) ET aucun projet aval en régime « merge » (table rase confirmée 2026-07-21) : plus de population exposée. Diffusion désormais par marketplace | Fermé (2026-07-21) |
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
| 2026-07-21 | Migration des projets existants (S-09) | **Sans objet** : aucun projet aval à migrer (table rase confirmée par D. Grohan). S-09 clôturée ; outillage (checklist + `verifier_migration_plugin.py`) conservé pour un éventuel clone résiduel | Cohérent avec la prémisse de l'ADR-001a (bascule immédiate justifiée par l'absence de projets aval). Ferme R-01 |
| 2026-07-21 | Périmètre MCP au cadrage (ADR-001d) | Cadrage propose (utilisateur valide) : **PostGIS RO** (`crystaldba/postgres-mcp` restricted, rôle BD dédié) en étude/analyse ; **FME Flow MCP** conditionné à **FME ≥ 2026.2** (pôle en 2025.2 → non proposé pour l'instant) en pipeline ; **Esri** hors périmètre (bêta, veille S-08, critères de sortie définis). Sécurité : RO + `${VAR}`, jamais de secret en clair. Livré en 0.5.1 (étape MCP `cadrer-projet`, gabarit `.mcp.json`, consigne template) | Faits vérifiés (serveur PG de référence archivé/vulnérable → écarté ; FME Flow MCP GA mais requiert 2026.2 ; Esri en bêta sans GA). Dernier point ADR-001 clos. Détail : ADR-001 §8 |
| 2026-07-29 | Statut des skills brouillons de plugin (S-12) | **Option A — assumer l'état actif.** Prémisse confirmée (doc Claude Code) : les skills embarqués par un plugin sont tous découverts/actifs dès l'install, sans activation ni désactivation par skill ; `skillOverrides` ne vise pas les skills de plugin ; pas de champ `draft`. Décision : ne PAS geler (option B, `disable-model-invocation`, écartée — annulerait la valeur auto-applicable et rendrait les évals S-13 sans objet) ni sortir du plugin (option C, écartée — ferait perdre `environnement-arcgis-tse` qui est complet et revu). Les deux 0.1 sont **reclassés « actif — complétion en cours »** dans le registre ; règle posée : *seul un contenu qu'on assume de voir auto-appliqué vit dans `plugins/geoid/skills/`*. | Lecture des deux SKILL.md : contenu sûr, manques regroupés et explicitement étiquetés « à compléter/à confirmer » (donc jamais présentés comme faits) et périphériques ; `environnement-arcgis-tse` déjà revu (critique APPROUVÉ). Aucune capacité native de gel sélectif (option B non fiable sans test). Cohérent avec le tout-ou-rien plugin acté à l'ADR-001 |

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
