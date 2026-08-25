#!/usr/bin/env python3
"""Generer une page de suivi de projet HTML, autoportante et interactive.

Outillage d'equipe GeoID : convertit le `docs/suivi-projet.md` d'un projet
(modele `templates/suivi-projet.template.md`) en une page unique — CSS, JS et
donnees inlines, aucune connexion requise a l'ouverture.

La page apporte ce qu'un Markdown rendu ne donne pas pour arbitrer :
    - recherche plein texte, filtres par statut / priorite / intervenant,
      tri par colonne, le tout combinable ;
    - compteurs et jauge d'avancement recalcules a chaque filtrage ;
    - vue « Increments » : une carte par increment, avec son avancement ;
    - journal des decisions en chronologie depliable.

Le Markdown reste la SOURCE DE VERITE : cette page est une vue, regeneree a
la demande. Ne pas la versionner (cf. `.gitignore`).

Usage :
    python3 scripts/generer_suivi_html.py \
        --source docs/suivi-projet.md --output docs/suivi-projet.html

Arguments :
    --source    (requis) le suivi Markdown a rendre.
    --output    (requis) la page HTML a produire.
    --titre     nom de la page (defaut : le premier H1 du source).
    --note      bandeau d'avertissement en tete de page (HTML accepte).
    --fragment  sort sans <html>/<head>/<body>, pour une publication qui
                fournit elle-meme l'enveloppe.

Lecture des tableaux : les colonnes sont reperees par le NOM de leur
en-tete, pas par leur position. La colonne `Increment` est donc facultative
(un suivi anterieur au gabarit 1.1.0 se rend a l'identique, sans vue
Increments) et l'ordre des colonnes est indifferent.

Prerequis : pip install markdown   (seule dependance tierce ; reste = stdlib).

Le script est idempotent : reexecutable sans effet de bord.
"""
import argparse
import json
import pathlib
import re
import sys
import unicodedata

try:
    import markdown
except ImportError:
    sys.exit("Erreur : la bibliotheque 'markdown' est introuvable.\n"
             "Installer avec : pip install markdown")

MD = markdown.Markdown(extensions=["tables", "fenced_code"])

# ── Vocabulaire de pilotage ────────────────────────────────────────────────
# Palette de STATUT (reservee : jamais reutilisee comme couleur de serie).
# Chaque pastille porte toujours son libelle -> la couleur est redondante,
# jamais le seul porteur d'information.
STATUTS = [
    ("bloque",  "Bloqué",  "#E8402F", "#FCE7E4", "#8F2318"),
    ("encours", "En cours", "#0E86AC", "#E2F1F7", "#0A5A73"),
    ("enrevue", "En revue", "#C07500", "#FBEEDC", "#7A4A00"),
    ("afaire",  "À faire",  "#7A8C8C", "#EDF1F1", "#445656"),
    ("termine", "Terminé",  "#10855F", "#E3F3EC", "#0B5A42"),
]
CLE_STATUT = {lib: cle for cle, lib, *_ in STATUTS}
# Vocabulaire du registre des risques, ramene aux memes cles.
ALIAS = {"Fermé": "termine", "Ouvert": "afaire",
         "En voie de fermeture": "enrevue", "Clos": "termine",
         "Clôturé": "termine", "Cloturé": "termine"}
# Tout statut hors vocabulaire tombe dans un bac VISIBLE plutot que d'etre
# range de force : la derive de registre doit se voir, pas se dissimuler.
HORS = ("autre", "Hors vocabulaire", "#8B7BA8", "#EFEAF5", "#4E3F66")

ORDRE_PRIO = {"Critique": 0, "Haute": 1, "Moyenne": 2, "Basse": 3, "": 9}
ORDRE_STATUT = {cle: i for i, (cle, *_) in enumerate(STATUTS)}
NIVEAUX = {"Élevée": "haut", "Élevé": "haut", "Moyenne": "moyen",
           "Moyen": "moyen", "Faible": "bas", "Basse": "bas"}


def inline(md_text):
    """Rend le markdown d'une cellule, sans le <p> englobant."""
    MD.reset()
    html = MD.convert(md_text.strip())
    return re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S).strip()


def bloc(md_text):
    """Rend une section entiere. NE PAS ecrire `MD.reset() or MD.convert(...)` :
    reset() renvoie l'objet Markdown, qui est vrai — le `or` court-circuite et
    la conversion n'a jamais lieu."""
    MD.reset()
    return MD.convert(md_text.strip())


def decouper(md_text):
    """Retourne {numero_section: (titre, corps)}."""
    parts = re.split(r"^## (.+)$", md_text, flags=re.M)
    sections = {}
    for titre, corps in zip(parts[1::2], parts[2::2]):
        num = re.match(r"\s*(\d+)", titre)
        sections[num.group(1) if num else titre] = (titre.strip(), corps)
    return sections


def clef(entete):
    """« Responsable / agent » -> « responsable » : on compare sur le radical."""
    txt = unicodedata.normalize("NFD", entete.lower())
    return "".join(c for c in txt if c.isalnum())


