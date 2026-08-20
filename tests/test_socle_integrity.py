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
        # Un lecteur de fichiers en allow rend les deny (cat *.env*, *.pem...)
        # inoperants sur le chemin le plus evident : la lecture d'un secret ne
        # se ferme pas par liste (head/less/xxd la contournent), mais elle ne
        # doit pas non plus etre auto-autorisee. Mode 'default' => 'ask'.
        verifier(not re.match(r"Bash\((?:cat|head|tail|less|more|xxd|strings)[:\s]", regle),
                 f"settings.json : lecteur de fichiers en allow : {regle} "
                 f"(le retirer : en mode 'default' il tombe en confirmation)")
    # Sandbox : les deux cles ne se dissocient jamais. 'enabled: true' avec
    # 'failIfUnavailable: false' est le pire etat possible — une protection
    # silencieusement nulle qu'on croit active (les stances filesystem/network
    # sont alors decoratives). Tant que bwrap n'est pas installable (S-11),
    # 'enabled: false' est l'etat assume ici.
    sandbox = settings.get("sandbox", {})
    if sandbox.get("enabled") is True:
        verifier(sandbox.get("failIfUnavailable") is True,
                 "settings.json : sandbox.enabled=true impose failIfUnavailable=true "
                 "(sinon la sandbox echoue en silence et les stances sont decoratives)")
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
# Fichiers dont le ROLE est de contenir ces motifs (le detecteur de secrets du
# hook geoid et son test) : exclus du scan, sinon faux positif garanti.
FICHIERS_MOTIFS_SECRET = {
    "plugins/geoid/hooks/bloquer_secrets.py",
    "tests/test_hooks.py",
}
for chemin in fichiers_traques:
    if chemin in FICHIERS_MOTIFS_SECRET:
        continue
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

# 10. Gabarit .mcp.json (ADR-001d) : JSON valide, structure attendue, et
#     aucun identifiant en dur — les valeurs de connexion/secret passent par
#     des placeholders ${VAR} (jamais de secret en clair, CHARTE §4).
gabarit_mcp = RACINE / "templates/mcp.projet.template.json"
if gabarit_mcp.exists():
    try:
        data = json.loads(gabarit_mcp.read_text(encoding="utf-8"))
        serveurs = data.get("mcpServers")
        verifier(isinstance(serveurs, dict) and serveurs,
                 "gabarit .mcp.json : clé 'mcpServers' absente ou vide")

        def _chaines(x):
            # toutes les valeurs texte d'une conf serveur (env, args, url, headers...)
            if isinstance(x, str):
                yield x
            elif isinstance(x, dict):
                for v in x.values():
                    yield from _chaines(v)
            elif isinstance(x, list):
                for v in x:
                    yield from _chaines(v)

        for nom, conf in (serveurs or {}).items():
            for val in _chaines(conf):
                # toute valeur ressemblant a une URI/identifiant doit etre un placeholder
                if ("://" in val) or ("@" in val):
                    verifier("${" in val,
                             f"gabarit .mcp.json : serveur '{nom}' contient un "
                             f"identifiant en dur (attendu : placeholder ${{VAR}})")
    except Exception as e:
        echecs.append(f"gabarit .mcp.json invalide : {e}")

# 11. Master/derive (S-23, audit SS3.6) : le skill conventions-sig-tse est une
#     copie derivee de la CHARTE SS3-SS4. Tout code EPSG cite dans la CHARTE
#     doit figurer dans le skill : sinon un amendement CHARTE non repercute
#     laisse une regle SRC perimee dans le derive (cause racine du bug 0.3.1).
try:
    charte = (RACINE / "CHARTE.md").read_text(encoding="utf-8")
    skill_sig = (RACINE / "plugins/geoid/skills/conventions-sig-tse/SKILL.md").read_text(encoding="utf-8")
    for code in sorted(set(re.findall(r"EPSG:\d+", charte))):
        verifier(code in skill_sig,
                 f"conventions-sig-tse : {code} present dans la CHARTE mais absent "
                 f"du skill derive (master/derive desynchronise)")
    verifier("fonci" in charte.lower() and "fonci" in skill_sig.lower(),
             "conventions-sig-tse : confidentialite fonciere (CHARTE SS4) non refletee dans le skill")
except Exception as e:
    echecs.append(f"coherence CHARTE <-> skill : {e}")

