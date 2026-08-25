"""Tests du generateur de page de suivi (scripts/generer_suivi_html.py).

Stdlib uniquement, sans framework. Si la dependance tierce « markdown » est
absente, le test AFFICHE « SKIP » et sort en code 0 (meme convention que
test_generer_doc_html.py : ne pas echouer faute du paquet optionnel).

Lancer : python3 tests/test_generer_suivi_html.py
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RACINE / "scripts" / "generer_suivi_html.py"

# Fixture : le gabarit livre en 1.1.0 (colonne « Increment »), avec trois
# pieges volontaires — un statut hors vocabulaire, un identifiant suffixe
# (S-03b, cas d'une collision d'ID resolue) et un statut a rallonge.
FIXTURE_INC = """# Suivi du projet — demonstration

## 1. Increments metier

| ID | Increment | Valeur | Critere de recette | Demo | Statut |
|----|-----------|--------|--------------------|------|--------|
| INC-01 | Consulter une couche | pour le charge d'etudes | la couche s'affiche | 2026-09 | En cours |

## 2. Roadmap / backlog

| ID | Tache | Increment | Priorite | Responsable / agent | Statut | Date cible |
|----|-------|-----------|----------|---------------------|--------|------------|
| S-01 | Poser le schema | 1.0.0 | Haute | architecte | Termine | 2026-07-03 |
| S-02 | Brancher la couche | 1.0.0 | Moyenne | developpeur / architecte | Termine (2026-07-04) — via PR #2 | 2026-07-04 |
| S-03 | Ecrire la doc | 1.1.0 | Basse | documentaliste | En cours | — |
| S-03b | Reprendre l'export | 1.1.0 | Haute | developpeur | Bloque (2026-08-01) — droits absents | — |
| S-04 | Recetter | — | Moyenne | chef_projet | Pret | — |

## 3. Registre des risques

| ID | Risque | Probabilite | Impact | Mitigation | Statut |
|----|--------|-------------|--------|------------|--------|
| R-01 | Perte de la source | Faible | Eleve | sauvegarde quotidienne | Ferme (2026-07-10) |

## 4. Journal des decisions

| Date | Sujet | Decision | Justification |
|------|-------|----------|---------------|
| 2026-07-03 | Schema | **Option B retenue** | moins de jointures |

## 5. A arbitrer (points ouverts)

Aucun point ouvert.
"""

# Meme suivi, sans colonne « Increment » : cas d'un projet cadre avant 1.1.0.
FIXTURE_SANS_INC = FIXTURE_INC.replace(
    "| ID | Tache | Increment | Priorite | Responsable / agent | Statut | Date cible |",
    "| ID | Tache | Priorite | Responsable / agent | Statut | Date cible |",
).replace(
    "|----|-------|-----------|----------|---------------------|--------|------------|",
    "|----|-------|----------|---------------------|--------|------------|",
)
FIXTURE_SANS_INC = re.sub(r"^(\| S-\w+ \| [^|]+ \|)[^|]+\|", r"\1", FIXTURE_SANS_INC,
                          flags=re.M)


def _markdown_dispo():
    return importlib.util.find_spec("markdown") is not None


try:
    import pytest as _pytest
    pytestmark = _pytest.mark.skipif(
        not _markdown_dispo(),
        reason="bibliotheque 'markdown' absente (pip install markdown)",
    )
except ImportError:
    pass  # mode script : skip gere dans main()


def _generer(source_md, output_html, *extra):
    cmd = [sys.executable, str(SCRIPT),
           "--source", str(source_md), "--output", str(output_html), *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def _donnees(html):
    """Extrait le jeu de donnees embarque dans la page."""
    m = re.search(r"const DONNEES = (\{.*?\});\n", html, re.S)
    assert m, "donnees embarquees introuvables"
    return json.loads(m.group(1))


def _rendu(tmp_path, fixture, nom, *extra):
    src = tmp_path / f"{nom}.md"
    out = tmp_path / f"{nom}.html"
    src.write_text(fixture, encoding="utf-8")
    r = _generer(src, out, *extra)
    assert r.returncode == 0, r.stderr
    assert out.exists(), "la page n'a pas ete produite"
    return out.read_text(encoding="utf-8")


def test_lecture_par_nom_de_colonne(tmp_path):
    """Les colonnes sont reperees par en-tete, pas par position."""
    html = _rendu(tmp_path, FIXTURE_INC, "inc")
    taches = {t["id"]: t for t in _donnees(html)["taches"]}

    assert len(taches) == 5, f"5 taches attendues, {len(taches)} lues"
    assert taches["S-01"]["jalon"] == "1.0.0"
    assert taches["S-01"]["prio"] == "Haute"
    assert taches["S-01"]["agent"] == "architecte"
    # « Date cible » doit etre reconnue comme colonne d'echeance.
    assert taches["S-01"]["echeance"] == "2026-07-03"
    # Un statut a rallonge : le libelle est isole, le commentaire va en note.
    assert taches["S-02"]["statutLib"] == "Termine"
    assert "PR #2" in taches["S-02"]["note"]


def test_sections_en_prose_reellement_rendues(tmp_path):
    """Non-regression : les panneaux affichaient l'objet Markdown, pas son rendu.

    `MD.reset() or MD.convert(...)` renvoie l'objet (qui est vrai) et
    court-circuite la conversion : la page restait valide, mais les sections
    « Revues » et « Points ouverts » sortaient en `<markdown.core.Markdown
    object at 0x...>`.
    """
    html = _rendu(tmp_path, FIXTURE_INC, "prose")

    assert "markdown.core.Markdown object" not in html, "section non convertie"
    assert "Aucun point ouvert." in html, "contenu de la section absent"


def test_identifiant_suffixe_ne_decale_pas_les_colonnes(tmp_path):
    """Non-regression : « S-03b » ne doit pas etre pris pour un en-tete.

    Une ligne de donnees non reconnue comme telle etait auparavant traitee
    comme une ligne d'en-tete, ce qui decalait les colonnes de TOUTES les
    lignes suivantes.
    """
    html = _rendu(tmp_path, FIXTURE_INC, "suffixe")
    taches = {t["id"]: t for t in _donnees(html)["taches"]}

    assert "S-03b" in taches, "identifiant suffixe non lu"
    assert taches["S-03b"]["prio"] == "Haute"
    # La ligne SUIVANTE doit rester correctement alignee.
    assert taches["S-04"]["prio"] == "Moyenne", "colonnes decalees apres S-03b"
    assert taches["S-04"]["agent"] == "chef_projet"


def test_statut_hors_vocabulaire_reste_visible(tmp_path):
    """« Pret » n'est pas au vocabulaire : il ne doit pas etre range de force."""
    html = _rendu(tmp_path, FIXTURE_INC, "vocab")
    taches = {t["id"]: t for t in _donnees(html)["taches"]}

    assert taches["S-04"]["statut"] == "autre", "statut inconnu absorbe a tort"
    assert taches["S-04"]["statutLib"] == "Pret", "libelle d'origine perdu"
    assert "Hors vocabulaire" in html, "le bac hors vocabulaire n'est pas affiche"


