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
Tests d'intégrité verts (10 blocs **à cette date** — 15 aujourd'hui).

**1.0.0** (première version officiellement supportée — décision du 2026-07-30)
porte le contenu ex-0.5.2 (skill `conventions-sig-tse` 1.2) + le réalignement
du modèle de démarrage (ADR-003 : template `geoid_agents_template`). Motivée
par : socle validé à l'usage (audit 2026-07-30), template en place, mainteneur
nommé (D. Grohan). Alignement strict des versions à `1.0.0` (SOCLE_VERSION,
marketplace, deux `plugin.json`). **Publiée le 2026-07-30** : tag `1.0.0`
poussé + **release pleine** GitHub (non pré-release). Reste :
re-packaging/republication du `.skill` sur claude.ai (admin).

**1.1.0** (lot 1 des correctifs de l'audit externe du 2026-08-20 — S-19,
S-25 volet 1, S-32, S-33, S-34) : bump **mineur** aligné (SOCLE_VERSION,
marketplace, deux `plugin.json`), correctifs et ajouts sans rupture
d'interface. Étapes de release restant à jouer par le mainteneur : tag `1.1.0`
+ release, `sync_template.py --apply` sur un clone de `geoid_agents_template`
— avec **retrait manuel de `templates/style-doc-tse.css`** côté template (il a
quitté le résiduel pour le plugin ; le script signale « en trop » mais ne
supprime jamais) — puis `claude plugin update geoid@geoid-socle` et relance de
`claude` sur chaque poste.

## 1. Roadmap / backlog