# 12. Coherence des versions (S-23) : la version d'un skill au registre
#     (section « Skills publies ») doit egaler le champ version_skill_evaluee
#     de son jeu d'evals. Attrape la derive du type eval 1.1 vs skill 1.2.
try:
    reg = (RACINE / "skills-geoid-registre-et-methode.md").read_text(encoding="utf-8")
    seg = reg.split("### Skills publiés", 1)
    publies_txt = seg[1].split("### Skills à créer", 1)[0] if len(seg) == 2 else ""
    versions_registre = dict(re.findall(r"^\|\s*`([\w-]+)`\s*\|\s*(\d+\.\d+)", publies_txt, re.M))
    dossier_evals = RACINE / "evals"
    for f in sorted(dossier_evals.glob("*.eval.json")) if dossier_evals.exists() else []:
        data = json.loads(f.read_text(encoding="utf-8"))
        nom = data.get("skill")
        vev = str(data.get("version_skill_evaluee", "")).strip()
        vreg = versions_registre.get(nom)
        verifier(vreg is not None,
                 f"eval {f.name} : skill '{nom}' introuvable dans « Skills publiés » du registre")
        if vreg is not None:
            verifier(vev == vreg,
                     f"eval {f.name} : version_skill_evaluee ({vev}) != version au registre "
                     f"({vreg}) pour {nom}")
except Exception as e:
    echecs.append(f"coherence registre <-> evals : {e}")

# --- Surface distribuee : tout ce qui atteint un depot projet ---------------
# Deux canaux : le residuel recopie par sync_template.py (CHARTE, templates/,
# specialisations/) et le plugin geoid installe depuis la
# marketplace. geoid-meta est HORS perimetre : outillage du mainteneur, jamais
# installe chez les equipes — il peut donc citer tests/ et scripts/ librement.
try:
    sys.path.insert(0, str(RACINE / "scripts"))
    import sync_template as _st
    DISTRIBUES = set(_st.fichiers_residuel(RACINE))
    for _p in (RACINE / "plugins/geoid").rglob("*"):
        if _p.is_file():
            DISTRIBUES.add(_p.relative_to(RACINE).as_posix())
except Exception as e:
    DISTRIBUES = set()
    echecs.append(f"surface distribuee illisible : {e}")

# 13. Portabilite des chemins (S-19, item « Portabilite » de /revue-socle) :
#     un fichier distribue ne doit citer aucun chemin qui n'existe QUE dans le
#     socle. Un projet n'a ni tests/, ni evals/, ni plugins/ : la consigne y
#     serait inexecutable. La regle se resout contre l'arbre reel plutot que
#     contre une liste de prefixes — elle reste juste quand le socle bouge.
EXT_SCANNEES = {".md", ".css", ".json", ".py", ".txt", ".yml"}
# Chemins qui existent des deux cotes : dans un texte distribue ils designent
# l'artefact DU PROJET, pas son homonyme du socle.
CONVENTION_PROJET = {"CLAUDE.md", "CHARTE.md", "docs/suivi-projet.md", ".mcp.json",
                     ".claude/settings.json", ".gitignore"}
