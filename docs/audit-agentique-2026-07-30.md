<!-- ════════════════════════════════════════════════════════════════
     docs/audit-agentique-2026-07-30.md
     Audit d'ingénierie agentique du socle geoid-socle, périmètre 1.0.0.
     DISTINCT de « l'audit du 2026-07-30 » déjà cité dans
     docs/suivi-projet.md (qui porte sur la valeur, les projets figés et
     la gouvernance) : celui-ci porte sur la CONCEPTION AGENTIQUE et
     l'exécutabilité réelle du socle. Les deux se complètent.
     Auditeur : revue externe (ingénierie agentique). Non commité.
     ════════════════════════════════════════════════════════════════ -->

# Audit du socle GéoID — fond et forme

| | |
|---|---|
| **Périmètre audité** | dépôt `geoid_socle_plugin` à l'état `1.0.0` (`main`, `e1454f8`), 74 fichiers, 664 Ko |
| **Méthode** | lecture intégrale des 37 documents, des 10 fiches d'agent, 3 skills, 4 commandes, 5 scripts, 6 suites de test ; exécution de la CI localement (**22 tests verts**) ; confrontation systématique des consignes aux capacités réelles de Claude Code |
| **Date** | 2026-07-30 |
| **Verdict global** | **Socle solide, conception au-dessus de la moyenne — mais qui laisse son levier principal inexploité et sa valeur non mesurée.** Continuer, en réorientant l'effort de la gouvernance vers l'exécution. |

---

## 1. Verdict par axe

| Axe | Note | En une phrase |
|---|:---:|---|
| Architecture de diffusion | **A** | Deux canaux tranchés par ADR, cohérents avec les vraies contraintes de l'outil. Rare. |
| Séparation des privilèges | **A−** | Outils restreints = garanties réelles ; exception `revieweur` assumée et documentée. |
| Discipline de contexte | **A** | CLAUDE.md court, suivi externalisé, et un test qui l'empêche de regrossir. |
| Outillage / CI | **B+** | 6 suites, 10 blocs d'intégrité, CI qui refuse le SKIP silencieux. Bien ciblé, mais pas sur le bon risque (§3.6). |
| **Garanties d'exécution (hooks)** | **D** | **Zéro hook.** Les règles non négociables reposent entièrement sur la docilité du modèle. |
| **Mesure de la valeur** | **E** | 2 pilotes aboutis, **15 cases d'indicateurs vides**, v1.0.0 « validée à l'usage » sans un chiffre. |
| Contenu métier (skills) | **C** | 1 skill excellent, 2 sur 3 incomplets et actifs en production, le plus rentable non lancé. |
| Soutenabilité | **C−** | Bus factor = 1, assumé sans mitigation, sur un actif désormais estampillé « supporté ». |
| Rigueur documentaire | **C+** | Honnêteté exemplaire sur le fond, mais dérive mesurable de la forme (§4). |

---

## 2. Forces — ce qu'il faut protéger

**2.1 L'architecture de diffusion est raisonnée, pas subie.** `ADR-001` part de six faits techniques vérifiés (activation tout-ou-rien, préfixage, ce qu'un plugin *ne peut pas* fournir) et en déduit l'option D plutôt que de l'affirmer. `ADR-003` va au bout en retranchant le point d'entrée resté incohérent. La très grande majorité des socles d'agents que l'on rencontre n'a pas ce niveau de raisonnement — et paie l'ambiguïté « copie locale vs version installée » que l'ADR-003 a précisément éliminée.

**2.2 Les garanties par les outils sont le bon réflexe.** `architecte` et `mentor` sont en `Read, Grep, Glob` : leur non-production n'est pas une consigne, c'est une impossibilité. Et l'exception est traitée honnêtement — [README.md:206](README.md:206) déclare que le `revieweur` garde `Bash`, donc que sa non-production redevient une simple consigne. Nommer ses propres trous est un marqueur de maturité.

**2.3 Le budget de contexte est traité comme une ressource rare.** Le CLAUDE.md projet (108 lignes) est lu à chaque session ; roadmap, risques et revues vivent dans `docs/suivi-projet.md`, lu à la demande. Surtout, le bloc 4 de [test_socle_integrity.py:53](tests/test_socle_integrity.py:53) **interdit** les tableaux de suivi dans le template : la discipline ne peut pas régresser par inattention. C'est exactement le bon usage d'un test sur un actif en langage naturel.

