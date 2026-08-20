"""Tests du generateur de doc HTML (plugins/geoid/scripts/generer_doc_html.py).

Stdlib uniquement, sans framework. Si la dependance tierce « markdown » est
absente, le test AFFICHE « SKIP » et sort en code 0 (portabilite : ne pas
echouer faute du paquet optionnel).

Lancer : python3 tests/test_generer_doc_html.py
"""
import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
# Le script et sa charte CSS sont embarques dans le plugin `geoid` (ADR-001 §2,
# S-19) : c'est ce qui les rend atteignables depuis un depot projet.
PLUGIN_SCRIPTS = RACINE / "plugins" / "geoid" / "scripts"
SCRIPT = PLUGIN_SCRIPTS / "generer_doc_html.py"
CSS = PLUGIN_SCRIPTS / "style-doc-tse.css"

# Fixture Markdown : un H1, deux sections, une TdM manuelle a ancres
# desaccentuees (pour verifier que les ancres resolvent), et le marqueur
# diagramme.
FIXTURE_MD = """# Outil de demonstration

**Version :** test

## Table des matieres

- [1. Premiere section](#1-premiere-section)
- [2. Deuxieme section](#2-deuxieme-section)

## 1. Première section

Texte de la premiere section.

<!-- WORKFLOW_DIAGRAM -->

## 2. Deuxième section

Texte de la deuxieme section.
"""

FIXTURE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">' \
              '<rect width="10" height="10" fill="#00373D"/></svg>'


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


def _ids_du_html(html):
    """Retourne l'ensemble des id= presents dans le HTML."""
    return set(re.findall(r'id="([^"]+)"', html))


def _ancres_internes(html):
    """Retourne les cibles des liens internes href="#...". """
    return set(re.findall(r'href="#([^"]+)"', html))


def _generer(source_md, output_html, diagram=None):
    cmd = [sys.executable, str(SCRIPT),
           "--source", str(source_md),
           "--output", str(output_html),
           "--css", str(CSS)]
    if diagram is not None:
        cmd += ["--diagram", str(diagram)]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_avec_diagramme(tmp_path):
    src = tmp_path / "fiche.md"
    out = tmp_path / "fiche.html"
    svg = tmp_path / "schema.svg"
    src.write_text(FIXTURE_MD, encoding="utf-8")
    svg.write_text(FIXTURE_SVG, encoding="utf-8")

    r = _generer(src, out, diagram=svg)
    assert r.returncode == 0, r.stderr
    assert out.exists(), "le HTML n'a pas ete produit"
    html = out.read_text(encoding="utf-8")

    # Titre derive du premier H1.
    assert "<title>Outil de demonstration</title>" in html, "titre absent ou non derive du H1"

    # Les sections ont des id (ancres auto-generees par l'extension toc).
    ids = _ids_du_html(html)
    assert "1-premiere-section" in ids, f"id de section manquant ; ids={ids}"
    assert "2-deuxieme-section" in ids, f"id de section manquant ; ids={ids}"

    # La nav TOC auto-generee est presente.
    assert 'id="toc"' in html, "nav TOC absente"
    assert 'class="toc"' in html, "fragment toc de markdown absent"

    # Toutes les ancres internes (TdM manuelle incluse) resolvent vers un id.
    ancres = _ancres_internes(html)
    assert ancres, "aucune ancre interne trouvee"
    non_resolues = ancres - ids
    assert not non_resolues, f"ancres non resolues : {non_resolues}"

    # Le SVG fourni est injecte, le marqueur a disparu.
    assert "diagram-wrapper" in html, "wrapper de diagramme absent"
    assert 'fill="#00373D"' in html, "SVG non injecte"
    assert "<!-- WORKFLOW_DIAGRAM -->" not in html, "marqueur diagramme non remplace"


def test_sans_diagramme(tmp_path):
    src = tmp_path / "fiche2.md"
    out = tmp_path / "fiche2.html"
    src.write_text(FIXTURE_MD, encoding="utf-8")

    r = _generer(src, out, diagram=None)
    assert r.returncode == 0, r.stderr
    assert out.exists(), "le HTML n'a pas ete produit"
    html = out.read_text(encoding="utf-8")

    # Le marqueur est retire proprement, aucun SVG injecte.
    assert "<!-- WORKFLOW_DIAGRAM -->" not in html, "marqueur diagramme non retire"
    assert "<svg" not in html, "un SVG est present alors qu'aucun diagramme n'a ete fourni"

    # Les ancres internes resolvent toujours.
    ids = _ids_du_html(html)
    non_resolues = _ancres_internes(html) - ids
    assert not non_resolues, f"ancres non resolues : {non_resolues}"


def test_idempotence(tmp_path):
    """Reexecuter deux fois produit exactement le meme HTML."""
    src = tmp_path / "fiche3.md"
    out = tmp_path / "fiche3.html"
    src.write_text(FIXTURE_MD, encoding="utf-8")

    assert _generer(src, out).returncode == 0
    premier = out.read_text(encoding="utf-8")
    assert _generer(src, out).returncode == 0
    second = out.read_text(encoding="utf-8")
    assert premier == second, "generation non idempotente"


def main():
    if not _markdown_dispo():
        print("SKIP : bibliotheque 'markdown' absente (pip install markdown)")
        return 0
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        test_avec_diagramme(tmp)
        test_sans_diagramme(tmp)
        test_idempotence(tmp)
    print("3 tests OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