RX_CHEMIN = re.compile(r"(?<![\w/.\-])((?:[\w.\-]+/)+[\w.*\-]+\.[\w*]+)")
for rel in sorted(DISTRIBUES):
    chemin = RACINE / rel
    if chemin.suffix.lower() not in EXT_SCANNEES:
        continue
    for num, ligne in enumerate(chemin.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        for m in RX_CHEMIN.finditer(ligne):
            cible = m.group(1).rstrip(".")
            if cible in CONVENTION_PROJET or cible in DISTRIBUES:
                continue
            verifier(not (RACINE / cible).exists(),
                     f"{rel}:{num} : renvoi non portable vers '{cible}' — chemin propre au "
                     f"socle, absent d'un depot projet (le distribuer, ou reformuler)")

# 14. Renvois ADR (arbitrage du 2026-08-03, option 3) : un contenu distribue
#     ne cite JAMAIS un ADR du socle. Les deux series partagent la meme
#     numerotation (ADR-001 du socle vs ADR-001 d'un projet), donc aucune
#     heuristique ne les distingue de facon fiable ; et un ADR du socle est de
#     toute facon irresolvable depuis un projet (ADR-001d n'est meme pas un
#     fichier, c'est une section). On cite la regle, pas sa source.
#     Seules exceptions : les gabarits qui parlent des ADR DU PROJET.
RX_ADR = re.compile(r"\bADR-\d")
for rel in sorted(DISTRIBUES):
    chemin = RACINE / rel
    if chemin.suffix.lower() != ".md":
        continue
    for num, ligne in enumerate(chemin.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not RX_ADR.search(ligne):
            continue
        if "ADR-00X" in ligne or "{{" in ligne:   # gabarit d'ADR du projet
            continue
        verifier(False,
                 f"{rel}:{num} : renvoi vers un ADR du socle — irresolvable depuis un "
                 f"projet et en collision avec la numerotation du projet. Citer la regle "
                 f"applicable (ex. « CHARTE §4 »), pas l'ADR qui l'a decidee")

# 15. Discipline d'increment metier (S-24). Le socle a longtemps decrit le
#     pilotage en tâches et jalons : un projet pouvait enchainer des sprints
#     100 % techniques sans jamais rien livrer de recettable par le metier.
#     La discipline tient a quatre endroits qui doivent rester alignes — si
#     l'un d'eux perd la notion, la chaine se rompt en silence.
_suivi_tpl = (RACINE / "templates/suivi-projet.template.md").read_text(encoding="utf-8")
_chef = (RACINE / "plugins/geoid/agents/chef_projet.md").read_text(encoding="utf-8")
_revue = (RACINE / "plugins/geoid/agents/revieweur.md").read_text(encoding="utf-8")
_cadrage = (RACINE / "plugins/geoid/commands/cadrer-projet.md").read_text(encoding="utf-8")
_cloture = (RACINE / "plugins/geoid/commands/cloturer-session.md").read_text(encoding="utf-8")

verifier("Incrément en cours" in tpl,
         "template CLAUDE projet : bloc « Incrément en cours » absent — "
         "sans cap de session, l'orchestrateur repart en pilotage par tâches")
verifier("Critère de recette" in tpl,
         "template CLAUDE projet : « Critère de recette » absent du bloc incrément")
verifier("| ID | Incrément" not in tpl,
         "template CLAUDE projet : tableau des incréments — il vit dans "
         "suivi-projet, pas dans le contexte permanent (seul l'incrément en cours)")
verifier("| ID | Incrément" in _suivi_tpl,
         "template suivi-projet : tableau des incréments absent")
verifier("Critère de recette" in _suivi_tpl and "Recettes prononcées" in _suivi_tpl,
         "template suivi-projet : critère de recette ou table des recettes absents "
         "(la revue dit « conforme », la recette dit « le métier en veut » — les deux)")
for _f, _t, _motifs in (("chef_projet", _chef, ("incrément", "recette", "vertical")),
                        ("revieweur", _revue, ("ecettab",)),
                        ("cadrer-projet", _cadrage, ("incrément recettable",)),
                        ("cloturer-session", _cloture, ("incrément", "Dégraissage"))):
    for _m in _motifs:
        verifier(_m in _t, f"{_f} : la discipline d'incrément a disparu (motif « {_m} » absent)")

# 16. Coherence du seuil d'hygiene du CLAUDE.md. Le hook avertit, le gabarit et
#     les deux commandes annoncent un chiffre : trois sources de verite pour un
#     meme nombre. Elles derivent des qu'on ajuste l'une sans les autres.
_hook = (RACINE / "plugins/geoid/hooks/injecter_contexte.py").read_text(encoding="utf-8")
_m = re.search(r"^SEUIL_LIGNES\s*=\s*(\d+)", _hook, re.M)
verifier(_m, "injecter_contexte.py : SEUIL_LIGNES introuvable")
if _m:
    seuil = int(_m.group(1))
    for _nom, _texte in (("template CLAUDE projet", tpl),
                         ("cadrer-projet", _cadrage),
                         ("cloturer-session", _cloture)):
        verifier(re.search(rf"{seuil}\s+lignes", _texte),
                 f"{_nom} : ne cite pas le seuil d'hygiène du hook ({seuil} lignes)")
    # Le gabarit vierge doit passer sous le seuil avec de la marge : rempli, il
    # grossit. Un gabarit qui declenche l'avertissement des la premiere session
    # transformerait le garde-fou en bruit de fond.
    n = len(tpl.splitlines())
    verifier(n <= seuil - 30,
             f"template CLAUDE projet : {n} lignes pour un seuil d'alerte à {seuil} — "
             f"trop peu de marge, un projet rempli déclencherait l'avertissement d'emblée")

# 17. Modele explicite par agent (S-35, audit externe C-01) : sans `model:`,
#     Claude Code retombe sur `inherit` et un agent a fort volume / faible
#     exigence de raisonnement (documentaliste) tourne au tarif du
#     modele de session. La ligne doit etre ECRITE, meme quand elle vaut
#     `inherit` : c'est ce qui la rend revisable et empeche qu'elle se reperde
#     au prochain agent cree.
MODELES_VALIDES = {"inherit", "haiku", "sonnet", "opus", "fable"}
for dossier in (*DOSSIERS_AGENTS, RACINE / "specialisations"):
    for f in sorted(dossier.glob("*.md")):
        m = re.search(r"^model:\s*(\S+)\s*$", f.read_text(encoding="utf-8"), re.M)
        verifier(m is not None, f"{f.name} : frontmatter sans 'model:' (S-35)")
        if m:
            verifier(m.group(1) in MODELES_VALIDES or m.group(1).startswith("claude-"),
                     f"{f.name} : model '{m.group(1)}' inconnu (attendu : "
                     f"{'/'.join(sorted(MODELES_VALIDES))} ou un id claude-*)")

# 18. Le seuil anti-delegation-triviale vit dans la COUCHE QUI PRIME (S-32,
#     audit externe C-02). La CHARTE prime explicitement sur le CLAUDE.md
#     projet : tant que la regle n'existait qu'au gabarit, elle perdait
#     l'arbitrage par construction face au « la session principale ne fait pas
#     le travail specialise » de la CHARTE SS6.
try:
    charte = (RACINE / "CHARTE.md").read_text(encoding="utf-8")
    gabarit = (RACINE / "templates/CLAUDE.projet.template.md").read_text(encoding="utf-8")
    for nom, txt in (("CHARTE.md", charte), ("CLAUDE.projet.template.md", gabarit)):
        verifier("déléguer du trivial" in txt.lower(),
                 f"{nom} : seuil anti-delegation-triviale absent — la regle doit "
                 f"figurer dans la couche 1 (CHARTE) autant qu'au gabarit (S-32)")
except Exception as e:
    echecs.append(f"seuil de delegation : {e}")

# 19. Tout chemin de fichier cite par un SKILL.md est ATTEIGNABLE DEPUIS UN
#     DEPOT PROJET (S-19, audit externe C-11). Ferme la classe « consigne
#     inexecutable cote equipe » : fme-tse prescrivait `scripts/
#     generer_doc_html.py`, qui existe cote socle mais n'a jamais ete livre.
#     Verifier l'existence dans le socle ne suffit donc PAS — c'est ce qui
#     rendait le defaut invisible. Un projet ne voit que deux choses :
#       - le plugin installe, via ${CLAUDE_PLUGIN_ROOT} -> plugins/geoid/ ;
#       - le residuel merge depuis le template (CHARTE.md, templates/,
#         specialisations/ — cf. scripts/sync_template.py).
#     Tout autre prefixe est un chemin du depot socle, invisible cote equipe.
RESIDUEL_TEMPLATE = ("CHARTE.md", "templates/", "specialisations/")
MOTIF_CHEMIN = re.compile(r"`([^`\s]*/[^`\s]*\.(?:md|py|css|json|html|yml|fmw))`")
for f in sorted(DOSSIER_SKILLS.glob("*/SKILL.md")):
    for cite in sorted(set(MOTIF_CHEMIN.findall(f.read_text(encoding="utf-8")))):
        if any(c in cite for c in "[<{"):
            continue  # placeholder documentaire, pas un chemin reel
        if cite.startswith("${CLAUDE_PLUGIN_ROOT}"):
            rel = cite.replace("${CLAUDE_PLUGIN_ROOT}", "plugins/geoid").lstrip("/")
        elif cite.startswith(RESIDUEL_TEMPLATE):
            rel = cite
        else:
            echecs.append(
                f"{f.parent.name}/SKILL.md : chemin cite '{cite}' hors du perimetre "
                f"livre — un depot projet ne voit que ${{CLAUDE_PLUGIN_ROOT}}/… et le "
                f"residuel du template ({', '.join(RESIDUEL_TEMPLATE)})")
            continue
        verifier((RACINE / rel).exists(),
                 f"{f.parent.name}/SKILL.md : chemin cite '{cite}' introuvable "
                 f"(attendu dans le socle : {rel})")

if echecs:
    print("ECHECS d'integrite :")
    for e in echecs:
        print("  -", e)
    sys.exit(1)
print("Integrite du socle : OK")
