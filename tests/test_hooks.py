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


GABARIT = RACINE / "templates" / "CLAUDE.projet.template.md"


def _session(claude_md):
    """Lance le hook SessionStart sur un projet dont le CLAUDE.md est `claude_md`."""
    with tempfile.TemporaryDirectory() as plug, tempfile.TemporaryDirectory() as proj:
        (pathlib.Path(plug) / ".claude-plugin").mkdir()
        (pathlib.Path(plug) / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "geoid", "version": "9.9.9"}), encoding="utf-8")
        (pathlib.Path(proj) / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
        r = _lancer("injecter_contexte.py", {"hook_event_name": "SessionStart"},
                    env={"CLAUDE_PLUGIN_ROOT": plug}, cwd=proj)
        assert r.returncode == 0, r.stderr
        return r.stdout


# La fixture est le gabarit RÉELLEMENT LIVRÉ, pas une chaîne construite pour
# l'occasion : c'est le seul fichier que le hook rencontrera en production.
# Règle générale du socle : un test de hook prend le gabarit livré comme fixture.

def test_injection_version():
    assert "9.9.9" in _session(GABARIT.read_text(encoding="utf-8"))


def test_gabarit_sans_adr_tranche_nannonce_rien():
    """Gabarit livré tel quel : aucun ADR ouvert à annoncer.

    Le §0 du gabarit explique le marqueur `🔧 À ARBITRER` en prose et le §9
    porte une ligne de tableau à placeholders : ni l'un ni l'autre n'est une
    décision en attente. L'ancien filtre remontait la prose du §0, tronquée.
    """
    sortie = _session(GABARIT.read_text(encoding="utf-8"))
    assert "Points à arbitrer" not in sortie, sortie


def test_ligne_de_tableau_a_decider_est_annoncee():
    """Un ADR réellement ouvert (§9, colonne Statut) est annoncé en entier."""
    gabarit = GABARIT.read_text(encoding="utf-8")
    ligne = "| ADR-002 | modèle de données | écriture du schéma, migrations | À décider |"
    rempli = gabarit.replace(
        "| ADR-001 | {{...}} | {{ex. écriture du schéma, migrations}} | À décider |", ligne)
    assert ligne in rempli, "structure du §9 du gabarit modifiée : adapter le test"
    sortie = _session(rempli)
    assert "Points à arbitrer" in sortie, sortie
    assert "ADR-002 — modèle de données" in sortie, sortie


def test_statut_tranche_nest_pas_annonce():
    """Une décision actée (statut hors À décider / À arbitrer / Ouvert) est muette."""
    gabarit = GABARIT.read_text(encoding="utf-8")
    rempli = gabarit.replace(
        "| ADR-001 | {{...}} | {{ex. écriture du schéma, migrations}} | À décider |",
        "| ADR-002 | modèle de données | — | Actée le 2026-08-20 |")
    assert "Points à arbitrer" not in _session(rempli)


def _injecter_avec_claude_md(contenu):
    with tempfile.TemporaryDirectory() as proj:
        (pathlib.Path(proj) / "CLAUDE.md").write_text(contenu, encoding="utf-8")
        r = _lancer("injecter_contexte.py", {"hook_event_name": "SessionStart"}, cwd=proj)
        assert r.returncode == 0, r.stderr
        return r.stdout


def test_hygiene_signale_fichier_trop_long():
    # Rien dans le cycle de vie d'un projet n'allège le CLAUDE.md : l'avertissement
    # de démarrage est la seule force de rappel. Il doit se déclencher sur la
    # taille SEULE, sans section suspecte.
    sortie = _injecter_avec_claude_md("# Projet\n" + "ligne anodine\n" * 300)
    assert "Hygiène du CLAUDE.md" in sortie
    assert "301 lignes" in sortie
    assert "cloturer-session" in sortie


def test_hygiene_signale_sections_hors_contexte():
    sortie = _injecter_avec_claude_md(
        "# Projet\n## 8. Glossaire interne (à enrichir)\n- POC : ...\n"
        "## 9. État d'avancement\n- [x] fait\n")
    assert "glossaire" in sortie and "état d'avancement" in sortie
    # Court : la taille ne doit pas être invoquée ici.
    assert "lignes (>" not in sortie


def test_hygiene_muette_sur_un_claude_md_sain():
    # Le gabarit vierge lui-même ne doit JAMAIS déclencher l'avertissement,
    # sinon il devient du bruit dès la première session d'un projet cadré.
    gabarit = (RACINE / "templates" / "CLAUDE.projet.template.md").read_text(encoding="utf-8")
    assert "Hygiène du CLAUDE.md" not in _injecter_avec_claude_md(gabarit)
    assert "Hygiène du CLAUDE.md" not in _injecter_avec_claude_md("# Projet\ncourt.\n")


def test_hygiene_absente_sans_claude_md():
    with tempfile.TemporaryDirectory() as proj:
        r = _lancer("injecter_contexte.py", {"hook_event_name": "SessionStart"}, cwd=proj)
        assert r.returncode == 0
        assert "Hygiène" not in r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"{len(fns)} tests OK")
