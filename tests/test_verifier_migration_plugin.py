"""Tests du vérificateur de migration plugin (scripts/verifier_migration_plugin.py)."""
import subprocess, sys, pathlib, tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RACINE / "scripts" / "verifier_migration_plugin.py"

EN_TETE_OK = (
    "> 📦 Version socle — plugin geoid : 0.5.0 (marketplace) ; "
    "template résiduel : 0.5.0 (dernier merge).\n"
)


def _lancer(projet):
    return subprocess.run([sys.executable, str(SCRIPT), "--projet", str(projet)],
                          capture_output=True, text=True)


def test_projet_propre():
    """Pas de doublon, en-tête de version présent → sortie 0."""
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "CLAUDE.md").write_text("# Projet\n" + EN_TETE_OK, encoding="utf-8")
        ag = p / ".claude" / "agents"
        ag.mkdir(parents=True)
        # Spécialisation locale légitime : ne doit PAS être signalée.
        (ag / "developpeur_etl.md").write_text("name: developpeur_etl", encoding="utf-8")
        r = _lancer(p)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "Aucun doublon" in r.stdout
        assert "developpeur_etl.md" in r.stdout  # listé en conservé


def test_detecte_doublons():
    """Agent, commande et skill fournis par le plugin → doublons, sortie 1."""
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "CLAUDE.md").write_text("# Projet\n" + EN_TETE_OK, encoding="utf-8")
        (p / ".claude" / "agents").mkdir(parents=True)
        (p / ".claude" / "agents" / "architecte.md").write_text("x", encoding="utf-8")
        (p / ".claude" / "commands").mkdir(parents=True)
        (p / ".claude" / "commands" / "cadrer-projet.md").write_text("x", encoding="utf-8")
        (p / ".claude" / "skills" / "fme-tse").mkdir(parents=True)
        (p / ".claude" / "skills" / "fme-tse" / "SKILL.md").write_text("x", encoding="utf-8")
        r = _lancer(p)
        assert r.returncode == 1, r.stdout
        for attendu in ("architecte.md", "cadrer-projet.md", "fme-tse"):
            assert attendu in r.stdout, f"{attendu} non signalé"


def test_en_tete_version_manquant():
    """CLAUDE.md sans en-tête de version → problème, sortie 1."""
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "CLAUDE.md").write_text("# Projet sans en-tête de version", encoding="utf-8")
        r = _lancer(p)
        assert r.returncode == 1, r.stdout
        assert "Version socle" in r.stdout


def test_gabarit_non_renseigne():
    """En-tête encore au gabarit {{…}} → problème, sortie 1."""
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "CLAUDE.md").write_text(
            "# Projet\n> 📦 Version socle — plugin geoid : {{VERSION_PLUGIN_GEOID}} …\n",
            encoding="utf-8")
        r = _lancer(p)
        assert r.returncode == 1, r.stdout
        assert "gabarit" in r.stdout


if __name__ == "__main__":
    test_projet_propre()
    test_detecte_doublons()
    test_en_tete_version_manquant()
    test_gabarit_non_renseigne()
    print("4 tests OK")