def lire_table(corps, prefixe):
    """Lignes `| PREFIXE-nn | ... |`, indexees par NOM de colonne.

    Lire par en-tete et non par position rend la colonne `Jalon` optionnelle
    et l'ordre des colonnes indifferent : un projet qui n'a pas encore
    migre son suivi continue de fonctionner, sans vue sprint.
    """
    entetes, lignes = [], []
    for ligne in corps.splitlines():
        if not ligne.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ligne.strip().strip("|").split("|")]
        # Les identifiants peuvent porter un suffixe (S-25b apres une
        # collision d'ID). Et seule une ligne dont la 1re colonne est « ID »
        # est un en-tete : sinon une ligne de donnees non reconnue serait
        # prise pour un en-tete et decalerait toutes les colonnes suivantes.
        if re.fullmatch(rf"{prefixe}-\d+[a-z]?", cells[0], re.I):
            row = {clef(e): v for e, v in zip(entetes, cells)}
            row["_cells"] = cells
            lignes.append(row)
        elif clef(cells[0]) == "id":
            entetes = cells
    return lignes


def champ(row, *radicaux, position=None, defaut=""):
    """Valeur d'une colonne designee par le radical de son en-tete."""
    for k, v in row.items():
        if k != "_cells" and any(k.startswith(r) for r in radicaux):
            return v
    if position is not None and len(row["_cells"]) > position:
        return row["_cells"][position]
    return defaut


def statut_de(txt):
    """(cle, libelle, complement) — gere « Terminé (2026-07-30) — … »."""
    nu = txt.lstrip("*").strip()          # « **Partiellement terminé** … »
    for lib in list(CLE_STATUT) + list(ALIAS):
        if nu.startswith(lib):
            cle = CLE_STATUT.get(lib) or ALIAS[lib]
            return cle, lib, nu[len(lib):].strip(" *—-")
    # Hors vocabulaire : on garde le libelle tel qu'il est ecrit, on ne devine pas.
    coupe = re.split(r"[(—]|\*\*", nu, maxsplit=1)
    return "autre", (coupe[0].strip(" *") or "—"), nu[len(coupe[0]):].strip(" *—-")


def parser(md_text):
    # Les sections sont reperees par leur CONTENU, pas par leur numero : le
    # gabarit 1.1.0 a insere « Increments metier » en tete, decalant tout le
    # reste d'un rang. Un dispatch par numero cassait a chaque evolution du
    # gabarit, et silencieusement (zero tache lue, page vide mais valide).
    sections = decouper(md_text)
    corps_de = {}
    for titre_sec, corps in sections.values():
        for prefixe in ("S", "R", "INC"):
            if prefixe not in corps_de and lire_table(corps, prefixe):
                corps_de[prefixe] = corps
        bas = titre_sec.lower()
        if "revue" in bas:
            corps_de["revues"] = corps
        elif "arbitrer" in bas:
            corps_de["arbitrer"] = corps
        elif "journal" in bas or "decision" in clef(titre_sec):
            corps_de["journal"] = corps

    taches, risques, increments = [], [], []

    for r in lire_table(corps_de.get("INC", ""), "INC"):
        increments.append({
            "id": r["_cells"][0],
            "titre": inline(champ(r, "increment", "titre", position=1)),
            "valeur": inline(champ(r, "valeur", defaut="")),
            "recette": inline(champ(r, "critere", "recette", defaut="")),
            "statut": statut_de(champ(r, "statut", position=-1))[1],
        })

    for r in lire_table(corps_de.get("S", ""), "S"):
        if len(r["_cells"]) < 6:
            continue
        tache = champ(r, "tache", "titre", position=1)
        cle, lib, comp = statut_de(champ(r, "statut", position=-2))
        jal = champ(r, "increment", "jalon", "sprint", "lot", "iteration").strip(" *")
        taches.append({
            "id": r["_cells"][0], "titre": inline(tache), "brut": tache,
            "jalon": jal if jal and jal != "—" else "",
            "prio": champ(r, "priorite", defaut="—") or "—",
            "agent": champ(r, "responsable", "agent", "porteur", defaut="—") or "—",
            "statut": cle, "statutLib": lib, "note": inline(comp) if comp else "",
            "echeance": champ(r, "echeance", "date", "cible", position=-1) or "—",
        })

    for r in lire_table(corps_de.get("R", ""), "R"):
        c = r["_cells"]
        if len(c) < 6:
            continue
        proba = champ(r, "probabilite", position=2)
        impact = champ(r, "impact", position=3)
        cle, lib, comp = statut_de(champ(r, "statut", position=-1))
        risques.append({
            "id": c[0], "titre": inline(champ(r, "risque", position=1)),
            "brut": champ(r, "risque", position=1),
            "proba": proba, "probaN": NIVEAUX.get(proba, "moyen"),
            "impact": impact, "impactN": NIVEAUX.get(impact, "moyen"),
            "mitigation": inline(champ(r, "mitigation", position=4)),
            "statut": cle, "statutLib": lib + (f" — {comp}" if comp else ""),
        })

    journal = []
    for ligne in corps_de.get("journal", "").splitlines():
        c = [x.strip() for x in ligne.strip().strip("|").split("|")]
        if len(c) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}$", c[0]):
            journal.append({"date": c[0], "sujet": inline(c[1]),
                            "decision": inline(c[2]), "pourquoi": inline(c[3]),
                            "brut": f"{c[0]} {c[1]} {c[2]} {c[3]}"})

    titre = re.search(r"^# (.+)$", md_text, flags=re.M)
    return {
        "titre": titre.group(1).strip() if titre else "Suivi du projet",
        "taches": taches, "risques": risques, "journal": journal,
        "increments": increments,
        "revues": bloc(corps_de.get("revues", "")),
        "arbitrer": bloc(corps_de.get("arbitrer", "")),
    }