**2.4 L'outillage teste l'invisible.** Verrouiller `defaultMode: default` et l'absence de `Bash(python3:*)` en `allow` par un test ([bloc 3](tests/test_socle_integrity.py:34)) empêche un durcissement de sécurité de se faire annuler six mois plus tard « pour aller plus vite ». La CI refuse même le SKIP silencieux du test HTML ([tests.yml:27](.github/workflows/tests.yml:27)) — détail qui trahit quelqu'un qui a déjà été mordu par un test vert-mais-non-exécuté.

**2.5 Le harnais d'évals lit correctement le problème.** `evals/` sépare ce qui est testable hors ligne (structure, couverture, anti-doublons) de ce qui ne l'est pas (le déclenchement réel, qui exige un LLM avec le skill chargé). Distinguer les deux, et refuser en CI un skill publié sans jeu d'éval, est une pratique que peu d'équipes atteignent.

**2.6 `conventions-sig-tse` est un vrai bon skill.** Règles vérifiables (« toujours `ST_MakeValid` avant INSERT », pas « être prudent »), pièges chiffrés (10 ha « mesurent » 13,5 ha en 3857), anti-déclencheurs explicites, et une `description` écrite pour déclencher plutôt que pour documenter. C'est le standard sur lequel aligner les deux autres.

**2.7 L'honnêteté est structurelle.** [README.md:127](README.md:127) assume que `deny`/`ask` est « une friction de premier niveau, pas une protection étanche ». Le journal des décisions rectifie publiquement une prémisse fausse (« table rase ») au lieu de l'enterrer. Le registre étiquette ses manques (« à compléter par Kilian ») plutôt que de les masquer. C'est ce qui rend tout le reste crédible — et c'est le premier actif à ne pas perdre.

---

## 3. Faiblesses de fond

### 3.1 🔴 Aucun hook : la philosophie affichée n'est pas outillée

[README.md:212](README.md:212) pose en note de conception que « les agents les plus solides sont ceux dont les **outils** diffèrent », c'est-à-dire : préférer la garantie technique à la consigne. Or le mécanisme Claude Code qui produit ces garanties — les **hooks** — est **totalement absent des deux plugins**.

Conséquence directe : toutes les règles vraiment critiques restent de la prose que le modèle peut ignorer.

| Règle CHARTE | Statut réel aujourd'hui |
|---|---|
| §4 — jamais de secret en clair | consigne dans 6 fichiers, **0 vérification** |
| §4 — jamais de donnée foncière dans un livrable sortant | consigne, **0 vérification** |
| §3 — GeoJSON en 4326, jamais en 2154 | consigne (× 4 emplacements), **0 vérification** |
| §5 — revue avant livraison | consigne, **0 vérification** |

Le socle a donc mis ses garanties là où c'était facile (restreindre `tools`) et aucune là où se situe son cœur de métier. C'est le levier n°1, et il est bon marché : un `PreToolUse` sur `Write|Edit` qui refuse (`exit 2`) un contenu contenant une chaîne de connexion, c'est ~20 lignes de bash et une entrée dans `hooks/hooks.json`.

Cas d'école : le bug du pilote `widget_export_geojson` ([CHANGELOG.md:213](CHANGELOG.md:213)) — un GeoJSON exporté en 2154 « par conformité CHARTE ». La correction retenue a été **d'ajouter une règle de prose**, alors que le CHANGELOG note lui-même que « le point de vigilance écrit dans le REX n'avait pas suffi ». Une même cause a été traitée deux fois par le même moyen inefficace. Un hook qui refuse d'écrire un `.geojson` dont les coordonnées dépassent ±180 rend la classe de bug impossible, définitivement.

### 3.2 🔴 Le gain n'est pas mesuré — et l'instrument est prêt, mais vide

- `REX-pilotes.md` : **15 cases d'indicateurs, zéro remplie** ; la section « SYNTHÈSE TRANSVERSE » est vierge.
- `docs/mesure-gain-entretiens.md` : kit d'entretien rédigé, **non joué**.
- Deux pilotes sont pourtant **aboutis** (~720 lignes de doc FME ; widget ExB ~327 lignes) depuis 5-6 semaines — et le document reconnaît lui-même que l'information « est dans la mémoire de Kilian et de Fateh, et qu'elle se dégrade ».

Le socle est passé en `1.0.0` au motif qu'il est « validé à l'usage » sans qu'un seul chiffre existe. Le seuil de rentabilité est posé (~1,25 j/projet) : il n'est ni confirmé ni infirmé. Et la décision suivante — l'extension aux 7 chargés d'identification — se prendrait sur une conviction : la grille go/no-go phase 2 ([REX-pilotes.md:140](REX-pilotes.md:140)) compte 7 critères dont **5 non cochables aujourd'hui**.