def test_colonne_increment_facultative(tmp_path):
    """Sans colonne « Increment », la page se rend sans vue Increments."""
    avec = _rendu(tmp_path, FIXTURE_INC, "avec")
    sans = _rendu(tmp_path, FIXTURE_SANS_INC, "sans")

    assert 'id="v-sprint"' in avec, "bascule de vue absente alors qu'il y a des increments"
    assert "const A_JALONS = true" in avec

    assert 'id="v-sprint"' not in sans, "bascule de vue presente sans increments"
    assert "const A_JALONS = false" in sans
    # Les taches restent lues normalement.
    taches = {t["id"]: t for t in _donnees(sans)["taches"]}
    assert len(taches) == 5, "taches perdues en l'absence de colonne Increment"
    assert taches["S-01"]["prio"] == "Haute", "colonnes mal lues sans Increment"


def test_page_autoportante_et_bi_theme(tmp_path):
    """Aucune ressource externe hors polices ; les deux themes sont definis."""
    html = _rendu(tmp_path, FIXTURE_INC, "theme")

    # Le bloc :root nu porte le theme clair COMPLET (sinon la page se rend
    # avec le texte d'un theme sur le fond de l'autre).
    racine = re.search(r":root\{(.*?)\}", html, re.S)
    assert racine and "--fond:" in racine.group(1), "tokens clairs absents de :root"
    assert "@media (prefers-color-scheme: dark)" in html, "theme sombre systeme absent"
    assert ':root[data-theme="dark"]' in html, "theme sombre explicite absent"
    assert "body{margin:0;background:var(--fond)" in html, "fond du body non peint"

    # Autoportance : pas de <script src>, pas de <img src> distant.
    assert "<script src=" not in html, "script externe"
    externes = re.findall(r'(?:href|src)="(https?://[^"]+)"', html)
    assert all("fonts.googleapis.com" in u or "fonts.gstatic.com" in u
               for u in externes), f"ressource externe non autorisee : {externes}"


def test_fragment_sans_enveloppe(tmp_path):
    """--fragment sort le contenu seul, pour une enveloppe fournie ailleurs."""
    html = _rendu(tmp_path, FIXTURE_INC, "frag", "--fragment", "--titre", "Essai")

    for balise in ("<!doctype", "<html", "<head>", "<body>"):
        assert balise not in html.lower(), f"{balise} present en mode fragment"
    assert html.startswith("<title>Essai</title>"), "titre absent en tete du fragment"


def test_idempotence(tmp_path):
    """Reexecuter deux fois produit exactement la meme page."""
    src = tmp_path / "idem.md"
    out = tmp_path / "idem.html"
    src.write_text(FIXTURE_INC, encoding="utf-8")

    assert _generer(src, out).returncode == 0
    premier = out.read_text(encoding="utf-8")
    assert _generer(src, out).returncode == 0
    assert out.read_text(encoding="utf-8") == premier, "generation non idempotente"


def main():
    if not _markdown_dispo():
        print("SKIP : bibliotheque 'markdown' absente (pip install markdown)")
        return 0
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        test_lecture_par_nom_de_colonne(tmp)
        test_sections_en_prose_reellement_rendues(tmp)
        test_identifiant_suffixe_ne_decale_pas_les_colonnes(tmp)
        test_statut_hors_vocabulaire_reste_visible(tmp)
        test_colonne_increment_facultative(tmp)
        test_page_autoportante_et_bi_theme(tmp)
        test_fragment_sans_enveloppe(tmp)
        test_idempotence(tmp)
    print("8 tests OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
