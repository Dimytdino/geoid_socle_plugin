"""Tests de la synchro socle → template (scripts/sync_template.py, S-15)."""
import pathlib, sys, tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
import sync_template as st


def _faux_socle(tmp):
    """Un socle minimal avec le résiduel (CHARTE + templates/ + specialisations/)
    et du bruit hors résiduel qui ne doit PAS être synchronisé."""
    p = pathlib.Path(tmp)
    (p / "CHARTE.md").write_text("CHARTE v1", encoding="utf-8")
    (p / "templates").mkdir()
    (p / "templates" / "a.template.md").write_text("gabarit A", encoding="utf-8")
    (p / "specialisations").mkdir()
    (p / "specialisations" / "dev_x.md").write_text("spé X", encoding="utf-8")
    # bruit hors résiduel :
    (p / "SOCLE_VERSION").write_text("9.9.9", encoding="utf-8")
    (p / "plugins").mkdir(); (p / "plugins" / "z.md").write_text("moteur", encoding="utf-8")
    return p


def test_liste_residuel_reelle():
    """Sur le vrai socle : CHARTE + templates/ + specialisations/. AUCUN script.

    Arbitrage S-19/S-26 : l'outillage executable d'equipe voyage par le PLUGIN
    (`${CLAUDE_PLUGIN_ROOT}/scripts/`), pas par le residuel — c'est ce que
    prevoit l'ADR-001 SS2 pour `generer_doc_html.py`. Le residuel ne porte que
    ce qu'un plugin ne peut pas fournir : la CHARTE, les gabarits, les
    specialisations. Un script dans cette liste serait une seconde source de
    verite pour le meme fichier, versionnee par un autre canal.
    """
    rels = st.fichiers_residuel(RACINE)
    assert "CHARTE.md" in rels
    autorises = ("templates/", "specialisations/")
    assert all(r == "CHARTE.md" or r.startswith(autorises) for r in rels), rels
    assert not any(r.startswith(("plugins/", "tests/")) for r in rels)
    assert not [r for r in rels if r.startswith("scripts/")], \
        "un script est revenu dans le residuel (arbitrage S-19/S-26)"


def test_check_signale_manquants_puis_apply_repare():
    with tempfile.TemporaryDirectory() as s, tempfile.TemporaryDirectory() as t:
        socle = _faux_socle(s); template = pathlib.Path(t)
        manquants, differents, en_trop = st.comparer(socle, template)
        assert set(manquants) == {"CHARTE.md", "templates/a.template.md", "specialisations/dev_x.md"}
        assert differents == [] and en_trop == []
        ecrits = st.appliquer(socle, template)
        assert set(ecrits) == set(manquants)
        # le bruit hors résiduel ne doit pas avoir été copié
        assert not (template / "SOCLE_VERSION").exists()
        assert not (template / "plugins").exists()
        # après apply : plus de dérive
        assert st.comparer(socle, template) == ([], [], [])


def test_check_signale_difference():
    with tempfile.TemporaryDirectory() as s, tempfile.TemporaryDirectory() as t:
        socle = _faux_socle(s); template = pathlib.Path(t)
        st.appliquer(socle, template)
        (template / "CHARTE.md").write_text("CHARTE modifiée localement", encoding="utf-8")
        manquants, differents, en_trop = st.comparer(socle, template)
        assert differents == ["CHARTE.md"] and manquants == [] and en_trop == []
        # apply réécrase la version du socle (source de vérité)
        assert st.appliquer(socle, template) == ["CHARTE.md"]
        assert (template / "CHARTE.md").read_text(encoding="utf-8") == "CHARTE v1"


def test_check_signale_en_trop():
    with tempfile.TemporaryDirectory() as s, tempfile.TemporaryDirectory() as t:
        socle = _faux_socle(s); template = pathlib.Path(t)
        st.appliquer(socle, template)
        (template / "templates" / "obsolete.template.md").write_text("vieux gabarit", encoding="utf-8")
        manquants, differents, en_trop = st.comparer(socle, template)
        assert en_trop == ["templates/obsolete.template.md"]
        # apply ne supprime rien (retrait manuel assumé)
        st.appliquer(socle, template)
        assert (template / "templates" / "obsolete.template.md").exists()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"{len(fns)} tests OK")