> **Deux séries d'identifiants coexistent.** S-01 à S-16 sont nés ici ;
> S-17 à S-31 viennent de la roadmap de l'audit interne du 2026-07-30
> (`docs/audit-agentique-2026-07-30.md` §6), qui a raccordé sa numérotation
> à celle-ci. S-32 et suivants sont issus de l'audit externe du 2026-08-20.
> ⚠️ Le sujet « suppléant du mainteneur » porte **deux** IDs : S-16 (ici) et
> S-24 (audit du 30/07). C'est le même point, toujours ouvert.


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
| S-09 | Migrer les projets existants vers le mode plugin | Haute | mainteneur / équipes | Clôturé (2026-07-30) — **décision : les ~7 projets figés restent gelés** (pas de migration). ⚠️ Rectifie le constat du 2026-07-21 (« table rase ») : des projets figés existent bien (dont la veille MRAE et `nemelios`), établi par l'audit du 2026-07-30 ; ils ne recevront pas de correction, gel assumé. Outillage de migration conservé pour un éventuel besoin ponctuel | 2026-07-30 |
| S-10 | Re-packager et faire republier `conventions-sig-tse.skill` dans claude.ai (master/dérivé) | Moyenne | mainteneur | Prêt (2026-07-29) — sync CHARTE §3-§4 revérifiée (à jour) ; skill régénéré 1.1 → 1.2 (renvois « (à venir) » périmés retirés) ; `.skill` re-packagé via `scripts/packager_skill.py` (artefact local, non versionné) ; bump de contenu porté par la **1.0.0**. Tag `1.0.0` + release **poussés le 2026-07-30**. **Reste** : faire publier le `.skill` sur claude.ai par l'admin de l'organisation (canal distinct) | — |
| S-11 | Activer le sandbox OS (`settings.json`, bubblewrap) après test sur un poste WSL2 | Moyenne | mainteneur | Bloqué (2026-07-21) — `bubblewrap` non installable sur le poste courant (droits admin/sudo indisponibles). Squelette prêt dans `settings.json` ; reste `apt install bubblewrap` + test du confinement + `enabled:true`, sur un poste avec droits admin (ou via l'IT). Ne PAS passer `enabled:true` sans bwrap (`failIfUnavailable:false` → sandbox silencieusement inopérant) | — |
| S-12 | Arbitrer le statut des skills brouillons dans `plugins/geoid/skills/` (actifs dès que le plugin est installé/rechargé — à confirmer) | Basse | mainteneur | Terminé (2026-07-29) — prémisse **confirmée** (doc Claude Code : skills de plugin tous actifs à l'install, aucune désactivation par skill ; `skillOverrides` ne s'applique pas aux skills de plugin). Arbitrage **Option A** : on assume l'état actif — les deux 0.1 reclassés « actif — complétion en cours » (contenu jugé sûr, manques explicitement étiquetés « à compléter/à confirmer »), règle posée dans le registre. Complétions restant côté experts : nommage/emplacement/staging/journalisation FME (Kilian), infos d'environnement ArcGIS (Fateh) — suivies au registre, hors S-12 | 2026-07-29 |
| S-13 | Construire les évaluations de déclenchement des skills (jeux de prompts déclencheurs / non-déclencheurs) | Basse | mainteneur | Terminé (2026-07-28) — harnais `evals/` : un jeu par skill publié (`<nom>.eval.json`, déclencheurs + non-déclencheurs frontière/hors-périmètre), validateur `scripts/evaluer_declenchement.py` (structure + couverture, mode `--rapport` pour le test manuel), test CI `tests/test_evaluer_declenchement.py` (5ᵉ test), protocole `evals/README.md`. Outillage mainteneur (hors plugin) → pas de bump de version. Reste à jouer le test de déclenchement RÉEL en conversation (grille `evals/README.md`) | 2026-07-28 |
| S-15 | Mettre en œuvre le template projet dédié (ADR-003, option B) : créer le dépôt `geoid_agents_template` (org, privé, *template*) ; y placer le résiduel + `.claude/settings.json` avec `extraKnownMarketplaces`/`enabledPlugins` (`autoUpdate`) ; définir la synchro socle → template ; mettre à jour DEMARRER/README/bootstrap (l'install `/plugin` manuelle quitte le chemin nominal) ; retirer au dépôt socle son rôle de template | Haute | mainteneur / architecte | Terminé (2026-07-30) — **dépôt `geoid_agents_template` créé** (org, privé, marqué *template*, branche `main`) et **contenu poussé** (résiduel + `.claude/settings.json` orienté projet avec plugin déclaré + `autoUpdate`). Docs du socle réalignées (DEMARRER — PR #14 ; README + `CLAUDE.md` bootstrap au passage 1.0.0). Synchro socle → template **tranchée (option 2) et livrée** : `scripts/sync_template.py` (`--check`/`--apply`, unidirectionnel), test `tests/test_sync_template.py` (6ᵉ test CI), procédure dans `DEMARRER.md`. `--check` sur le clone réel : template à jour. **Terminé** — la synchro devient une étape de release (manuelle) | 2026-07-30 |
| S-16 | Désigner un **suppléant** au mainteneur du socle (backup) | Haute | Direction / D. Grohan | À faire (2026-07-30) — mainteneur nommé (D. Grohan, S-15/journal) ; l'audit demande un binôme pour lever la dépendance à une seule personne (critère « moins de dépendance »). Point le plus urgent selon l'audit, coût ≈ une décision écrite. **Confirmé sans suppléant au 2026-07-30** — dépendance à une seule personne assumée en l'état ; à revoir à la revue 30 j | — |
| S-14 | Supprimer la branche `charte-0.3.1-src-format-echange` (intégrée à main) | Basse | mainteneur | Terminé (2026-07-21) — la branche visée n'existait plus (historique recréé) ; nettoyage de la branche résiduelle mergée `bascule-plugins-0.5.0` (distant + local) et purge des refs de suivi. Seul `main` subsiste | 2026-07-21 |
| S-17 | Jouer les 2 entretiens de mesure du gain (kit `docs/mesure-gain-entretiens.md`), dans l'unité de la thèse de chaque pilote | Haute | mainteneur + pilotes | À faire — **seule action périssable** du plan post-audit externe : la matière est dans la mémoire de Kilian et de Fateh et se dégrade (ouverte depuis le 2026-07-30) | — |
| S-19 | Rendre `fme-tse` exécutable côté projet | Haute | mainteneur | Terminé (2026-08-20) — option **ADR-001 §2 appliquée** (celle retenue et jamais mise en œuvre) : `generer_doc_html.py` + sa charte CSS déplacés dans `plugins/geoid/scripts/`, cités par `${CLAUDE_PLUGIN_ROOT}` dans le skill ; script rendu autoportant (CSS résolu à côté de lui) ; renvoi au dépôt pilote `documentation-fme/` retiré. Verrouillé par le bloc 15 | 2026-08-20 |
| S-25 | Modèle explicite par agent + `allowed-tools:` sur les commandes | Haute | mainteneur | **Partiellement terminé (2026-08-20)** — volet `model:` livré sur les **13** agents (7 `geoid`, 3 `geoid-meta`, 3 spécialisations : `opus` pour architecte/revieweur/mentor, `haiku` pour documentaliste/chef_projet/interviewer_skill, `inherit` écrit explicitement ailleurs), verrouillé par le bloc 13. **Reste le volet `allowed-tools:` sur les 4 commandes** : non appliqué faute de pouvoir vérifier en session réelle qu'une liste restrictive ne casse pas la délégation (une liste incomplète casserait les commandes en silence) | 2026-08-20 (volet 1) |
| S-32 | Porter le seuil anti-délégation-triviale dans la CHARTE (couche 1) | Haute | mainteneur | Terminé (2026-08-20) — la règle « déléguer du trivial coûte plus qu'il ne rapporte » n'existait qu'au gabarit projet (couche 2), donc perdait l'arbitrage face au §6 de la CHARTE, qui prime (`CHARTE.md:6`). CHARTE §6 réécrit ; verrouillé par le bloc 14 | 2026-08-20 |
| S-33 | Réparer le hook `SessionStart` et le test qui le couvrait mal | Haute | mainteneur | Terminé (2026-08-20) — `adr_ouverts()` lisait toute ligne contenant `🔧` ou « À ARBITRER » : **faux positif systématique** (la prose du §0 du gabarit, tronquée, annoncée à chaque session de chaque projet) et **faux négatif** (les vrais ADR, décrits dans le tableau §9, non détectés). Nouveau contrat : lignes de tableau de la section « Décisions en attente » dont la cellule Statut vaut À décider / À arbitrer / Ouvert. Fixture du test = **le gabarit réellement livré** (4 cas, dont la non-régression du faux positif) | 2026-08-20 |
| S-34 | Alléger l'amorçage de chaque délégation | Moyenne | mainteneur | Terminé (2026-08-20) — les 10 fichiers d'agents et de spécialisations ordonnaient une relecture intégrale de la CHARTE (~1 520 tokens) pour 3 à 5 règles réellement appliquées. Règles inlinées par rôle (le corps de l'agent est déjà chargé) + « consulte `CHARTE.md` si un point transverse sort de cette liste ». **Exception : le `revieweur` garde la lecture intégrale** (il vérifie la conformité). Transcript d'entretien brut sorti du plugin des équipes → `docs/interviews/` | 2026-08-20 |

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R-01 | Dérive de version du socle entre projets pendant le statu quo (diffusion par merge) | Élevée | Moyen | **Rectifié le 2026-07-30** : la prémisse « table rase » (2026-07-21) était inexacte — ~7 projets figés existent (veille MRAE, `nemelios`…). Décision : ils **restent gelés** (pas de mise à jour). Donc aucune population à tenir synchronisée par merge ; les nouveaux projets sont diffusés par marketplace + template. Risque de dérive sans objet (aucune diffusion attendue vers les figés) | Fermé (rectifié 2026-07-30) |
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
| 2026-07-29 | Template de création de projet post-bascule (ADR-003) | **Option B acceptée** : un dépôt-template dédié « slim » (`geoid_agents_template`) remplace « Use this template » sur le dépôt socle entier. Le template ne porte que le résiduel (CHARTE, `settings.json` avec le plugin déclaré, `templates/`, `specialisations/`, bootstrap). Options A (statu quo) et C (variantes) écartées. Mise en œuvre → S-15 | Achève la séparation des canaux de l'ADR-001 ; supprime la duplication plugin local/installé, la CI héritée et le poids mort dans les dépôts projet. Déclaration du plugin en `settings.json` commité → install au démarrage sur toutes surfaces (dont WSL/desktop/cloud, où `/plugin` est indisponible). Détail : `docs/adr/ADR-003-template-projet.md` |
| 2026-07-29 | Statut des skills brouillons de plugin (S-12) | **Option A — assumer l'état actif.** Prémisse confirmée (doc Claude Code) : les skills embarqués par un plugin sont tous découverts/actifs dès l'install, sans activation ni désactivation par skill ; `skillOverrides` ne vise pas les skills de plugin ; pas de champ `draft`. Décision : ne PAS geler (option B, `disable-model-invocation`, écartée — annulerait la valeur auto-applicable et rendrait les évals S-13 sans objet) ni sortir du plugin (option C, écartée — ferait perdre `environnement-arcgis-tse` qui est complet et revu). Les deux 0.1 sont **reclassés « actif — complétion en cours »** dans le registre ; règle posée : *seul un contenu qu'on assume de voir auto-appliqué vit dans `plugins/geoid/skills/`*. | Lecture des deux SKILL.md : contenu sûr, manques regroupés et explicitement étiquetés « à compléter/à confirmer » (donc jamais présentés comme faits) et périphériques ; `environnement-arcgis-tse` déjà revu (critique APPROUVÉ). Aucune capacité native de gel sélectif (option B non fiable sans test). Cohérent avec le tout-ou-rien plugin acté à l'ADR-001 |
| 2026-07-30 | Mainteneur du socle nommé | **D. Grohan est mainteneur** du socle (registre `skills-geoid-registre-et-methode.md` et `REX-pilotes.md` mis à jour). **Suppléant : à désigner** (→ S-16). | Répond au critère de gouvernance de l'audit (2026-07-30). La désignation d'un **suppléant** reste requise pour lever réellement le risque de dépendance à une seule personne — c'est le point que l'audit juge le plus urgent |
| 2026-07-30 | Sort des 7 projets figés (audit ; S-09 ; R-01) | **Ils restent gelés** (pas de migration, décision mainteneur). Rectifie le constat « table rase » du 2026-07-21 : des projets figés existent bien (~7, dont la veille MRAE et `nemelios`), mais ne recevront aucune correction — **gel assumé**. S-09 clôturée sur cette base rectifiée ; R-01 rectifié (reste fermé). | L'audit a établi que la prémisse « aucun projet aval » était inexacte. Le gel est acceptable (ces projets peuvent vivre figés) ; ce qui ne l'était pas, c'était de l'inscrire « sans objet ». Honnêteté de registre |
| 2026-07-30 | Passage en version **1.0.0** | La version publiable (ex-`0.5.2`) devient **1.0.0**, première version officiellement supportée. Bump aligné (SOCLE_VERSION, marketplace, deux `plugin.json`) + CHANGELOG 1.0.0. Tag `1.0.0` + release à pousser par le mainteneur. | Socle validé à l'usage (audit), template de projet en place (ADR-003), mainteneur nommé : les conditions d'une v1 supportée sont réunies. Alignement strict conservé (ADR-001c) |
| 2026-07-30 | Correctifs post-audit agentique (dérive doc + `grep`/`find`) | Suite à l'audit d'ingénierie agentique (externe, 2026-07-30) : dérive documentaire corrigée (listes de tests README/DEMARRER → 6 ; arborescence du README ; `evals/README` « brouillon » → « actif » ; version d'éval 1.1 → 1.2 ; docstring de `packager_skill.py`) ; **retrait de `Bash(grep:*)`/`Bash(find:*)` de l'`allow`** (contournaient le `deny` sur `.env`), dans le socle et le template. **Décision (résout l'écart §4.1) : `.claude/settings.json` n'est PAS synchronisé vers le template** — il est propre à chaque dépôt ; DEMARRER rectifié. | 9 des 12 écarts §4 de l'audit étaient des désynchronisations entre copies, dont plusieurs introduites le jour même : confirme la thèse « trop de registres manuels » (§3.3). Hooks (§3.1), mesure (§3.2), complétion des skills (§3.4) et test CHARTE↔skill (§3.6) restent à planifier |
| 2026-07-30 | Premiers hooks du plugin (§3.1 / audit S-22) | Le plugin `geoid` embarque `hooks/hooks.json` (auto-chargé) + 2 scripts : **`bloquer_secrets.py`** (PreToolUse Write/Edit → refus, code 2, si secret en clair — précision élevée : littéraux et formats connus, jamais les références `os.environ`/`${…}`) et **`injecter_contexte.py`** (SessionStart → version du plugin + points « À ARBITRER » du projet ; résout l'écart §4.9, `cadrer-projet` reformulé). Test `tests/test_hooks.py` (8 cas, 7ᵉ suite CI). | Rend *exécutable* la règle CHARTE §4 « jamais de secret en clair » (même règle que le bloc 7, mais à l'écriture et dans tout projet) — passage « consigne → garantie » demandé par l'audit. ⚠️ **Chargement/blocage réels non vérifiables hors session** (`/plugin` indisponible ici) : à confirmer en session réelle (checklist). Garantie de 1er niveau, non étanche (hors Write/Edit). Restent : hook SRC/GeoJSON (S-29), test CHARTE↔skill (S-23) |
| 2026-07-31 | Fin de la promesse « le plugin s'installe automatiquement » (retour terrain) | **Constat, sur un projet réel créé depuis `geoid_agents_template`** : session démarrée sans aucune commande `/geoid:…` ni agent `@geoid:*`, alors que `enabledPlugins` était bien pris en compte. Cause établie : `enabledPlugins` **active** le plugin sans garantir qu'une copie installée soit rattachée au projet — la seule copie du poste était au scope `local` d'un autre dépôt et en 0.5.2, pendant que la marketplace clonée était bien en 1.0.0 (`autoUpdate` ne rafraîchit que la marketplace). Correctif documentaire : **installation explicite `claude plugin install geoid@geoid-socle --scope user`, une fois par poste**, vérification par `claude plugin list` (une ligne par scope), relance de `claude`, + tableau de diagnostic. Portée : socle (`README.md`, `DEMARRER.md`) et template (PR #1 : `DEMARRER.md` étape 2 dédiée + renumérotation, `README.md`, `CLAUDE.md` bootstrap). Au passage, **commandes préfixées partout** (`/geoid:cadrer-projet`, `/geoid:cloturer-session` — la forme nue ne résout pas), résiduel resynchronisé. | Le chemin nominal documenté ne fonctionnait pas : coût réel en temps sur la première prise en main, et symptôme trompeur (statut *enabled* sans rien de chargé). Doc-only, pas de bump. ⚠️ Non tranché : savoir si l'auto-installation par `enabledPlugins` fonctionne sur un poste **vierge** (jamais observé ici) — la doc n'en dépend plus. Reste à confirmer par un « Use this template » de bout en bout |

| 2026-08-20 | Lot 1 des correctifs de l'audit externe du 2026-08-20 (S-19, S-25 volet 1, S-32, S-33, S-34) | Cinq correctifs livrés d'un coup, plus **trois blocs de test** (13 `model:` obligatoire, 14 seuil de délégation en couche 1, 15 chemins cités par un SKILL.md atteignables depuis un dépôt projet). Chacun a été vérifié **rouge sur l'état d'avant** avant d'être déclaré vert. Arbitrage retenu sur S-19 : **embarquer** `generer_doc_html.py` dans le plugin (constat C-11 de l'audit, conforme à l'ADR-001 §2) plutôt que retirer la consigne du skill, comme le proposait le plan d'action joint — retirer la consigne aurait été un revirement d'ADR non instruit, et aurait jeté un script déjà testé. | L'audit externe a été vérifié constat par constat contre le dépôt avant d'agir : les 6 constats vérifiables tenaient tous. Les trois blocs de test sont la seule mesure qui empêche ces règles de se reperdre avec un mainteneur unique — même médecine que le bloc 11 (S-23). ⚠️ Le bloc 15 dans sa première rédaction résolvait les chemins depuis la racine du socle : il aurait laissé passer `scripts/generer_doc_html.py`, c'est-à-dire précisément le défaut S-19. Corrigé pour ne reconnaître que le périmètre réellement livré (plugin + résiduel du template). |

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
