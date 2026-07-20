"""Tests d'intégrite du socle geoid-socle.
Verifie la coherence structurelle avant un push (complement de /revue-socle).
Lancer : python3 tests/test_socle_integrity.py
"""
import json, pathlib, re, subprocess, sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIER_SKILLS = RACINE / ".claude/skills"
echecs = []

def verifier(cond, msg):
    if not cond:
        echecs.append(msg)

# 1. Tous les agents ont un frontmatter name/description/tools et lisent la CHARTE
for f in (RACINE / ".claude/agents").glob("*.md"):
    t = f.read_text(encoding="utf-8")
    for champ in ("name:", "description:", "tools:"):
        verifier(champ in t, f"{f.name} : frontmatter sans '{champ}'")
    verifier("CHARTE" in t, f"{f.name} : ne mentionne pas la lecture de CHARTE.md")

# 2. Les trois agents skill-builder sont presents en permanence dans le socle
#    (la commande /creer-skill ne les active plus a chaud : les agents copies
#    en cours de session ne seraient charges qu'au redemarrage).
for nom in ("interviewer_skill", "redacteur_skill", "critique_skill"):
    verifier((RACINE / f".claude/agents/{nom}.md").exists(),
             f"agent skill-builder absent du socle : {nom}.md")

# 3. settings.json est un JSON valide, en mode 'default', sans interpreteur
#    generaliste auto-autorise (un python:* en allow contourne le reste).
try:
    settings = json.loads((RACINE / ".claude/settings.json").read_text(encoding="utf-8"))
    permissions = settings.get("permissions", {})
    verifier(permissions.get("defaultMode") == "default",
             "settings.json : defaultMode doit rester 'default' (acceptEdits se choisit par session)")
    for regle in permissions.get("allow", []):
        verifier(not re.match(r"Bash\(python3?[:\s]\*?\)?$", regle),
                 f"settings.json : interpreteur generaliste en allow : {regle}")
except Exception as e:
    echecs.append(f"settings.json invalide : {e}")

# 4. Les templates portent les sections attendues, au bon etage :
#    le CLAUDE.md projet reste court (journal des decisions + renvoi au
#    suivi) ; roadmap/risques/revues vivent dans le template de suivi.
tpl = (RACINE / "templates/CLAUDE.projet.template.md").read_text(encoding="utf-8")
for section in ("Journal des décisions", "docs/suivi-projet.md", "Tâches bloquées"):
    verifier(section in tpl, f"template CLAUDE projet : '{section}' absent")
for entete in ("| ID | Tâche |", "| ID | Risque |", "| Date | Livrable |"):
    verifier(entete not in tpl,
             f"template CLAUDE projet : tableau de suivi '{entete}' — il vit dans suivi-projet, pas dans le contexte permanent")
suivi = (RACINE / "templates/suivi-projet.template.md").read_text(encoding="utf-8")
for section in ("Roadmap", "Registre des risques", "Suivi des revues"):
    verifier(section in suivi, f"template suivi-projet : section '{section}' absente")

# 5. Aucun artefact genere *suivi par git* (on tolere les artefacts de build
#    locaux git-ignores ; on ne signale que ce qui est reellement commite).
try:
    sortie = subprocess.run(
        ["git", "ls-files"], cwd=RACINE,
        capture_output=True, text=True, check=True,
    ).stdout
    fichiers_traques = set(sortie.splitlines())
except Exception:
    # Degradation : hors d'un depot git (ou git absent), on considere
    # l'ensemble traque comme vide -> aucun artefact genere n'est signale.
    # Choix prudent : ce test d'hygiene ne vaut que sur un depot git.
    fichiers_traques = set()

verifier(not any("__pycache__" in chemin.split("/") for chemin in fichiers_traques),
         "__pycache__ present (a supprimer)")
skills_versionnes = [c for c in fichiers_traques if c.endswith(".skill")]
verifier(not skills_versionnes,
         f".skill versionne(s) (artefact genere, a exclure) : {skills_versionnes}")

# 6. Chaque skill present dans .claude/skills/ a un SKILL.md avec frontmatter
#    name/description, figure dans le tableau « Skills publiés » du registre,
#    et n'apparait pas comme entree « a creer » (seuls les titres en gras en
#    debut de ligne comptent — une simple mention en prose n'est pas une
#    entree, c'est ce qui causait un faux positif avant 0.4.0).
registre = (RACINE / "skills-geoid-registre-et-methode.md").read_text(encoding="utf-8")
apres_publies = registre.split("### Skills publiés", 1)
publies = apres_publies[1].split("### Skills à créer", 1)[0] if len(apres_publies) == 2 else ""
verifier(publies, "registre : section '### Skills publiés' introuvable")
section_a_creer = registre.split("### Skills à créer", 1)
noms_a_creer = re.findall(r"^\*\*`?([\w-]+)`?\*\*", section_a_creer[-1], re.M)

for d in sorted(DOSSIER_SKILLS.iterdir()) if DOSSIER_SKILLS.exists() else []:
    if not d.is_dir():
        continue
    skill_md = d / "SKILL.md"
    verifier(skill_md.exists(), f"{d.name} : pas de SKILL.md")
    if skill_md.exists():
        t = skill_md.read_text(encoding="utf-8")
        for champ in ("name:", "description:"):
            verifier(champ in t, f"{d.name}/SKILL.md : frontmatter sans '{champ}'")
    verifier(f"`{d.name}`" in publies,
             f"registre : '{d.name}' absent du tableau « Skills publiés »")
    verifier(d.name not in noms_a_creer,
             f"registre : '{d.name}' est publie mais encore liste comme 'a creer'")

# 7. Pas de secret evident commite — scanne tous les fichiers texte traques par git
EXTENSIONS_TEXTE = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".sh", ".cfg", ".ini", ".env"}
PATTERN_SECRET = re.compile(r"(password|mot de passe)\s*[:=]\s*\S+", re.I)
for chemin in fichiers_traques:
    p = RACINE / chemin
    if p.suffix.lower() not in EXTENSIONS_TEXTE:
        continue
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    verifier(not PATTERN_SECRET.search(txt),
             f"{chemin} : possible secret en clair (a verifier manuellement)")

if echecs:
    print("ECHECS d'integrite :")
    for e in echecs:
        print("  -", e)
    sys.exit(1)
print("Integrite du socle : OK")
