#!/usr/bin/env python3
"""Hook SessionStart du plugin geoid — injection de contexte.

Injecte au démarrage de session :
  1. la **version du plugin geoid installé** (lue dans le plugin lui-même via
     ${CLAUDE_PLUGIN_ROOT}) — ce qui résout l'écart §4.9 : plus besoin de lire
     `SOCLE_VERSION`, fichier du socle absent d'un dépôt projet ;
  2. les points « À ARBITRER » du `CLAUDE.md` du projet, s'il y en a, pour que
     l'orchestrateur les ait en tête sans relecture ;
  3. un **avertissement d'hygiène** si le `CLAUDE.md` a dérivé : trop long, ou
     porteur de sections qui n'ont pas à occuper le contexte permanent
     (glossaire, état d'avancement, roadmap…). Le CLAUDE.md est lu en entier à
     chaque session et rien, dans le cycle de vie d'un projet, ne l'allège
     spontanément — l'avertissement est la seule force de rappel. Il est
     volontairement **non bloquant** : il suggère `/geoid:cloturer-session`
     (étape de dégraissage), il n'impose rien.

Contrat Claude Code (SessionStart) : le texte écrit sur stdout est ajouté au
contexte de la session ; on sort en 0. Léger par conception (budget de
contexte).
"""
import os, sys, json, re, pathlib, unicodedata


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


# Budget de lignes du CLAUDE.md projet. Le gabarit vierge fait ~130 lignes ;
# rempli, il tourne autour de 150. 180 laisse la marge d'un projet réellement
# documenté sans laisser passer l'accumulation (glossaire + avancement +
# historique font vite franchir la barre). Doit rester cohérent avec le seuil
# annoncé dans `templates/CLAUDE.projet.template.md`.
SEUIL_LIGNES = 180

# Titres qui n'ont rien à faire dans le contexte permanent : ils décrivent
# l'historique ou le référentiel du projet, pas ce qui oriente une décision.
# Ils vivent dans `docs/`, lus à la demande. Comparaison sur le titre
# normalisé (sans accents ni casse) pour rester tolérante aux variantes.
SECTIONS_HORS_CONTEXTE = {
    "glossaire": "glossaire",
    "etat d'avancement": "état d'avancement",
    "avancement": "état d'avancement",
    "roadmap": "roadmap / backlog",
    "backlog": "roadmap / backlog",
    "historique": "historique",
    "journal de session": "comptes rendus de session",
    "journaux de session": "comptes rendus de session",
    "comptes rendus": "comptes rendus de session",
    "registre des risques": "registre des risques",
    "suivi des revues": "suivi des revues",
}


def _sans_accent(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def hygiene_claude_md():
    """Retourne les avertissements d'hygiène sur le CLAUDE.md, ou [] si sain."""
    cm = pathlib.Path("CLAUDE.md")
    if not cm.is_file():
        return []
    texte = cm.read_text(encoding="utf-8", errors="ignore")
    lignes = texte.splitlines()
    alertes = []
    if len(lignes) > SEUIL_LIGNES:
        alertes.append(
            f"il fait {len(lignes)} lignes (> {SEUIL_LIGNES}) et il est lu en "
            f"entier à chaque session")
    trouvees = []
    for ligne in lignes:
        if not ligne.startswith("#"):
            continue
        # « ## 8. Glossaire interne (à enrichir) » -> « glossaire interne »
        titre = _sans_accent(ligne.lstrip("# ").strip()).lower()
        titre = re.sub(r"^\d+[.)]?\s*", "", titre)
        titre = re.sub(r"\(.*?\)", "", titre).strip(" :-")
        for motif, etiquette in SECTIONS_HORS_CONTEXTE.items():
            if titre.startswith(motif) and etiquette not in trouvees:
                trouvees.append(etiquette)
    if trouvees:
        alertes.append("il porte des sections qui vivent dans `docs/` : "
                       + ", ".join(trouvees))
    return alertes


def main():
    lignes = [
        f"[geoid] Plugin d'équipe geoid v{version_plugin()} actif "
        f"(agents, skills et commandes préfixés `geoid:`)."
    ]
    ouverts = adr_ouverts()
    if ouverts:
        lignes.append("Points à arbitrer encore ouverts dans le CLAUDE.md du projet :")
        lignes.extend(f"  - {o}" for o in ouverts)
    alertes = hygiene_claude_md()
    if alertes:
        lignes.append("[geoid] Hygiène du CLAUDE.md — " + " ; ".join(alertes)
                      + ". Proposer un dégraissage vers `docs/` en fin de séance "
                        "(`/geoid:cloturer-session`, étape 2 bis) ; ne rien "
                        "déplacer sans l'accord de l'utilisateur.")
    sys.stdout.write("\n".join(lignes) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