# ── Gabarit ────────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --fond:#FBFCFC; --carte:#FFFFFF; --bord:#E4EAEA; --bord-fort:#CFDADA;
  --zebre:var(--zebre); --entete:var(--entete); --filet:var(--filet);
  --ink:#12292B; --ink-2:#4A5F60; --ink-3:#7D9091;
  --vert:#00373D; --canard:#005F5A; --corail:#E8402F; --peche:#FFE6CD;
  --sur-vert:#FFFFFF;
  /* Bases de melange des pastilles : un seul jeu de regles, deux rendus. */
  --mel-fond:#FFFFFF; --force-fond:13%;
  --mel-txt:#0B1416;  --force-txt:72%;
  --ombre:0 1px 2px rgba(0,55,61,.05);
  --r:10px;
  --f-titre:'Segoe UI Variable Display','Archivo','Segoe UI',system-ui,sans-serif;
  --f:'Segoe UI','Source Sans 3',system-ui,-apple-system,sans-serif;
  --f-mono:'Cascadia Code','IBM Plex Mono',Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --fond:#0C1618; --carte:#111F21; --bord:#1E3033; --bord-fort:#2B4145;
    --zebre:#142325; --entete:#152628; --filet:#1A2C2F;
    --ink:#E6EDED; --ink-2:#A8BDBD; --ink-3:#7B9394;
    --vert:#D8E6E5; --canard:#6FC3BC; --peche:#4A3524; --sur-vert:#0C1618;
    --mel-fond:#0C1618; --force-fond:26%;
    --mel-txt:#FFFFFF;  --force-txt:74%;
    --ombre:0 1px 2px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --fond:#0C1618; --carte:#111F21; --bord:#1E3033; --bord-fort:#2B4145;
  --zebre:#142325; --entete:#152628; --filet:#1A2C2F;
  --ink:#E6EDED; --ink-2:#A8BDBD; --ink-3:#7B9394;
  --vert:#D8E6E5; --canard:#6FC3BC; --peche:#4A3524; --sur-vert:#0C1618;
  --mel-fond:#0C1618; --force-fond:26%;
  --mel-txt:#FFFFFF;  --force-txt:74%;
  --ombre:0 1px 2px rgba(0,0,0,.35);
}
/* Une seule regle de pastille ; chaque variante ne pose que sa teinte. */
.b,.p,.n{background:color-mix(in srgb, var(--st) var(--force-fond), var(--mel-fond));
  color:color-mix(in srgb, var(--st) var(--force-txt), var(--mel-txt))}

body{margin:0;background:var(--fond);color:var(--ink);font-family:var(--f);
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px 72px}
a{color:var(--canard)} code{font-family:var(--f-mono);
  font-size:.87em;background:var(--filet);padding:.1em .35em;border-radius:4px}

/* En-tete : un filet, pas un aplat */
header.top{position:sticky;top:0;z-index:30;background:color-mix(in srgb, var(--fond) 93%, transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--bord)}
.top-in{max-width:1180px;margin:0 auto;padding:14px 24px;display:flex;
  align-items:baseline;gap:20px;flex-wrap:wrap}
.top h1{font-family:var(--f-titre);font-size:1.06rem;margin:0;font-weight:650;letter-spacing:-.01em}
.top h1 .pt{color:var(--corail)}
nav.sections{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
nav.sections a{padding:5px 11px;border-radius:99px;font-size:.83rem;
  text-decoration:none;color:var(--ink-2)}
nav.sections a:hover{background:var(--filet);color:var(--vert)}

h2.sec{font-family:var(--f-titre);font-size:1.22rem;margin:44px 0 4px;letter-spacing:-.01em;font-weight:650}
h2.sec .n{color:var(--ink-3);font-weight:400;margin-right:.45em}
.sec-note{color:var(--ink-2);font-size:.88rem;margin:0 0 18px}

/* KPI : tuiles claires, chiffre en vedette */
.kpis{display:grid;gap:12px;margin:26px 0 18px;
  grid-template-columns:repeat(auto-fit,minmax(132px,1fr))}
.kpi{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);
  padding:14px 16px;box-shadow:var(--ombre);cursor:pointer;text-align:left;
  font:inherit;transition:border-color .12s,transform .12s}
.kpi:hover{border-color:var(--bord-fort);transform:translateY(-1px)}
.kpi[aria-pressed=true]{border-color:var(--vert);box-shadow:0 0 0 2px rgba(0,55,61,.09)}
.kpi .v{font-family:var(--f-titre);font-variant-numeric:tabular-nums;font-size:1.9rem;font-weight:680;line-height:1;letter-spacing:-.02em}
.kpi .l{display:flex;align-items:center;gap:6px;margin-top:7px;
  font-size:.79rem;color:var(--ink-2)}
.pastille{width:8px;height:8px;border-radius:50%;flex:none}

