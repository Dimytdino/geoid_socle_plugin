#!/usr/bin/env python3
"""Évaluations de déclenchement des skills GéoID (S-13).

Un skill ne vaut que par sa `description` : c'est elle seule qui décide s'il
s'active. Ces évals figent, pour chaque skill publié, un jeu de prompts
DÉCLENCHEURS (le skill DOIT s'activer) et NON-DÉCLENCHEURS (il NE doit PAS
s'activer — soit parce qu'un skill voisin est attendu, soit parce que la
demande est hors périmètre). Les jeux vivent dans `evals/<skill>.eval.json`.

Le déclenchement réel dépend d'un LLM avec le skill installé ; il n'est donc
pas testable hors ligne. Ce script fait deux choses, toutes deux hors ligne :

  --valider  (défaut) : contrôle la STRUCTURE et la COUVERTURE des jeux
             (un fichier par skill publié, seuils de prompts, présence des
             deux types de non-déclencheurs, pas de doublon, renvois valides).
             C'est ce que lance la CI.
  --rapport            : imprime, skill par skill, les prompts à copier-coller
             dans une conversation NEUVE avec le plugin installé, pour mener
             le test de déclenchement réel (protocole : evals/README.md).

Usage :
  python3 scripts/evaluer_declenchement.py            # valide, sortie 1 si échec
  python3 scripts/evaluer_declenchement.py --rapport   # protocole de test manuel
"""
import json, pathlib, sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIER_SKILLS = RACINE / "plugins/geoid/skills"
DOSSIER_EVALS = RACINE / "evals"

# Seuils de couverture minimale par skill.
MIN_DECLENCHEURS = 5
MIN_NON_DECLENCHEURS = 3


def _skills_publies():
    """Noms des skills réellement embarqués par le plugin geoid."""
    if not DOSSIER_SKILLS.exists():
        return set()
    return {d.name for d in DOSSIER_SKILLS.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()}


def _norm(prompt):
    return " ".join(prompt.split()).casefold()


def valider(racine=RACINE):
    """Retourne la liste des messages d'échec (vide = tout est conforme)."""
    echecs = []
    dossier_skills = racine / "plugins/geoid/skills"
    dossier_evals = racine / "evals"
    publies = {d.name for d in dossier_skills.iterdir()
               if d.is_dir() and (d / "SKILL.md").exists()} if dossier_skills.exists() else set()

    # 1. Chaque skill publié a son fichier d'éval.
    for nom in sorted(publies):
        if not (dossier_evals / f"{nom}.eval.json").exists():
            echecs.append(f"skill publié sans éval : evals/{nom}.eval.json manquant")

    # 2. Chaque fichier d'éval est valide, couvre son skill, sans orphelin.
    for f in sorted(dossier_evals.glob("*.eval.json")) if dossier_evals.exists() else []:
        attendu = f.name[:-len(".eval.json")]
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            echecs.append(f"{f.name} : JSON invalide ({e})")
            continue

        if data.get("skill") != attendu:
            echecs.append(f"{f.name} : champ 'skill' ({data.get('skill')!r}) != nom de fichier ({attendu!r})")
        if attendu not in publies:
            echecs.append(f"{f.name} : éval orpheline (aucun skill publié '{attendu}')")

        decl = data.get("declencheurs") or []
        non = data.get("non_declencheurs") or []
        if not isinstance(decl, list) or not isinstance(non, list):
            echecs.append(f"{f.name} : 'declencheurs' et 'non_declencheurs' doivent être des listes")
            continue

        if len(decl) < MIN_DECLENCHEURS:
            echecs.append(f"{f.name} : {len(decl)} déclencheur(s) < minimum {MIN_DECLENCHEURS}")
        if len(non) < MIN_NON_DECLENCHEURS:
            echecs.append(f"{f.name} : {len(non)} non-déclencheur(s) < minimum {MIN_NON_DECLENCHEURS}")

        # Chaque item : prompt + pourquoi non vides.
        for etiquette, items in (("declencheurs", decl), ("non_declencheurs", non)):
            for i, it in enumerate(items):
                if not isinstance(it, dict) or not (it.get("prompt") or "").strip():
                    echecs.append(f"{f.name} : {etiquette}[{i}] sans 'prompt'")
                if isinstance(it, dict) and not (it.get("pourquoi") or "").strip():
                    echecs.append(f"{f.name} : {etiquette}[{i}] sans 'pourquoi' (justifier le libellé)")

        # Les non-déclencheurs doivent couvrir LES DEUX risques :
        #  - le sur-déclenchement vers un skill voisin (skill_attendu renseigné),
        #  - le hors-périmètre pur (aucun skill_attendu).
        avec_voisin = [n for n in non if isinstance(n, dict) and n.get("skill_attendu")]
        sans_voisin = [n for n in non if isinstance(n, dict) and not n.get("skill_attendu")]
        if not avec_voisin:
            echecs.append(f"{f.name} : aucun non-déclencheur 'frontière' (avec 'skill_attendu') — "
                          f"le sur-déclenchement vers un skill voisin n'est pas testé")
        if not sans_voisin:
            echecs.append(f"{f.name} : aucun non-déclencheur hors-périmètre (sans 'skill_attendu')")

        # Un skill_attendu doit viser un autre skill publié.
        for n in avec_voisin:
            cible = n.get("skill_attendu")
            if cible == attendu:
                echecs.append(f"{f.name} : 'skill_attendu' == skill évalué ({cible}) — incohérent")
            elif cible not in publies:
                echecs.append(f"{f.name} : 'skill_attendu' inconnu ({cible!r}) — pas un skill publié")

        # Pas de doublon de prompt (dans un fichier, tous types confondus) :
        # un même libellé ne peut être à la fois déclencheur et non-déclencheur.
        vus = {}
        for etiquette, items in (("declencheurs", decl), ("non_declencheurs", non)):
            for it in items:
                if not isinstance(it, dict):
                    continue
                cle = _norm(it.get("prompt") or "")
                if not cle:
                    continue
                if cle in vus:
                    echecs.append(f"{f.name} : prompt en double ({vus[cle]} et {etiquette}) : {it.get('prompt')!r}")
                else:
                    vus[cle] = etiquette

    return echecs


