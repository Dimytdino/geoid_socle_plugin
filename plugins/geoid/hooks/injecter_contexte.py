#!/usr/bin/env python3
"""Hook SessionStart du plugin geoid — injection de contexte.

Injecte au démarrage de session :
  1. la **version du plugin geoid installé** (lue dans le plugin lui-même via
     ${CLAUDE_PLUGIN_ROOT}) — ce qui résout l'écart §4.9 : plus besoin de lire
     `SOCLE_VERSION`, fichier du socle absent d'un dépôt projet ;
  2. les points « À ARBITRER » du `CLAUDE.md` du projet, s'il y en a, pour que
     l'orchestrateur les ait en tête sans relecture.

Contrat Claude Code (SessionStart) : le texte écrit sur stdout est ajouté au
contexte de la session ; on sort en 0. Léger par conception (budget de
contexte).
"""
import os, sys, json, pathlib


def version_plugin():
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if root:
        pj = pathlib.Path(root) / ".claude-plugin" / "plugin.json"
        try:
            return json.loads(pj.read_text(encoding="utf-8")).get("version", "inconnue")
        except Exception:
            pass
    return "inconnue"


def adr_ouverts():
    cm = pathlib.Path("CLAUDE.md")
    if not cm.is_file():
        return []
    ouverts = []
    for ligne in cm.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "À ARBITRER" in ligne or "🔧" in ligne:
            ouverts.append(ligne.strip().lstrip("#>-* ").strip())
    return ouverts[:10]


def main():
    lignes = [
        f"[geoid] Plugin d'équipe geoid v{version_plugin()} actif "
        f"(agents, skills et commandes préfixés `geoid:`)."
    ]
    ouverts = adr_ouverts()
    if ouverts:
        lignes.append("Points à arbitrer encore ouverts dans le CLAUDE.md du projet :")
        lignes.extend(f"  - {o}" for o in ouverts)
    sys.stdout.write("\n".join(lignes) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