**Coût pour lever ce doute : 2 entretiens d'une heure.** C'est le meilleur rapport effort/valeur de tout l'audit.

### 3.3 🟠 Le coût de gouvernance est disproportionné à la charge utile

| Catégorie | Lignes |
|---|---:|
| **Charge utile livrée aux équipes** (10 agents + 3 skills + 4 commandes + 3 spécialisations) | **1 069** |
| Documentation de gouvernance et de méthode | **1 781** |
| Outillage mainteneur (5 scripts + 6 suites de test) | **1 348** |

Ratio méta / charge utile : **1,67**. `ADR-001` fait à lui seul 312 lignes. Les 36 commits du dépôt portent **tous** sur le socle lui-même. Six artefacts de suivi doivent être tenus à jour à la main par une seule personne : `CHANGELOG.md`, `docs/suivi-projet.md`, `skills-geoid-registre-et-methode.md`, `REX-pilotes.md`, `evals/README.md`, `docs/adr/`.

Nuance importante, à porter au crédit du projet : **cette gouvernance a produit de bonnes décisions**. ADR-001 et ADR-003 sont utiles et justes. Le problème n'est pas la méthode, c'est sa **cadence** rapportée à une équipe de ~7 personnes avec un mainteneur unique. La dérive documentaire relevée au §4 n'est pas un accident : c'est le symptôme mécanique de six registres manuels pour une personne.

### 3.4 🟠 Les deux tiers du catalogue de skills sont incomplets — et c'est le catalogue qui porte la valeur

Ce qui distingue ce socle d'un bon prompt générique, c'est la connaissance TSE. Elle vit dans les skills. Or :

- `fme-tse` (0.1) : quatre conventions structurantes marquées **« À COMPLÉTER par Kilian »** (nommage, emplacement de référence, staging→prod, journalisation des millésimes) ;
- `environnement-arcgis-tse` (0.1) : nombre d'applications, intervenants, procédure VDI **« à confirmer avec Fateh »** ;
- les deux sont **actifs en production** — décision S-12, correctement instruite et assumée, mais qui ne remplace pas la complétion ;
- `catalogue-outils-geoid`, présenté au registre comme « la règle 0 rendue exécutoire » et classé **priorité 1 — à lancer maintenant** ([registre:72](skills-geoid-registre-et-methode.md:72)), **n'est pas lancé**. C'est probablement le skill au plus fort rendement du pôle : il rend le « réutiliser avant de créer » vérifiable au lieu d'incantatoire.

Le goulot n'est pas technique, il est humain : du temps d'expert. Il doit donc être planifié comme un jalon daté avec un nom dessus, pas laissé en « à compléter ».

### 3.5 🟠 Bus factor = 1, acté sans mitigation

S-16 est marqué **« Confirmé sans suppléant au 2026-07-30 — dépendance à une seule personne assumée en l'état »** ([suivi:57](docs/suivi-projet.md:57)). Le même individu est : unique auteur des 36 commits, unique mainteneur, seul relecteur humain (`/revue-socle` délègue à un agent, pas à un tiers), et le point de passage vers l'admin pour publier les `.skill`.

Assumer un risque est légitime ; l'assumer **sans aucune mitigation** sur un actif qu'on vient d'estampiller « première version officiellement supportée » ne l'est pas. Le minimum n'est pas un binôme à temps plein : c'est **une page** — qui republie un `.skill`, qui a les droits GitHub sur l'organisation, où sont les tags, comment on sort une version. Aujourd'hui cette page n'existe pas, et `DEMARRER.md` suppose partout un lecteur qui est déjà le mainteneur.

### 3.6 🟠 La duplication la plus risquée est la seule non testée

Le socle assume **une** duplication : CHARTE §3-§4 (master) ↔ skill `conventions-sig-tse` (dérivé), régénéré à la main par le mainteneur. C'est déclaré des deux côtés — bonne pratique.

Mais l'effort de test est réparti à l'inverse du risque :

| Duplication | Risque si désynchronisée | Couverture de test |
|---|---|:---:|
| `SOCLE_VERSION` ↔ marketplace ↔ 2 × `plugin.json` | cosmétique | **bloc 8 dédié, 25 lignes** |
| CHARTE §3-§4 ↔ skill `conventions-sig-tse` | **un skill enseigne une règle périmée à tous les projets** | **aucune** |