/* Jauge segmentee : 2px de respiration entre segments, extremites arrondies */
.jauge{display:flex;gap:2px;height:10px;margin:6px 0 10px}
.jauge div{border-radius:2px;transition:flex-grow .25s}
.jauge div:first-child{border-radius:5px 2px 2px 5px}
.jauge div:last-child{border-radius:2px 5px 5px 2px}
.jauge-lib{font-size:.83rem;color:var(--ink-2);margin-bottom:26px}
.jauge-lib b{color:var(--ink);font-weight:650}

/* Barre d'outils */
.outils{position:sticky;top:53px;z-index:20;background:var(--fond);
  padding:12px 0 12px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  border-bottom:1px solid var(--bord);margin-bottom:2px}
.rech{position:relative;flex:1;min-width:210px;max-width:330px}
.rech input{width:100%;padding:8px 30px 8px 32px;border:1px solid var(--bord-fort);
  border-radius:8px;font:inherit;font-size:.88rem;background:var(--carte);color:var(--ink)}
.rech input:focus{outline:2px solid rgba(0,95,90,.35);outline-offset:-1px;border-color:var(--canard)}
.rech .loupe{position:absolute;left:10px;top:50%;transform:translateY(-50%);
  color:var(--ink-3);font-size:.9rem}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--bord-fort);background:var(--carte);border-radius:99px;
  padding:5px 11px;font:inherit;font-size:.81rem;color:var(--ink-2);cursor:pointer;
  display:inline-flex;align-items:center;gap:6px}
.chip:hover{border-color:var(--canard)}
.chip[aria-pressed=true]{background:var(--vert);border-color:var(--vert);color:var(--sur-vert)}
.chip[aria-pressed=true] .pastille{box-shadow:0 0 0 1.5px rgba(255,255,255,.5)}
select{padding:7px 9px;border:1px solid var(--bord-fort);border-radius:8px;
  font:inherit;font-size:.83rem;background:var(--carte);color:var(--ink-2)}
.compte{margin-left:auto;font-size:.83rem;color:var(--ink-3);white-space:nowrap}
.raz{background:none;border:none;color:var(--canard);font:inherit;font-size:.83rem;
  cursor:pointer;text-decoration:underline;padding:4px}
.raz[hidden]{display:none}

/* Tableaux */
table{width:100%;border-collapse:collapse;font-size:.88rem;background:var(--carte);
  border:1px solid var(--bord);border-radius:var(--r);overflow:hidden}
thead th{text-align:left;font-weight:600;font-size:.76rem;text-transform:uppercase;
  letter-spacing:.05em;color:var(--ink-3);padding:11px 14px;
  border-bottom:1px solid var(--bord);white-space:nowrap;background:var(--entete)}
th.tri{cursor:pointer;user-select:none}
th.tri:hover{color:var(--vert)}
th.tri::after{content:'↕';opacity:.3;margin-left:5px;font-size:.9em}
th.tri[data-sens='1']::after{content:'↑';opacity:.9}
th.tri[data-sens='-1']::after{content:'↓';opacity:.9}
tbody td{padding:11px 14px;border-bottom:1px solid var(--filet);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:var(--zebre)}
td.id{font-family:var(--f-mono);font-size:.82rem;
  color:var(--ink-3);white-space:nowrap}
td.tache{max-width:520px}
.note{color:var(--ink-2);font-size:.85rem;margin-top:5px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.note.ouvert{-webkit-line-clamp:unset}
.plus{background:none;border:none;color:var(--canard);font:inherit;font-size:.79rem;
  cursor:pointer;padding:3px 0;text-decoration:underline}
.vide{padding:38px;text-align:center;color:var(--ink-3);font-size:.9rem;
  background:var(--carte);border:1px dashed var(--bord-fort);border-radius:var(--r)}

/* Pastilles de statut : couleur + libelle, jamais la couleur seule */
.b{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:99px;
  font-size:.78rem;font-weight:600;white-space:nowrap}
.n{display:inline-block;padding:2px 8px;border-radius:5px;font-size:.77rem;font-weight:600}

.p{display:inline-block;padding:2px 9px;border-radius:99px;font-size:.77rem;font-weight:600}


/* Journal : chronologie */
.journal{border-left:2px solid var(--bord);margin:18px 0 0;padding-left:0}
.jour{position:relative;padding:0 0 4px 26px}
.jour::before{content:'';position:absolute;left:-5px;top:15px;width:8px;height:8px;
  border-radius:50%;background:var(--canard);border:2px solid var(--fond)}
.jour summary{cursor:pointer;padding:10px 0;list-style:none;display:flex;gap:12px;
  align-items:baseline;flex-wrap:wrap}
.jour summary::-webkit-details-marker{display:none}
.jour summary:hover .sujet{color:var(--canard)}
.jour .date{font-family:var(--f-mono);font-size:.79rem;
  color:var(--ink-3);white-space:nowrap}
.jour .sujet{font-weight:600;font-size:.92rem}
.jour .corps{padding:2px 0 16px;font-size:.88rem;color:var(--ink-2);max-width:840px}
.jour .corps .quoi{color:var(--ink);margin-bottom:8px}
.jour .corps .pq{border-left:3px solid var(--peche);padding-left:12px}

.panneau{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);
  padding:6px 22px;margin-top:18px;box-shadow:var(--ombre);font-size:.91rem}
