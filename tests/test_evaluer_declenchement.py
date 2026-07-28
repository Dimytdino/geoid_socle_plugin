"""Tests du validateur d'évals de déclenchement (scripts/evaluer_declenchement.py).

On teste deux choses : (1) les jeux d'évals RÉELS du dépôt sont conformes ;
(2) le validateur attrape bien chaque défaut de structure/couverture, sur des
racines factices construites en tmp.
"""
import json, pathlib, sys, tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
import evaluer_declenchement as ed


def _racine_factice(tmp, evals):
    """Construit une racine minimale : un skill publié 'skill-a' (+ 'skill-b'
    référençable en voisin), et les fichiers d'éval fournis.
    `evals` : dict {nom_skill: donnée_dict_ou_None}. None = fichier absent."""
    p = pathlib.Path(tmp)
    for nom in ("skill-a", "skill-b"):
        d = p / "plugins/geoid/skills" / nom
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("name: x\ndescription: y\n", encoding="utf-8")
    (p / "evals").mkdir()
    for nom, data in evals.items():
        if data is None:
            continue
        (p / "evals" / f"{nom}.eval.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


def _eval_ok(skill="skill-a"):
    """Un jeu d'éval conforme, à dégrader dans chaque test."""
    return {
        "skill": skill,
        "version_skill_evaluee": "1.0",
        "declencheurs": [{"prompt": f"decl {i}", "pourquoi": "p"} for i in range(5)],
        "non_declencheurs": [
            {"prompt": "voisin", "pourquoi": "p", "skill_attendu": "skill-b"},
            {"prompt": "hors 1", "pourquoi": "p"},
            {"prompt": "hors 2", "pourquoi": "p"},
        ],
    }


def test_evals_reels_valides():
    """Les jeux d'évals versionnés dans evals/ sont conformes."""
    echecs = ed.valider(RACINE)
    assert echecs == [], "évals réelles non conformes :\n" + "\n".join(echecs)


def test_jeu_conforme_factice():
    with tempfile.TemporaryDirectory() as tmp:
        r = _racine_factice(tmp, {"skill-a": _eval_ok(), "skill-b": _eval_ok("skill-b")})
        # skill-b se réfère à skill-a pour rester symétrique
        r_b = json.loads((r / "evals/skill-b.eval.json").read_text(encoding="utf-8"))
        r_b["non_declencheurs"][0]["skill_attendu"] = "skill-a"
        (r / "evals/skill-b.eval.json").write_text(json.dumps(r_b, ensure_ascii=False), encoding="utf-8")
        assert ed.valider(r) == []


def test_skill_sans_eval():
    with tempfile.TemporaryDirectory() as tmp:
        r = _racine_factice(tmp, {"skill-a": _eval_ok()})  # skill-b sans éval
        echecs = ed.valider(r)
        assert any("skill-b.eval.json manquant" in e for e in echecs), echecs


def test_couverture_insuffisante():
    with tempfile.TemporaryDirectory() as tmp:
        mauvais = _eval_ok()
        mauvais["declencheurs"] = mauvais["declencheurs"][:2]
        r = _racine_factice(tmp, {"skill-a": mauvais, "skill-b": _eval_ok("skill-b")})
        echecs = ed.valider(r)
        assert any("< minimum" in e for e in echecs), echecs


def test_sans_frontiere():
    """Aucun non-déclencheur avec skill_attendu → défaut signalé."""
    with tempfile.TemporaryDirectory() as tmp:
        mauvais = _eval_ok()
        for n in mauvais["non_declencheurs"]:
            n.pop("skill_attendu", None)
        r = _racine_factice(tmp, {"skill-a": mauvais, "skill-b": _eval_ok("skill-b")})
        echecs = ed.valider(r)
        assert any("frontière" in e for e in echecs), echecs


def test_sans_hors_perimetre():
    """Tous les non-déclencheurs ont un skill_attendu → défaut signalé."""
    with tempfile.TemporaryDirectory() as tmp:
        mauvais = _eval_ok()
        for n in mauvais["non_declencheurs"]:
            n["skill_attendu"] = "skill-b"
        r = _racine_factice(tmp, {"skill-a": mauvais, "skill-b": _eval_ok("skill-b")})
        echecs = ed.valider(r)
        assert any("hors-périmètre" in e for e in echecs), echecs


def test_skill_attendu_inconnu():
    with tempfile.TemporaryDirectory() as tmp:
        mauvais = _eval_ok()
        mauvais["non_declencheurs"][0]["skill_attendu"] = "skill-fantome"
        r = _racine_factice(tmp, {"skill-a": mauvais, "skill-b": _eval_ok("skill-b")})
        echecs = ed.valider(r)
        assert any("inconnu" in e for e in echecs), echecs


def test_prompt_double():
    with tempfile.TemporaryDirectory() as tmp:
        mauvais = _eval_ok()
        mauvais["non_declencheurs"][0]["prompt"] = "decl 0"  # collision avec un déclencheur
        r = _racine_factice(tmp, {"skill-a": mauvais, "skill-b": _eval_ok("skill-b")})
        echecs = ed.valider(r)
        assert any("double" in e for e in echecs), echecs


def test_eval_orpheline():
    with tempfile.TemporaryDirectory() as tmp:
        r = _racine_factice(tmp, {"skill-a": _eval_ok(), "skill-b": _eval_ok("skill-b"),
                                  "skill-disparu": _eval_ok("skill-disparu")})
        echecs = ed.valider(r)
        assert any("orpheline" in e for e in echecs), echecs


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"{len(fns)} tests OK")