def rapport(racine=RACINE):
    """Imprime le protocole de test manuel, prompts prêts à copier-coller."""
    dossier_evals = racine / "evals"
    fichiers = sorted(dossier_evals.glob("*.eval.json")) if dossier_evals.exists() else []
    if not fichiers:
        print("Aucun jeu d'éval dans evals/.")
        return
    print("Protocole : ouvrir une conversation NEUVE avec le plugin geoid installé,")
    print("coller chaque prompt, noter si le skill attendu se déclenche.")
    print("Détail et grille de résultats : evals/README.md\n")
    for f in fichiers:
        data = json.loads(f.read_text(encoding="utf-8"))
        nom = data.get("skill", f.name)
        decl = data.get("declencheurs") or []
        non = data.get("non_declencheurs") or []
        print(f"══ {nom} (v{data.get('version_skill_evaluee', '?')}) — "
              f"{len(decl)} déclencheurs / {len(non)} non-déclencheurs ══")
        print(f"  DOIT déclencher « {nom} » :")
        for it in decl:
            print(f"    • {it.get('prompt')}")
        print("  NE doit PAS déclencher :")
        for it in non:
            cible = it.get("skill_attendu")
            suffixe = f"  → attendu : {cible}" if cible else "  → attendu : aucun skill"
            print(f"    • {it.get('prompt')}{suffixe}")
        print()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--valider"
    if mode == "--rapport":
        rapport()
        return
    if mode not in ("--valider", ""):
        sys.exit(f"Mode inconnu : {mode} (attendu : --valider ou --rapport)")
    echecs = valider()
    if echecs:
        print("ÉCHECS de validation des évals de déclenchement :")
        for e in echecs:
            print("  -", e)
        sys.exit(1)
    n = len(list((DOSSIER_EVALS).glob("*.eval.json"))) if DOSSIER_EVALS.exists() else 0
    print(f"Évals de déclenchement : OK ({n} skill(s) couvert(s), {len(_skills_publies())} publié(s))")


if __name__ == "__main__":
    main()