.panneau blockquote{background:var(--filet);border-left:3px solid var(--peche);
  margin:14px 0;padding:10px 14px;border-radius:0 6px 6px 0;font-size:.88rem}
.panneau table{font-size:.85rem;margin:12px 0}
.avis{background:color-mix(in srgb, var(--peche) 55%, var(--carte));
  border:1px solid color-mix(in srgb, var(--corail) 30%, var(--bord));
  border-radius:var(--r);padding:13px 17px;margin:22px 0 0;font-size:.86rem;
  color:var(--ink-2);line-height:1.5}
.avis b{color:var(--ink)}
footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--bord);
  font-size:.8rem;color:var(--ink-3)}

/* Bascule de vue */
.vue{display:inline-flex;border:1px solid var(--bord-fort);border-radius:8px;
  overflow:hidden;background:var(--carte)}
.vue button{border:none;background:none;padding:7px 14px;font:inherit;
  font-size:.83rem;color:var(--ink-2);cursor:pointer}
.vue button+button{border-left:1px solid var(--bord)}
.vue button[aria-pressed=true]{background:var(--vert);color:var(--sur-vert)}
[hidden]{display:none!important}

/* Board par jalon */
.board{display:grid;gap:14px;margin-top:4px;
  grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.sprint{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);
  box-shadow:var(--ombre);padding:16px 18px 8px;display:flex;flex-direction:column}
