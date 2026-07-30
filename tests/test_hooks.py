"""Tests des hooks du plugin geoid (plugins/geoid/hooks/).

On teste la LOGIQUE des scripts en isolation (entrée JSON simulée sur stdin) :
- bloquer_secrets.py : sort en 2 sur un secret, en 0 sinon ;
- injecter_contexte.py : injecte la version du plugin (+ points « À ARBITRER »).

Le *chargement* réel des hooks par Claude Code (hooks.json auto-découvert,
blocage effectif de Write/Edit) n'est PAS testable ici : il se vérifie en
session réelle avec le plugin installé (voir la checklist du PR / DEMARRER).
"""
import json, subprocess, sys, pathlib, tempfile, os

RACINE = pathlib.Path(__file__).resolve().parents[1]
HOOKS = RACINE / "plugins" / "geoid" / "hooks"


def _lancer(script, payload, env=None, cwd=None):
    r = subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(payload), capture_output=True, text=True,
        env={**os.environ, **(env or {})}, cwd=cwd)
    return r


def test_hooks_json_valide_et_scripts_presents():
    data = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
    assert "PreToolUse" in data["hooks"] and "SessionStart" in data["hooks"]
    for script in ("bloquer_secrets.py", "injecter_contexte.py"):
        assert (HOOKS / script).is_file(), script


def test_bloque_chaine_de_connexion():
    r = _lancer("bloquer_secrets.py", {
        "tool_name": "Write",
        "tool_input": {"file_path": "app/db.py",
                       "content": "DSN = 'postgresql://user:s3cret@10.0.0.1:5432/prod'"}})
    assert r.returncode == 2, r.stdout + r.stderr
    assert "connexion" in r.stderr.lower()


def test_bloque_mot_de_passe_litteral_cle_aws_et_cle_privee():
    for contenu in ("password = 'hunter2'",
                    'mot de passe: "Secret123"',
                    "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "AKIAIOSFODNN7EXAMPLE",
                    "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"):
        r = _lancer("bloquer_secrets.py",
                    {"tool_name": "Write", "tool_input": {"file_path": "f", "content": contenu}})
        assert r.returncode == 2, f"non bloqué : {contenu!r}\n{r.stderr}"


def test_reference_env_ou_placeholder_autorisee():
    # La bonne pratique (référence, placeholder) ne doit PAS être bloquée.
    for contenu in ("password = os.environ['DB_PASSWORD']",
                    'password: "${DB_PW}"',
                    "PASSWORD = get_secret('db')"):
        r = _lancer("bloquer_secrets.py",
                    {"tool_name": "Write", "tool_input": {"file_path": "f", "content": contenu}})
        assert r.returncode == 0, f"faux positif sur : {contenu!r}\n{r.stderr}"


def test_edit_inspecte_new_string_pas_old_string():
    # On RETIRE un secret : old_string en contient un, new_string non → autorisé.
    r = _lancer("bloquer_secrets.py", {
        "tool_name": "Edit",
        "tool_input": {"file_path": "conf.py",
                       "old_string": "PASSWORD = 'hunter2'",
                       "new_string": "PASSWORD = os.environ['DB_PASSWORD']"}})
    assert r.returncode == 0, r.stderr


def test_contenu_benin_autorise():
    r = _lancer("bloquer_secrets.py", {
        "tool_name": "Write",
        "tool_input": {"file_path": "q.sql",
                       "content": "SELECT ST_MakeValid(geom) FROM parcelles WHERE srid = 2154;"}})
    assert r.returncode == 0, r.stderr


def test_entree_illisible_fail_open():
    r = subprocess.run([sys.executable, str(HOOKS / "bloquer_secrets.py")],
                       input="pas du json", capture_output=True, text=True)
    assert r.returncode == 0


def test_injection_version_et_adr():
    with tempfile.TemporaryDirectory() as plug, tempfile.TemporaryDirectory() as proj:
        # faux plugin root avec plugin.json versionné
        (pathlib.Path(plug) / ".claude-plugin").mkdir()
        (pathlib.Path(plug) / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "geoid", "version": "9.9.9"}), encoding="utf-8")
        # projet avec un point À ARBITRER dans CLAUDE.md
        (pathlib.Path(proj) / "CLAUDE.md").write_text(
            "# Projet\n- 🔧 À ARBITRER : choix de la stack (ADR-002)\n", encoding="utf-8")
        r = _lancer("injecter_contexte.py", {"hook_event_name": "SessionStart"},
                    env={"CLAUDE_PLUGIN_ROOT": plug}, cwd=proj)
        assert r.returncode == 0, r.stderr
        assert "9.9.9" in r.stdout
        assert "À ARBITRER" in r.stdout and "stack" in r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"{len(fns)} tests OK")
