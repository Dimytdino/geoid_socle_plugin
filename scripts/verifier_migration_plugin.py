#!/usr/bin/env python3
"""Vérifier la migration d'un projet GéoID vers le mode plugin (socle 0.5.0+).

À lancer DANS le dépôt d'un projet (ou avec --projet CHEMIN) après avoir
installé le plugin `geoid` depuis la marketplace. Détecte les copies locales
sous `.claude/` qui font désormais doublon avec les composants fournis par le
plugin (agents génériques, commandes, skills du pôle) — cf. checklist de
migration du CHANGELOG 0.5.0 et ADR-001 §4.2.

Ne touche à rien : il signale, l'humain supprime. Sortie non nulle si un
doublon subsiste ou si l'en-tête de version du CLAUDE.md est absent/non
renseigné.

Usage : python3 scripts/verifier_migration_plugin.py [--projet CHEMIN]
"""
import sys, pathlib

# ── Composants fournis par les plugins (source de vérité = la marketplace) ──
# Ces listes DOIVENT rester synchrones avec plugins/geoid et plugins/geoid-meta ;
# tests/test_socle_integrity.py (bloc 9) le vérifie côté socle pour empêcher
# toute dérive. Le script reste ainsi autonome dans un dépôt projet (qui n'a
# pas les dossiers plugins/).
AGENTS_GEOID = {
    "architecte", "developpeur", "analyste_sig", "revieweur",
    "documentaliste", "chef_projet", "mentor",
}
AGENTS_GEOID_META = {"interviewer_skill", "redacteur_skill", "critique_skill"}
COMMANDS_GEOID = {"cadrer-projet", "cloturer-session"}
COMMANDS_GEOID_META = {"creer-skill", "revue-socle"}
SKILLS_GEOID = {"conventions-sig-tse", "environnement-arcgis-tse", "fme-tse"}

AGENTS_PLUGIN = AGENTS_GEOID | AGENTS_GEOID_META
COMMANDS_PLUGIN = COMMANDS_GEOID | COMMANDS_GEOID_META


def analyser(projet: pathlib.Path):
    """Retourne (doublons, a_conserver, problemes_version)."""
    claude = projet / ".claude"
    doublons = []      # (chemin relatif, raison)
    conserves = []     # fichiers locaux légitimes détectés (info)

    # Agents : doublon si le nom correspond à un agent du plugin. Les
    # spécialisations copiées au cadrage (developpeur_back_geo, _front_carto,
    # _etl) et tout agent projet sur mesure ne matchent pas → conservés.
    for f in sorted((claude / "agents").glob("*.md")) if (claude / "agents").is_dir() else []:
        if f.stem in AGENTS_PLUGIN:
            plugin = "geoid" if f.stem in AGENTS_GEOID else "geoid-meta"
            doublons.append((f.relative_to(projet),
                             f"agent fourni par le plugin {plugin} (@{plugin}:{f.stem})"))
        else:
            conserves.append(f.relative_to(projet))

    # Commandes : doublon si le nom (sans extension) est fourni par un plugin.
    for f in sorted((claude / "commands").glob("*.md")) if (claude / "commands").is_dir() else []:
        if f.stem in COMMANDS_PLUGIN:
            plugin = "geoid" if f.stem in COMMANDS_GEOID else "geoid-meta"
            doublons.append((f.relative_to(projet),
                             f"commande fournie par le plugin {plugin} ({plugin}:{f.stem})"))
        else:
            conserves.append(f.relative_to(projet))

    # Skills : doublon si le dossier porte le nom d'un skill du pôle.
    for d in sorted((claude / "skills").iterdir()) if (claude / "skills").is_dir() else []:
        if d.is_dir() and d.name in SKILLS_GEOID:
            doublons.append((d.relative_to(projet),
                             "skill du pôle fourni par le plugin geoid"))
        elif d.is_dir():
            conserves.append(d.relative_to(projet))

    # En-tête de version du CLAUDE.md (ADR-001c : deux champs).
    problemes_version = []
    claude_md = projet / "CLAUDE.md"
    if not claude_md.exists():
        problemes_version.append("CLAUDE.md introuvable (projet non cadré ?)")
    else:
        txt = claude_md.read_text(encoding="utf-8", errors="ignore")
        if "Version socle" not in txt or "plugin geoid" not in txt:
            problemes_version.append(
                "en-tête « Version socle — plugin geoid … ; template résiduel … » absent "
                "(ADR-001c) : l'ajouter en en-tête du CLAUDE.md")
        if "{{VERSION_PLUGIN_GEOID}}" in txt or "{{VERSION_TEMPLATE}}" in txt:
            problemes_version.append(
                "l'en-tête de version contient encore un gabarit {{…}} non renseigné")

    return doublons, conserves, problemes_version


def main():
    projet = pathlib.Path.cwd()
    args = sys.argv[1:]
    if args:
        if args[0] == "--projet" and len(args) == 2:
            projet = pathlib.Path(args[1])
        else:
            sys.exit("Usage : python3 scripts/verifier_migration_plugin.py [--projet CHEMIN]")
    projet = projet.resolve()

    if not projet.is_dir():
        sys.exit(f"Erreur : dossier projet introuvable : {projet}")

    doublons, conserves, problemes_version = analyser(projet)

    print(f"Vérification de migration plugin — projet : {projet}")
    print("-" * 60)

    if doublons:
        print("\n⚠️  DOUBLONS à supprimer (fournis désormais par le plugin) :")
        for chemin, raison in doublons:
            print(f"  - {chemin}  — {raison}")
        print("\n  → supprimer ces copies locales : un composant local non préfixé")
        print("    coexisterait avec sa version plugin et divergerait en silence.")
    else:
        print("\n✅ Aucun doublon plugin/local sous .claude/.")

    if conserves:
        print("\nℹ️  Conservés (locaux légitimes — spécialisation ou sur-mesure projet) :")
        for chemin in conserves:
            print(f"  - {chemin}")

    if problemes_version:
        print("\n⚠️  En-tête de version (CLAUDE.md) :")
        for p in problemes_version:
            print(f"  - {p}")
    else:
        print("\n✅ En-tête de version du CLAUDE.md renseigné.")

    print("\nRappel — à CONSERVER dans tous les cas : CLAUDE.md, .claude/settings.json")
    print("(+ .local.json), docs/, la spécialisation .claude/agents/developpeur_*.md,")
    print("CHARTE.md. Relancer Claude Code après nettoyage (chargement au démarrage).")

    probleme = bool(doublons or problemes_version)
    print("\n" + ("RÉSULTAT : migration incomplète (voir ci-dessus)." if probleme
                   else "RÉSULTAT : migration propre."))
    sys.exit(1 if probleme else 0)


if __name__ == "__main__":
    main()
