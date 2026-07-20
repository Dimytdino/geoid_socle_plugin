#!/usr/bin/env python3
"""Packager un skill GéoID en fichier .skill installable.
Usage : python3 scripts/packager_skill.py .claude/skills/nom-du-skill/
"""
import sys, zipfile, pathlib

# Allowlist explicite : seuls SKILL.md et les fichiers sous references/ sont
# inclus dans l'archive. Tout autre contenu (notes d'entretien, brouillons,
# sous-dossiers ad-hoc) est exclu par défaut, quels que soient leurs noms.
FICHIERS_RACINE_AUTORISES = {"SKILL.md"}
DOSSIERS_AUTORISES = {"references"}


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage : python3 scripts/packager_skill.py .claude/skills/nom-du-skill/")
    src = pathlib.Path(sys.argv[1]).resolve()
    if not (src / "SKILL.md").exists():
        sys.exit(f"Erreur : pas de SKILL.md dans {src}")
    out = src.parent / f"{src.name}.skill"
    inclus = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_symlink() or not f.is_file():
                continue
            rel = f.relative_to(src)
            parties = rel.parts
            if len(parties) == 1 and parties[0] in FICHIERS_RACINE_AUTORISES:
                pass  # SKILL.md à la racine
            elif parties[0] in DOSSIERS_AUTORISES:
                pass  # fichiers sous references/
            else:
                continue
            z.write(f, f.relative_to(src.parent))
            inclus += 1
    print(f"Skill packagé : {out} ({inclus} fichier(s))")


if __name__ == "__main__":
    main()