Le scénario redouté est déjà arrivé : le bug 0.3.1 avait pour cause racine une règle SRC absente. Un amendement de la CHARTE non répercuté produit exactement le même effet, en silence. Un bloc 11 d'une trentaine de lignes (présence des jetons `2154`, `3857`, `4326`, `ST_MakeValid`, foncier, millésime de part et d'autre) refermerait ce risque pour de bon.

### 3.7 🟡 Quatre capacités de l'outil, gratuites, non utilisées

| Capacité | État | Gain |
|---|---|---|
| `hooks/` dans un plugin | **0** hook | §3.1 — le levier n°1 |
| `model:` en frontmatter d'agent | absent des 10 agents | `mentor`/`documentaliste` sur un modèle rapide, `architecte`/`revieweur` sur le plus capable : coût et latence, immédiatement |
| `allowed-tools:` sur les commandes | absent des 4 commandes | `cadrer-projet` n'a aucun besoin de `Bash` |
| `references/` dans un skill | aucun | divulgation progressive — nécessaire dès que `fme-tse` sera complété (137 lignes déjà, plafond auto-imposé à 200) |

---

## 4. Faiblesses de forme — écarts constatés

Tous vérifiés sur le dépôt. Les trois premiers sont des **régressions fonctionnelles**, pas des fautes de rédaction.

| # | Écart | Preuve | Gravité |
|:--:|---|---|:--:|
| 1 | `DEMARRER.md` annonce que `.claude/settings.json` est répercuté vers le template par `sync_template.py` ; **le script l'exclut explicitement**. Le durcissement des permissions n'a donc **aucun** chemin de propagation. | [DEMARRER.md:63](DEMARRER.md:63) vs [sync_template.py:26](scripts/sync_template.py:26) (`RESIDUEL` = `CHARTE.md` + `templates/` + `specialisations/`) | 🔴 |
| 2 | Le skill `fme-tse` ordonne de produire le HTML via `scripts/generer_doc_html.py` et cite `documentation-fme/docs/workflow-covisibilite.md` : **aucun des deux n'existe dans un dépôt projet**. Consigne inexécutable côté équipe — et violation de l'item « Portabilité » de leur propre grille `/revue-socle`. | [fme-tse/SKILL.md:63](plugins/geoid/skills/fme-tse/SKILL.md:63), [:65](plugins/geoid/skills/fme-tse/SKILL.md:65), [:94](plugins/geoid/skills/fme-tse/SKILL.md:94) | 🔴 |
| 3 | `Bash(grep:*)` et `Bash(find:*)` en `allow` contournent le `deny` sur `cat *.env*` : `grep . .env` lit le secret sans confirmation. La limite est documentée dans son principe, mais ce contournement-là est gratuit à fermer. | [settings.json:7-8](.claude/settings.json:7) vs [:30](.claude/settings.json:30) | 🟠 |
| 4 | Trois listes de tests divergentes : README en annonce **4**, DEMARRER **5**, la CI en lance **6**. | [README.md:152](README.md:152), [DEMARRER.md:40](DEMARRER.md:40), [tests.yml](.github/workflows/tests.yml) | 🟠 |
| 5 | Le bloc « Structure » du README ne reflète plus l'arborescence : `evals/`, `docs/`, `scripts/evaluer_declenchement.py`, `scripts/sync_template.py` absents. Item explicite de la grille `/revue-socle` (« le README reflète l'arborescence réelle »). | [README.md:59](README.md:59) | 🟠 |
| 6 | `evals/README.md` classe encore 2 skills en « 0.1 (**brouillon**) » — contredit la décision S-12 (« actif — complétion en cours »). | [evals/README.md:86](evals/README.md:86) | 🟡 |
| 7 | `evals/conventions-sig-tse.eval.json` évalue la version **1.1** ; le skill est en **1.2**. Aucun test ne relie `version_skill_evaluee` au registre. | eval vs [registre:35](skills-geoid-registre-et-methode.md:35) | 🟡 |
| 8 | `scripts/packager_skill.py` documente encore un chemin `.claude/skills/…`, abandonné en 0.5.0. | [packager_skill.py:3](scripts/packager_skill.py:3) | 🟡 |
| 9 | `cadrer-projet` demande de renseigner la version du plugin « = contenu de `SOCLE_VERSION` » : ce fichier **n'existe pas** dans un dépôt projet. Le champ sera rempli au doigt mouillé. | [cadrer-projet.md:134](plugins/geoid/commands/cadrer-projet.md:134) | 🟡 |
| 10 | `cloturer-session` délègue au `chef_projet` avec la consigne « mettre à jour le **CLAUDE.md** », alors que l'essentiel de la mise à jour visée est `docs/suivi-projet.md`. Le prompt réellement transmis au sous-agent contredit les instructions qui l'entourent. | [cloturer-session.md:29](plugins/geoid/commands/cloturer-session.md:29) | 🟡 |
| 11 | Le test de déclenchement **réel** des skills n'a jamais été joué : la grille de résultats de `evals/README.md` est intégralement à `—`. Le harnais existe, il n'a pas servi. | [evals/README.md](evals/README.md) grille §2 | 🟡 |
| 12 | `interview-brut.md` n'est présent que pour 1 skill sur 3, et voyage dans le plugin livré aux équipes (le packageur `.skill`, lui, l'exclut correctement). | `plugins/geoid/skills/` | 🟢 |

