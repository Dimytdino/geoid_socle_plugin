#!/usr/bin/env python3
"""Hook PreToolUse (Write|Edit) du plugin geoid — garantie CHARTE §4.

Refuse l'écriture d'un **secret en clair**. Conçu pour une **précision élevée**
(peu de faux positifs) : on ne bloque que ce qui est sans ambiguïté un secret
littéral, jamais une *référence* à un secret (variable d'environnement,
placeholder), qui est au contraire la bonne pratique.

Sont bloqués :
  - une chaîne de connexion avec identifiants (`scheme://user:motdepasse@…`) ;
  - un identifiant/clé AWS (`AKIA…`, `aws_secret_access_key = <40 car.>`) ;
  - un bloc de clé privée (`-----BEGIN … PRIVATE KEY-----`) ;
  - des jetons de format connu (`ghp_…`, `xox…-…`) ;
  - un mot de passe affecté à un **littéral entre guillemets**
    (`password = "hunter2"`) — mais PAS `password = os.environ[...]` ni
    `password = "${DB_PW}"`.

Contrat (PreToolUse) : JSON du hook sur stdin ; pour BLOQUER → raison sur
stderr + **code 2** ; sinon 0. Entrée illisible → fail-open (0).

Garantie de premier niveau, pas étanche (un `Bash(echo > f)` échappe à
Write/Edit) : elle rend l'erreur *courante* impossible. Le bloc 7 du test
d'intégrité reste le filet au commit.
"""
import sys, json, re

# Formats non ambigus → toujours bloquer.
MOTIFS = [
    (re.compile(r"[a-zA-Z][a-zA-Z0-9+.\-]*://[^\s/@]+:[^\s/@]+@"),
     "chaîne de connexion avec identifiants (scheme://user:motdepasse@…)"),
    (re.compile(r"AKIA[0-9A-Z]{16}"),
     "identifiant de clé AWS (AKIA…)"),
    (re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+]{40}"),
     "clé secrète AWS"),
    (re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
     "clé privée"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
     "jeton GitHub (ghp_…)"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
     "jeton Slack (xox…)"),
]

# Mot de passe = littéral entre guillemets (≥ 3 car.), hors placeholder/référence.
_PWD = re.compile(r"(?im)\b(?:password|passwd|pwd|mot de passe)\b\s*[:=]\s*(['\"])([^'\"]{3,})\1")


def _mot_de_passe_litteral(texte):
    for m in _PWD.finditer(texte):
        val = m.group(2).strip()
        bas = val.lower()
        if val[0] in "$<%{" or bas.startswith(("os.environ", "os.getenv", "getenv",
                                               "process.env")) or "environ" in bas or "getenv" in bas:
            continue  # référence / placeholder → bonne pratique, on laisse
        return True
    return False


def contenu_a_inspecter(data):
    """Le texte que l'outil s'apprête à écrire, ciblé selon l'outil (pour ne
    pas inspecter l'`old_string` d'un Edit qui RETIRE un secret), avec repli
    sur les valeurs texte (hors chemin) si le nom de champ diffère."""
    ti = data.get("tool_input") or {}
    tool = data.get("tool_name", "")
    if tool == "Write" and isinstance(ti.get("content"), str):
        return ti["content"]
    if tool == "Edit" and isinstance(ti.get("new_string"), str):
        return ti["new_string"]
    return "\n".join(v for k, v in ti.items() if isinstance(v, str) and k != "file_path")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # fail-open
    texte = contenu_a_inspecter(data)
    libelle = None
    for motif, lib in MOTIFS:
        if motif.search(texte):
            libelle = lib
            break
    if libelle is None and _mot_de_passe_litteral(texte):
        libelle = "mot de passe en clair (littéral)"
    if libelle:
        fichier = (data.get("tool_input") or {}).get("file_path", "?")
        sys.stderr.write(
            f"[geoid] Écriture refusée dans {fichier} : {libelle} détecté(e).\n"
            f"CHARTE §4 — jamais de secret en clair. Passer par une variable "
            f"d'environnement (${{VAR}}) ou un gestionnaire de secrets.\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
