"""Tests du packageur de skills."""
import subprocess, sys, zipfile, pathlib, tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RACINE / "scripts" / "packager_skill.py"


def test_packaging_nominal():
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp) / "mon-skill"
        d.mkdir()
        (d / "SKILL.md").write_text("---\nname: mon-skill\n---\n# Test")
        (d / "interview-brut.md").write_text("matière brute — ne doit pas être packagée")
        r = subprocess.run([sys.executable, str(SCRIPT), str(d)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        paquet = d.parent / "mon-skill.skill"
        assert paquet.exists()
        noms = zipfile.ZipFile(paquet).namelist()
        assert "mon-skill/SKILL.md" in noms
        assert not any("interview-brut" in n for n in noms), \
            "l'interview brute ne doit pas partir dans le paquet"


def test_refus_sans_skill_md():
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp) / "vide"
        d.mkdir()
        r = subprocess.run([sys.executable, str(SCRIPT), str(d)],
                           capture_output=True, text=True)
        assert r.returncode != 0


if __name__ == "__main__":
    test_packaging_nominal()
    test_refus_sans_skill_md()
    print("2 tests OK")