> **Lecture d'ensemble** : neuf de ces douze écarts sont des désynchronisations entre deux copies d'une même information. C'est la signature du §3.3 — trop de registres manuels pour une personne — et non un défaut de soin.

---

## 5. Axes d'amélioration, par rendement décroissant

1. **Mesurer** (2 h). Le kit est écrit, les pilotes sont finis, la mémoire s'efface. Sans ce chiffre, tout le reste est un pari — y compris la phase 2.
2. **Passer des consignes aux garanties** (1-2 j). Trois hooks suffisent à couvrir l'essentiel : secrets à l'écriture, SRC/GeoJSON, injection au `SessionStart` de la version du plugin et des ADR ouverts (ce dernier règle aussi l'écart n°9).
3. **Rendre le livré exécutable** (½ j). Écarts n°1 et n°2 : un skill qui ordonne de lancer un script absent perd sa crédibilité auprès de l'équipe, et un durcissement de permissions qui ne se propage pas est un durcissement fictif.
4. **Automatiser la cohérence plutôt que la surveiller** (½ j). Un bloc de test qui relie CHARTE ↔ skill dérivé ↔ registre ↔ evals tue la classe entière des écarts n°6, 7 et le risque §3.6 — et allège durablement la charge du mainteneur.
5. **Réduire la surface de gouvernance** (arbitrage). Passer de six registres manuels à trois. Le CHANGELOG et `docs/suivi-projet.md` gardent leur raison d'être ; le registre des skills, `REX-pilotes` et la grille d'évals peuvent fusionner ou se replier une fois la mesure faite.
6. **Faire porter la valeur par les skills** (jalons datés). Compléter les deux 0.1, puis lancer `catalogue-outils-geoid`. C'est du temps d'expert : ça se planifie et ça s'assigne, ça ne s'attend pas.
7. **Lever le bus factor à coût minimal** (½ j). Un suppléant nommé et **une page** de procédure de secours.
8. **Récolter les capacités gratuites** (½ j). `model:` par agent, `allowed-tools` par commande.

---

## 6. Roadmap

Numérotation raccordée au backlog existant (dernier ID utilisé : S-16).

### Horizon 1 — 2 semaines · « lever le doute, boucher les trous gratuits » (≈ 1,5 j)

| ID | Action | Traite | Effort |
|---|---|:--:|:--:|
| **S-17** | **Jouer les 2 entretiens de mesure** (kit `docs/mesure-gain-entretiens.md`) et reporter les chiffres dans `REX-pilotes.md` + la synthèse transverse | §3.2 | **2 h** |
| **S-18** | Étendre `sync_template.py` à `.claude/settings.json` **ou** retirer la promesse de `DEMARRER.md` — décider explicitement, puis livrer | écart 1 | 1 h |
| **S-19** | Rendre `fme-tse` exécutable côté projet : embarquer `generer_doc_html.py` dans le plugin `geoid` (option retenue par ADR-001 §2, jamais appliquée) ou reformuler la consigne | écart 2 | ½ j |
| **S-20** | Retirer/restreindre `Bash(grep:*)` et `Bash(find:*)` de l'`allow`, + 1 ligne de test qui l'empêche de revenir | écart 3 | 30 min |
| **S-21** | Passe de dérive documentaire : listes de tests (× 3), arborescence README, `evals/README`, versions d'évals, docstring du packageur, prompt de `cloturer-session` | écarts 4-8, 10 | 2 h |

*Jalon H1 : un chiffre de gain écrit, plus aucune consigne inexécutable dans le plugin livré.*

### Horizon 2 — 1 mois · « des consignes aux garanties » (≈ 3 j)

| ID | Action | Traite | Effort |
|---|---|:--:|:--:|
| **S-22** | **Premiers hooks** dans `plugins/geoid/hooks/` : (a) `PreToolUse` Write/Edit refusant secrets et chaînes de connexion ; (b) `SessionStart` injectant version du plugin + ADR ouverts | §3.1, écart 9 | 1 j |
| **S-23** | **Bloc 11 du test d'intégrité** : cohérence CHARTE §3-§4 ↔ skill dérivé, et registre ↔ `evals/` ↔ skills publiés (versions incluses) | §3.6, écarts 6-7 | ½ j |
| **S-24** | Suppléant nommé + **une page** de procédure de secours (droits, publication `.skill`, release, tags) | §3.5 | ½ j |
| **S-25** | `model:` sur les 10 agents, `allowed-tools:` sur les 4 commandes | §3.7 | ½ j |
| **S-26** | **Jouer les évals de déclenchement réel** des 3 skills (`--rapport`), consigner la grille datée, corriger les `description` qui sous-déclenchent | écart 11 | ½ j |

*Jalon H2 : trois règles CHARTE deviennent des garanties ; la désynchronisation CHARTE↔skill devient impossible sans casser la CI.*

### Horizon 3 — 1 trimestre · « faire porter la valeur par les skills » (≈ 5 j + temps d'expert)

| ID | Action | Traite | Effort |
|---|---|:--:|:--:|
| **S-27** | Compléter `fme-tse` → 1.0 (Kilian) et `environnement-arcgis-tse` → 1.0 (Fateh). **Jalon daté, responsable nommé** | §3.4 | 2 × ½ j expert |
| **S-28** | Créer **`catalogue-outils-geoid`** (priorité 1 du registre) — le skill au plus fort rendement du pôle | §3.4 | 1 j + inventaire |
| **S-29** | Hook de garde SRC/GeoJSON : refus d'écriture d'un `.geojson` à coordonnées hors ±180. La règle 0.3.1 rendue exécutoire | §3.1 | ½ j |
| **S-30** | Consolidation de la gouvernance : six registres → trois, après arbitrage | §3.3 | 1 j |
| **S-31** | **Go / no-go phase 2** sur la grille `REX-pilotes.md` complétée — décision documentée, plus une conviction | §3.2 | ½ j |

*Jalon H3 : la valeur du socle vient de son contenu métier, pas de son appareil de gouvernance.*

---

## 7. Indicateurs à instrumenter

Trois suffisent. Aucun n'existe aujourd'hui.

| Indicateur | Mesure | Cible | Source |
|---|---|---|---|
| **Gain par projet** | jours économisés / projet | ≥ 1,25 j (seuil de rentabilité déjà posé) | S-17, puis à chaque REX |
| **Règles garanties / règles totales** | nb de règles CHARTE couvertes par un hook ou une restriction d'outil, sur le total | ≥ 4/8 à 3 mois (0/8 aujourd'hui) | inventaire, revue trimestrielle |
| **Dérive documentaire** | nb d'écarts détectés automatiquement entre deux copies d'une même information | 0, vérifié en CI | bloc 11 (S-23) |

---

## 8. Conclusion

Ce socle est **au-dessus de la moyenne de ce qu'on rencontre** : les décisions structurantes sont instruites, les canaux de diffusion sont propres, le contexte est traité comme une ressource rare, et l'auteur nomme ses propres limites — ce dernier point étant le plus difficile à acquérir et le plus facile à perdre.

Sa faiblesse n'est pas un défaut de rigueur, c'est un **déséquilibre d'allocation**. L'effort est allé à la gouvernance de l'appareil (1 781 lignes de méta, six registres, 1 348 lignes d'outillage mainteneur) plutôt qu'à ses deux fonctions vitales : **garantir** ce qui compte (zéro hook) et **prouver** ce qu'il rapporte (zéro mesure, alors que l'instrument est prêt). La dérive documentaire du §4 n'est pas la maladie, c'en est le symptôme.

Les trois prochaines heures les plus rentables sont : **deux entretiens de mesure (S-17) et la fermeture des deux consignes inexécutables (S-18, S-19)**. Le mois suivant, trois hooks feront gagner au socle plus de fiabilité que les 400 lignes d'ADR déjà écrites — sans les contredire.

**Recommandation : continuer, en déplaçant l'effort de la description du socle vers son exécution.**
