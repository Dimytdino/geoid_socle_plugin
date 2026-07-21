"""Tests d'intégrite du socle geoid-socle.
Verifie la coherence structurelle avant un push (complement de /revue-socle).
Lancer : python3 tests/test_socle_integrity.py
"""
import json, pathlib, re, subprocess, sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
# Depuis la transposition en plugins (ADR-001 option D), agents / skills /
# commandes vivent dans plugins/geoid et plugins/geoid-meta, plus dans .claude/.
DOSSIER_SKILLS = RACINE / "plugins/geoid/skills"
DOSSIERS_AGENTS = (RACINE / "plugins/geoid/agents", RACINE / "plugins/geoid-meta/agents")
DOSSIER_AGENTS_META = RACINE / "plugins/geoid-meta/agents"
echecs = []

def verifier(cond, msg):
    if not cond:
        echecs.append(msg)

# 1. Tous les agents (des deux plugins) ont un frontmatter name/description/tools
#    et lisent la CHARTE.
for dossier in DOSSIERS_AGENTS:
    for f in dossier.glob("*.md"):
        t = f.read_text(encoding="utf-8")
        for champ in ("name:", "description:", "tools:"):
            verifier(champ in t, f"{f.name} : frontmatter sans '{champ}'")
        verifier("CHARTE" in t, f"{f.name} : ne mentionne pas la lecture de CHARTE.md")

# 2. Les trois agents skill-builder sont presents dans le plugin geoid-meta
#    (outillage mainteneur, non installe chez les equipes).
for nom in ("interviewer_skill", "redacteur_skill", "critique_skill"):
    verifier((DOSSIER_AGENTS_META / f"{nom}.md").exists(),
             f"agent skill-builder absent de geoid-meta : {nom}.md")

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

# 6. Chaque skill present dans plugins/geoid/skills/ a un SKILL.md avec frontmatter
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

# 8. Coherence de version (ADR-001c, alignement strict) : SOCLE_VERSION est la
#    source de verite unique. La version de la marketplace (chaque entree de
#    plugin) et celle de chaque manifeste plugin.json doivent lui etre egales.
try:
    socle_version = (RACINE / "SOCLE_VERSION").read_text(encoding="utf-8").strip()
    verifier(bool(socle_version), "SOCLE_VERSION vide")

    marketplace = json.loads((RACINE / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    entrees = {p.get("name"): p.get("version") for p in marketplace.get("plugins", [])}
    for nom in ("geoid", "geoid-meta"):
        verifier(nom in entrees,
                 f"marketplace.json : entree de plugin '{nom}' absente")
        verifier(entrees.get(nom) == socle_version,
                 f"marketplace.json : version de '{nom}' ({entrees.get(nom)}) "
                 f"!= SOCLE_VERSION ({socle_version})")

    for nom in ("geoid", "geoid-meta"):
        manifeste = RACINE / f"plugins/{nom}/.claude-plugin/plugin.json"
        verifier(manifeste.exists(), f"manifeste absent : {manifeste.relative_to(RACINE)}")
        if manifeste.exists():
            data = json.loads(manifeste.read_text(encoding="utf-8"))
            verifier(data.get("name") == nom,
                     f"{manifeste.relative_to(RACINE)} : name '{data.get('name')}' != '{nom}'")
            verifier(data.get("version") == socle_version,
                     f"{manifeste.relative_to(RACINE)} : version ({data.get('version')}) "
                     f"!= SOCLE_VERSION ({socle_version})")
except Exception as e:
    echecs.append(f"coherence de version : {e}")

# 9. Le verificateur de migration (scripts/verifier_migration_plugin.py) embarque
#    les listes de composants fournis par les plugins pour rester autonome dans un
#    depot projet. Elles doivent egaler le contenu reel des plugins, sinon il rate
#    des doublons ou en signale de faux.
try:
    sys.path.insert(0, str(RACINE / "scripts"))
    import verifier_migration_plugin as vmp
    attendus = {
        "AGENTS_GEOID": ({f.stem for f in (RACINE / "plugins/geoid/agents").glob("*.md")}, vmp.AGENTS_GEOID),
        "AGENTS_GEOID_META": ({f.stem for f in (RACINE / "plugins/geoid-meta/agents").glob("*.md")}, vmp.AGENTS_GEOID_META),
        "COMMANDS_GEOID": ({f.stem for f in (RACINE / "plugins/geoid/commands").glob("*.md")}, vmp.COMMANDS_GEOID),
        "COMMANDS_GEOID_META": ({f.stem for f in (RACINE / "plugins/geoid-meta/commands").glob("*.md")}, vmp.COMMANDS_GEOID_META),
        "SKILLS_GEOID": ({d.name for d in (RACINE / "plugins/geoid/skills").iterdir() if d.is_dir()}, vmp.SKILLS_GEOID),
    }
    for nom, (reel, embarque) in attendus.items():
        verifier(reel == embarque,
                 f"verifier_migration_plugin.{nom} desynchronise du plugin : "
                 f"reel={sorted(reel)} vs embarque={sorted(embarque)}")
except Exception as e:
    echecs.append(f"verificateur de migration : {e}")

if echecs:
    print("ECHECS d'integrite :")
    for e in echecs:
        print("  -", e)
    sys.exit(1)
print("Integrite du socle : OK")
