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


TITRE_SECTION = "Décisions en attente"
STATUTS_OUVERTS = {"à décider", "à arbitrer", "ouvert"}


def adr_ouverts():
    """ADR réellement ouverts du `CLAUDE.md` projet, sous la forme `ADR-00X — sujet`.

    Contrat (gabarit `templates/CLAUDE.projet.template.md` §9) : la seule
    source est le **tableau** de la section « Décisions en attente », de la
    forme `| ADR | Sujet | Tâches bloquées | Statut |`. Une ligne compte si sa
    cellule Statut vaut « À décider », « À arbitrer » ou « Ouvert ».

    Toute prose est ignorée, y compris celle qui contient `🔧 À ARBITRER` :
    le §0 du gabarit explique le marqueur en toutes lettres, et l'ancien filtre
    ligne-à-ligne le remontait comme un arbitrage fantôme à chaque session.
    Les lignes contenant un placeholder `{{…}}` non substitué sont ignorées
    elles aussi : un gabarit non rempli n'est pas une décision en attente.
    """
    cm = pathlib.Path("CLAUDE.md")
    if not cm.is_file():
        return []
    ouverts = []
    dans_section = False
    for ligne in cm.read_text(encoding="utf-8", errors="ignore").splitlines():
        nue = ligne.strip()
        if nue.startswith("#"):
            dans_section = TITRE_SECTION in nue
            continue
        if not dans_section or not nue.startswith("|") or "{{" in nue:
            continue
        cellules = [c.strip() for c in nue.strip("|").split("|")]
        if len(cellules) < 4:
            continue
        if set(cellules[-1]) <= set("-: "):  # ligne de séparation du tableau
            continue
        if cellules[-1].lower() not in STATUTS_OUVERTS:
            continue  # en-tête (« Statut ») et lignes tranchées
        ouverts.append(f"{cellules[0]} — {cellules[1]}")
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
