#!/usr/bin/env python3
"""Synchronise le contenu « résiduel » du socle vers le dépôt-template
`geoid_agents_template` (ADR-003, option B ; S-15).

Sens **unidirectionnel** : le socle est la source de vérité. Seuls les
fichiers copiés à l'identique dans le template sont concernés — `CHARTE.md`,
`templates/`, `specialisations/`. Le reste du template (`.claude/settings.json`,
`CLAUDE.md`, `DEMARRER.md`, `README.md`) lui est propre et n'est JAMAIS touché
ici.

Usage :
  python3 scripts/sync_template.py --check  <chemin_clone_template>
      Compare et signale toute dérive (sortie 1 si dérive). À lancer au release.
  python3 scripts/sync_template.py --apply  <chemin_clone_template>
      Recopie le résiduel dans le clone (n'écrit rien d'autre, ne supprime
      rien). Ensuite, relire `git status` / `git diff` dans le clone et
      committer / pousser à la main.
"""
import sys, pathlib, shutil, filecmp

RACINE = pathlib.Path(__file__).resolve().parents[1]

# Le sous-ensemble « résiduel » copié à l'identique socle → template : ce
# qu'un plugin ne peut PAS fournir. Aucun script n'y figure (arbitrage
# S-19/S-26, 2026-08-25). L'outillage exécutable d'équipe voyage par le
# plugin — `generer_doc_html.py` et sa charte CSS vivent dans
# `plugins/geoid/scripts/` et s'invoquent via `${CLAUDE_PLUGIN_ROOT}`,
# comme le prévoit l'ADR-001 §2. Un script présent des deux côtés serait une
# seconde source de vérité pour le même fichier, versionnée par l'autre canal.
# Le bloc « aucun script dans le résiduel » de tests/test_sync_template.py
# tient cette règle.
RESIDUEL_FICHIERS = ["CHARTE.md"]
RESIDUEL_DOSSIERS = ["templates", "specialisations"]


def fichiers_residuel(socle):
    """Chemins relatifs POSIX de tous les fichiers du résiduel sous `socle`."""
    rels = []
    for f in RESIDUEL_FICHIERS:
        if (socle / f).is_file():
            rels.append(f)
    for d in RESIDUEL_DOSSIERS:
        base = socle / d
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    rels.append(p.relative_to(socle).as_posix())
    return sorted(rels)


def comparer(socle, template):
    """Retourne (manquants, differents, en_trop). Dérive si l'un est non vide."""
    src = set(fichiers_residuel(socle))
    manquants, differents = [], []
    for rel in sorted(src):
        cible = template / rel
        if not cible.is_file():
            manquants.append(rel)
        elif not filecmp.cmp(socle / rel, cible, shallow=False):
            differents.append(rel)
    # « en trop » : fichier présent dans un dossier résiduel du template mais
    # absent du socle (ex. un gabarit supprimé côté socle). Signalé, jamais
    # supprimé automatiquement.
    en_trop = []
    for d in RESIDUEL_DOSSIERS:
        base = template / d
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(template).as_posix()
                    if rel not in src:
                        en_trop.append(rel)
    return sorted(manquants), sorted(differents), sorted(en_trop)


def appliquer(socle, template):
    """Copie le résiduel du socle vers le template. Retourne les fichiers écrits."""
    ecrits = []
    for rel in fichiers_residuel(socle):
        cible = template / rel
        if not cible.is_file() or not filecmp.cmp(socle / rel, cible, shallow=False):
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(socle / rel, cible)
            ecrits.append(rel)
    return ecrits


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("--check", "--apply"):
        sys.exit("Usage : python3 scripts/sync_template.py --check|--apply <chemin_clone_template>")
    mode = sys.argv[1]
    template = pathlib.Path(sys.argv[2]).resolve()
    if not template.is_dir():
        sys.exit(f"Erreur : clone du template introuvable : {template}")

    if mode == "--check":
        manquants, differents, en_trop = comparer(RACINE, template)
        if not (manquants or differents or en_trop):
            print(f"Template à jour ({len(fichiers_residuel(RACINE))} fichiers résiduel).")
            return
        print("DÉRIVE template / socle :")
        for rel in manquants:  print("  manquant  :", rel)
        for rel in differents: print("  différent :", rel)
        for rel in en_trop:    print("  en trop   :", rel)
        print("→ lancer --apply (les « en trop » se retirent à la main), puis committer dans le clone.")
        sys.exit(1)

    ecrits = appliquer(RACINE, template)
    if ecrits:
        print(f"{len(ecrits)} fichier(s) mis à jour dans le template :")
        for rel in ecrits:
            print("  •", rel)
        print("→ relire `git status` / `git diff` dans le clone, puis committer / pousser.")
    else:
        print("Rien à faire : template déjà à jour.")


if __name__ == "__main__":
    main()
