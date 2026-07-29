# ADR-003 — Template de création de projet après la bascule en plugins

- **Statut** : **Accepté — option B** (décision du 2026-07-29, D. Grohan)
- **Date d'instruction** : 2026-07-29
- **Instruit par** : `architecte`
- **Version du socle concernée** : 0.5.2
- **Référence** : ADR-001 (transposition en plugins, §4.4 — les deux canaux de diffusion) ; `DEMARRER.md` étape 1

> Numérotation : « ADR-002 » désigne le pilote « documentation FME » (ADR de
> projet, hors socle) référencé par le skill `fme-tse`. Le présent ADR du
> socle prend donc le numéro 003 pour éviter toute collision.

## 1. Contexte

L'ADR-001 a acté **deux canaux de diffusion** distincts (§4.4) :
1. le **plugin** `geoid` (agents, skills, commandes) — diffusé par la
   **marketplace**, installé/mis à jour par utilisateur ou par projet ;
2. le **« template résiduel »** (CHARTE, `settings.json`, `templates/`,
   `specialisations/`, `CLAUDE.md` bootstrap) — ce qu'un plugin ne peut pas
   fournir, diffusé par copie/merge git.

La bascule a bien déplacé le contenu du canal 1 dans `plugins/`. **Mais le
point d'entrée de création de projet n'a pas été retranché** : `DEMARRER.md`
étape 1 pointe toujours « Use this template » sur le dépôt du socle
(`geoid_socle_plugin`) **entier**. Créer un projet copie donc aussi les
sources du plugin, la marketplace, `tests/`, `scripts/`, `evals/`,
`CHANGELOG`, `SOCLE_VERSION` et les workflows CI — c'est-à-dire le moteur du
socle, sans rapport avec un projet.

Ce point n'avait pas été explicitement tranché à l'ADR-001. Il l'est ici.

## 2. Options

### Option A — Statu quo : le dépôt socle sert de template
« Use this template » reste sur `geoid_socle_plugin`. Rien à créer.

- **+** Effort de mise en place nul ; un seul dépôt à maintenir.
- **−** Chaque projet traîne tout le socle (poids mort, repères trompeurs).
- **−** **Duplication du plugin** : copie locale `plugins/geoid/` **≠**
  version installée par la marketplace → source de vérité ambiguë, dérive
  silencieuse.
- **−** Le **workflow CI du socle est recopié** et se déclenche dans le
  projet (bruit, puis échecs dès que le projet diverge).
- **−** Re-mélange les deux canaux que l'ADR-001 a séparés.

### Option B — Template dédié « slim »
Un nouveau dépôt `geoid-projet-template` (marqué *template* GitHub) ne
contenant que l'utile projet : `CHARTE.md`, `.claude/settings.json` (plugin
`geoid` déjà déclaré), `templates/` doc, `specialisations/`, `CLAUDE.md`
bootstrap, guide de démarrage.

- **+** Dépôt projet propre ; modèle mental clair (le plugin vient d'un seul
  endroit, la marketplace).
- **+** Aucune duplication, aucune CI parasite héritée.
- **+** Matérialise la séparation des canaux de l'ADR-001 — aboutissement
  logique de la bascule.
- **−** Coût de mise en place unique (~½ journée) ; un deuxième dépôt à
  synchroniser depuis le socle (sous-ensemble figé, changements rares).

## 3. Décision

**Option B.** Le coût unique et borné (mise en place + une synchro simple
d'un contenu qui bouge rarement) élimine des coûts récurrents et des risques
réels : dépôts projet encombrés, CI héritée qui casse, et surtout
l'ambiguïté « copie locale du plugin vs version installée ». C'est aussi la
seule option cohérente avec la séparation des canaux décidée en ADR-001.

L'option A resterait acceptable pour une équipe très réduite, peu de projets
et à horizon court — ce n'est pas la trajectoire du pôle (extension aux
chargés d'identification, multiplication des projets).

## 4. Conséquences

- **Nouveau dépôt** `geoid-projet-template` (org TSE-Pole-Geomatique, privé,
  marqué *template*) : le résiduel + `.claude/settings.json` portant
  `extraKnownMarketplaces` (marketplace `geoid-socle`) et `enabledPlugins`
  (`geoid@geoid-socle`, `autoUpdate` activé). Le plugin s'installe alors au
  démarrage de la session, **sans `/plugin` manuel** — ce qui fonctionne sur
  toutes les surfaces (terminal, desktop, WSL, sessions cloud), contrairement
  à l'installation interactive.
- **Synchro socle → template** : le socle reste la source de vérité du
  résiduel (CHARTE, `settings.json`, `templates/`, `specialisations/`). Un
  mécanisme simple (script de copie du sous-ensemble, joué aux releases)
  maintient le template à jour. À définir à la mise en œuvre (S-15).
- **Documentation** : `DEMARRER.md` étape 1 pointe le nouveau template ;
  l'installation manuelle par `/plugin` disparaît du chemin nominal (gardée
  en option). `README.md` et le `CLAUDE.md` bootstrap alignés.
- **Projets existants** : inchangés ; ils récupèrent la déclaration du plugin
  via le canal de merge du socle, ou par ajout ponctuel des deux clés.
- **Le dépôt du socle** cesse d'être un template ; il redevient purement le
  dépôt de développement du socle + la marketplace.
- Mise en œuvre suivie en **S-15** (`docs/suivi-projet.md`).