.sprint.encours{border-color:#0E86AC;box-shadow:0 0 0 2px rgba(14,134,172,.10)}
.sprint.rien{opacity:.55}
.sprint-t{display:flex;align-items:center;gap:9px;margin-bottom:3px;flex-wrap:wrap}
.sprint-t h3{font-family:var(--f-titre);margin:0;font-size:1.02rem;font-weight:650;letter-spacing:-.01em}
.etiq{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600;
  padding:2px 8px;border-radius:99px}
.e-encours{--st:#0E86AC} .e-livre{--st:#10855F}
.e-avenir{--st:#7A8C8C} .e-non{--st:#8B7BA8}
.etiq{background:color-mix(in srgb, var(--st) var(--force-fond), var(--mel-fond));
  color:color-mix(in srgb, var(--st) var(--force-txt), var(--mel-txt))}
.n-haut{--st:#E8402F} .n-moyen{--st:#C07500} .n-bas{--st:#7A8C8C}
.p-Critique{--st:#E8402F} .p-Haute{--st:#D4553F} .p-Moyenne{--st:#C07500}
.p-Basse{--st:#7A8C8C} .p-nc{--st:#7A8C8C}
.sprint-m{font-size:.81rem;color:var(--ink-3);margin-bottom:10px}
.sprint .jauge{height:8px;margin:0 0 12px}
.tl{list-style:none;margin:0;padding:0;flex:1}
.tl li{display:flex;gap:9px;align-items:flex-start;padding:8px 0;
  border-top:1px solid var(--filet);font-size:.86rem}
.tl li:first-child{border-top:none}
.tl .pp{width:7px;height:7px;border-radius:50%;flex:none;margin-top:6px}
.tl .tid{font-family:var(--f-mono);font-size:.78rem;
  color:var(--ink-3);white-space:nowrap}
.tl .tt{flex:1;line-height:1.4}
.tl .tp{font-size:.72rem;color:var(--ink-3);white-space:nowrap}
.tl .fini .tt{color:var(--ink-3)}

@media(max-width:760px){
  .outils{position:static} nav.sections{width:100%;margin:6px 0 0}
  td.tache{max-width:none} .compte{margin-left:0;width:100%}
}
@media print{
  header.top,.outils,nav.sections,.plus{display:none}
  body{background:#fff} .note{-webkit-line-clamp:unset}
  details{open:true} .jour .corps{display:block!important}
}
"""

JS = """
const D = DONNEES;
const S = {q:'', statuts:new Set(), prios:new Set(), jalons:new Set(),
           agent:'', tri:null, sens:1, vue:'liste'};
const $ = s => document.querySelector(s);
const norm = t => (t||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');

/* ---- Filtrage : une seule source de verite, tout en decoule ---- */
function filtrer(){
  const q = norm(S.q);
  return D.taches.filter(t =>
    (!S.statuts.size || S.statuts.has(t.statut)) &&
    (!S.prios.size   || S.prios.has(t.prio)) &&
    (!S.agent        || norm(t.agent).includes(norm(S.agent))) &&
    (!S.jalons.size  || S.jalons.has(t.jalon)) &&
    (!q || norm(t.id+' '+t.brut+' '+t.agent+' '+t.statutLib+' '+t.note+' '+t.jalon).includes(q))
  );
}

function trier(l){
  if(!S.tri) return l;
  const cl = {prio:t=>ORDRE_PRIO[t.prio] ?? 9, statut:t=>ORDRE_STATUT[t.statut],
              id:t=>+t.id.replace(/\\D/g,''), agent:t=>norm(t.agent),
              jalon:t=>t.jalon ? JALONS.indexOf(t.jalon) : 999,
              echeance:t=>t.echeance, titre:t=>norm(t.brut)}[S.tri];
  return [...l].sort((a,b)=>{const x=cl(a),y=cl(b);
    return (x>y?1:x<y?-1:0)*S.sens;});
}

/* ---- Rendu ---- */
const pastille = c => `<span class="pastille" style="background:${COULEURS[c]}"></span>`;
function badge(t){
  return `<span class="b s-${t.statut}">${pastille(t.statut)}${t.statutLib}</span>`;
}

function rendre(){
  const l = trier(filtrer());
  $('#corps').innerHTML = l.length ? l.map(t=>`
    <tr>
      <td class="id">${t.id}</td>
      <td class="tache"><div>${t.titre}</div>${
        t.note ? `<div class="note" id="n${t.id}">${t.note}</div>
                  <button class="plus" data-n="n${t.id}">détail ▾</button>` : ''}</td>
      ${A_JALONS ? `<td style="white-space:nowrap">${t.jalon
        ? t.jalon : '<span style="color:var(--ink-3)">—</span>'}</td>` : ''}
      <td><span class="p p-${/^[A-Za-zÀ-ÿ]+$/.test(t.prio)?t.prio:'nc'}">${t.prio}</span></td>
      <td>${t.agent}</td>
      <td>${badge(t)}</td>
      <td style="white-space:nowrap;color:var(--ink-2)">${t.echeance}</td>
    </tr>`).join('')
    : `<tr><td colspan="${A_JALONS?7:6}"><div class="vide">Aucune tâche ne correspond à ces filtres.</div></td></tr>`;

  $('#compte').textContent = l.length === D.taches.length
    ? `${D.taches.length} tâches`
    : `${l.length} sur ${D.taches.length} tâches`;
  majKpis(l);
  if(A_JALONS) rendreBoard(l);
  const actif = S.q || S.statuts.size || S.prios.size || S.agent;
  $('#raz').hidden = !actif;
}

/* Un jalon se decrit par ce qu'il contient, pas par une date declaree :
   tout termine = livre, au moins une en cours = en cours, sinon a venir. */
function etatJalon(ts){
  if(!ts.length) return ['e-avenir','Vide'];
  if(ts.every(t=>t.statut==='termine')) return ['e-livre','Livré'];
  // Demarre = au moins une tache close OU en cours. Un jalon a 4/5 termine
  // n'est pas « a venir » : ne compter que les « En cours » le classait mal.
  if(ts.some(t=>t.statut==='encours'||t.statut==='termine')) return ['e-encours','En cours'];
  return ['e-avenir','À venir'];
}

function rendreBoard(l){
  const groupes = [...JALONS, ''];
  document.querySelector('#vue-sprint').innerHTML = groupes.map(j=>{
    const tous = D.taches.filter(t=>t.jalon===j);
    if(!tous.length) return '';
    const ts = l.filter(t=>t.jalon===j);
    const [cl,lib] = j === '' ? ['e-non','Non planifié'] : etatJalon(tous);
    const n = {}; STATUTS.forEach(s=>n[s[0]]=0); ts.forEach(t=>n[t.statut]++);
    const fini = n.termine, tot = ts.length;
    const pct = tot ? Math.round(100*fini/tot) : 0;
    const jauge = tot ? STATUTS.map(([c,lb])=> n[c]
        ? `<div style="flex:${n[c]};background:${COULEURS[c]}" title="${lb} : ${n[c]}"></div>`
        : '').join('') : '<div style="flex:1;background:#EDF1F1"></div>';
    const lignes = ts.length ? ts.map(t=>`
        <li class="${t.statut==='termine'?'fini':''}">
          <span class="pp" style="background:${COULEURS[t.statut]}" title="${t.statutLib}"></span>
          <span class="tid">${t.id}</span><span class="tt">${t.titre}</span>
          <span class="tp">${t.prio}</span></li>`).join('')
      : `<li style="color:var(--ink-3)">Aucune tâche pour ces filtres.</li>`;
    return `<section class="sprint ${cl==='e-encours'?'encours':''} ${ts.length?'':'rien'}">
      <div class="sprint-t"><h3>${j || 'Non planifié'}</h3>
        <span class="etiq ${cl}">${lib}</span></div>
      <div class="sprint-m">${tot} tâche${tot>1?'s':''}${
        tot ? ` · ${fini} terminée${fini>1?'s':''} · ${pct} %` : ''}${
        ts.length !== tous.length ? ` <span style="opacity:.7">(sur ${tous.length})</span>` : ''}</div>
      <div class="jauge">${jauge}</div><ul class="tl">${lignes}</ul></section>`;
  }).join('');
}

/* Les KPI et la jauge suivent le filtre : ils decrivent ce qu'on regarde. */
function majKpis(l){
  const n = {}; STATUTS.forEach(s => n[s[0]] = 0);
  l.forEach(t => n[t.statut]++);
  STATUTS.forEach(([c])=>{
    $(`#k-${c} .v`).textContent = n[c];
    $(`#k-${c}`).style.opacity = n[c] ? 1 : .45;
  });
  const tot = l.length || 1, pct = Math.round(100*n.termine/tot);
  $('#jauge').innerHTML = STATUTS.map(([c,lib])=> n[c]
    ? `<div style="flex:${n[c]};background:${COULEURS[c]}" title="${lib} : ${n[c]} (${Math.round(100*n[c]/tot)} %)"></div>`
    : '').join('');
  $('#pct').innerHTML = `<b>${pct} %</b> des tâches affichées sont terminées`
    + (n.bloque ? ` · <b style="color:var(--corail)">${n.bloque} bloquée${n.bloque>1?'s':''}</b>` : '');
}

/* ---- Branchements ---- */
function bascule(set, val, el){
  set.has(val) ? set.delete(val) : set.add(val);
  el.setAttribute('aria-pressed', set.has(val));
  rendre();
}
document.addEventListener('click', e=>{
  const k = e.target.closest('.kpi');       if(k) return bascule(S.statuts, k.dataset.s, k);
  const c = e.target.closest('.chip');      if(c) return bascule(S.prios, c.dataset.p, c);
  const p = e.target.closest('.plus');
  if(p){ const n = $('#'+p.dataset.n); n.classList.toggle('ouvert');
         p.textContent = n.classList.contains('ouvert') ? 'réduire ▴' : 'détail ▾'; return; }
  const th = e.target.closest('th.tri');
  if(th){ S.sens = S.tri===th.dataset.k ? -S.sens : 1; S.tri = th.dataset.k;
          document.querySelectorAll('th.tri').forEach(x=>x.removeAttribute('data-sens'));
          th.dataset.sens = S.sens; rendre(); }
});
if(A_JALONS){
  const bascVue = v => {
    S.vue = v;
    $('#v-liste').setAttribute('aria-pressed', v==='liste');
    $('#v-sprint').setAttribute('aria-pressed', v==='sprint');
    $('#vue-liste').hidden = v!=='liste';
    $('#vue-sprint').hidden = v!=='sprint';
  };
  $('#v-liste').addEventListener('click', ()=>bascVue('liste'));
  $('#v-sprint').addEventListener('click', ()=>bascVue('sprint'));
}
$('#q').addEventListener('input', e=>{ S.q = e.target.value; rendre(); });
$('#agent').addEventListener('change', e=>{ S.agent = e.target.value; rendre(); });
$('#raz').addEventListener('click', ()=>{
  S.q=''; S.agent=''; S.statuts.clear(); S.prios.clear(); S.tri=null; S.sens=1;
  $('#q').value=''; $('#agent').value='';
  document.querySelectorAll('[aria-pressed]').forEach(x=>x.setAttribute('aria-pressed',false));
  document.querySelectorAll('th.tri').forEach(x=>x.removeAttribute('data-sens'));
  rendre();
});
/* Raccourci : « / » place le curseur dans la recherche. */
document.addEventListener('keydown', e=>{
  if(e.key==='/' && e.target.tagName!=='INPUT'){ e.preventDefault(); $('#q').focus(); }
  if(e.key==='Escape' && e.target.id==='q'){ S.q=''; e.target.value=''; rendre(); }
});
rendre();
"""


def page(d, source, titre=None, note=None, fragment=False):
    # Le bac « hors vocabulaire » n'apparait que s'il est peuple.
    liste = list(STATUTS)
    if any(x["statut"] == "autre" for x in d["taches"] + d["risques"]):
        liste.append(HORS)
    couleurs = {c: p for c, lib, p, f, t in liste}
    fonds = {c: [f, t] for c, lib, p, f, t in liste}
    ordre = {c: i for i, (c, *_) in enumerate(liste)}
    css_statuts = "\n".join(f".s-{c}{{--st:{pt}}}" for c, lib, pt, *_ in liste)
    # Ordre des jalons : numerique quand ils ressemblent a des versions
    # (1.2.0 apres 1.10.0 serait faux en tri alphabetique), le reste ensuite,
    # « Non planifie » toujours en dernier.
    def rang(j):
        m = re.fullmatch(r"[vV]?(\d+(?:\.\d+)*)", j)
        return (0, [int(x) for x in m.group(1).split(".")], "") if m else (1, [], j.lower())

    jalons = sorted({t["jalon"] for t in d["taches"] if t["jalon"]}, key=rang)
    a_jalons = bool(jalons)
    vue = ('<div class="vue" role="group" aria-label="Choix de vue">'
           '<button id="v-liste" aria-pressed="true">Liste</button>'
           '<button id="v-sprint" aria-pressed="false">Incréments</button></div>'
           ) if a_jalons else ""
    th_jalon = '<th class="tri" data-k="jalon">Jalon</th>' if a_jalons else ""

    atomes = set()
    for t in d["taches"]:
        for a in re.split(r"[/+]", t["agent"]):
            if a.strip() and a.strip() != "—":
                atomes.add(a.strip())
    agents = sorted(atomes, key=str.lower)
    prios = [p for p in ("Critique", "Haute", "Moyenne", "Basse")
             if any(t["prio"] == p for t in d["taches"])]

    kpis = "".join(
        f'<button class="kpi" id="k-{c}" data-s="{c}" aria-pressed="false" '
        f'title="Filtrer sur « {lib} »"><div class="v">0</div>'
        f'<div class="l"><span class="pastille" style="background:{pt}"></span>{lib}</div></button>'
        for c, lib, pt, f, t in liste)

    chips = "".join(
        f'<button class="chip" data-p="{p}" aria-pressed="false">{p}</button>'
        for p in prios)

    opts = "".join(f'<option value="{a}">{a}</option>' for a in agents)

    risques = "".join(f"""
      <tr><td class="id">{r['id']}</td>
        <td class="tache"><div>{r['titre']}</div>
          <div class="note" id="m{r['id']}">{r['mitigation']}</div>
          <button class="plus" data-n="m{r['id']}">détail ▾</button></td>
        <td><span class="n n-{r['probaN']}">{r['proba']}</span></td>
        <td><span class="n n-{r['impactN']}">{r['impact']}</span></td>
        <td><span class="b s-{r['statut']}">
          <span class="pastille" style="background:{couleurs[r['statut']]}"></span>{r['statutLib']}</span></td>
      </tr>""" for r in d["risques"])

    journal = "".join(f"""
      <details class="jour"><summary>
        <span class="date">{j['date']}</span><span class="sujet">{j['sujet']}</span></summary>
        <div class="corps"><div class="quoi">{j['decision']}</div>
          <div class="pq">{j['pourquoi']}</div></div></details>""" for j in d["journal"])

    donnees = json.dumps({"taches": d["taches"]}, ensure_ascii=False)

    avis = f'<div class="avis">{note}</div>' if note else ""
    tete = f"""<title>{titre or d['titre']}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}
{css_statuts}</style>"""

    corps_html = f"""
<header class="top"><div class="top-in">
  <h1>{d['titre']}<span class="pt"> ·</span></h1>
  <nav class="sections">
    <a href="#backlog">Backlog</a><a href="#risques">Risques</a>
    <a href="#journal">Journal</a><a href="#ouverts">Points ouverts</a>
  </nav></div></header>

<div class="wrap">
  {avis}
  <h2 class="sec" id="backlog"><span class="n">1</span>Roadmap / backlog</h2>
  <p class="sec-note">Cliquez un indicateur pour filtrer ; les compteurs et la
     jauge décrivent toujours ce qui est affiché.</p>
  <div class="kpis">{kpis}</div>
  <div class="jauge" id="jauge"></div>
  <div class="jauge-lib" id="pct"></div>

  <div class="outils">
    <div class="rech"><span class="loupe">⌕</span>
      <input id="q" type="search" placeholder="Rechercher   (touche /)" aria-label="Rechercher une tâche"></div>
    <div class="chips">{chips}</div>
    <select id="agent" aria-label="Filtrer par responsable">
      <option value="">Tous intervenants</option>{opts}</select>
    {vue}<button class="raz" id="raz" hidden>réinitialiser</button>
    <span class="compte" id="compte"></span>
  </div>

  <table id="vue-liste"><thead><tr>
    <th class="tri" data-k="id">ID</th><th class="tri" data-k="titre">Tâche</th>
    {th_jalon}<th class="tri" data-k="prio">Priorité</th>
    <th class="tri" data-k="agent">Responsable</th>
    <th class="tri" data-k="statut">Statut</th><th class="tri" data-k="echeance">Échéance</th>
  </tr></thead><tbody id="corps"></tbody></table>
  <div class="board" id="vue-sprint" hidden></div>

  <h2 class="sec" id="risques"><span class="n">2</span>Registre des risques</h2>
  <p class="sec-note">{len(d['risques'])} risques enregistrés.</p>
  <table><thead><tr><th>ID</th><th>Risque et mitigation</th>
    <th>Probabilité</th><th>Impact</th><th>Statut</th></tr></thead>
    <tbody>{risques}</tbody></table>

  <h2 class="sec" id="journal"><span class="n">4</span>Journal des décisions</h2>
  <p class="sec-note">{len(d['journal'])} décisions actées — dépliez pour la justification.</p>
  <div class="journal">{journal}</div>

  <h2 class="sec" id="ouverts"><span class="n">5</span>Points ouverts et revues</h2>
  <div class="panneau">{d['arbitrer']}</div>
  <div class="panneau">{d['revues']}</div>

  <footer>Généré depuis <code>{source}</code> — page autoportante, aucune
    connexion requise. La source de vérité reste le fichier Markdown versionné.</footer>
</div>

<script>
const DONNEES = {donnees};
const STATUTS = {json.dumps([[c, lib] for c, lib, *_ in liste], ensure_ascii=False)};
const COULEURS = {json.dumps(couleurs, ensure_ascii=False)};
const ORDRE_PRIO = {json.dumps(ORDRE_PRIO, ensure_ascii=False)};
const ORDRE_STATUT = {json.dumps(ordre, ensure_ascii=False)};
const JALONS = {json.dumps(jalons, ensure_ascii=False)};
const A_JALONS = {json.dumps(a_jalons)};
{JS}
</script>"""

    if fragment:      # publie en Artifact : l'enveloppe est fournie a la publication
        return tete + corps_html
    return ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            + tete + "</head><body>" + corps_html + "</body></html>")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--titre", default=None, help="Nom de la page (sinon : le H1 du source).")
    p.add_argument("--note", default=None, help="Bandeau d'avertissement en tete de page.")
    p.add_argument("--fragment", action="store_true",
                   help="Sort sans <html>/<head>/<body> (publication en Artifact).")
    a = p.parse_args()

    src = pathlib.Path(a.source)
    d = parser(src.read_text(encoding="utf-8"))
    pathlib.Path(a.output).write_text(
        page(d, src.name, a.titre, a.note, a.fragment), encoding="utf-8")
    print(f"Genere : {a.output}  ({len(d['taches'])} taches, "
          f"{len(d['risques'])} risques, {len(d['journal'])} decisions)")


if __name__ == "__main__":
    sys.exit(main())
