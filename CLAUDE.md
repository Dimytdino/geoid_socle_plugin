<!-- ════════════════════════════════════════════════════════════════
     CLAUDE.md — BOOTSTRAP (projet non cadré)
     Ce fichier est remplacé par /cadrer-projet.
     ════════════════════════════════════════════════════════════════ -->

# Projet GéoID — non cadré

⚠️ **Ce projet n'a pas encore été cadré.**

Règles applicables dès maintenant :
1. Lire `CHARTE.md` (règles transverses du pôle GéoID) — elle s'applique
   intégralement.
2. Installer le plugin d'équipe s'il ne l'est pas encore
   (`/plugin marketplace add TSE-Pole-Geomatique/geoid_socle_plugin` puis
   `/plugin install geoid@geoid-socle`) : c'est lui qui apporte les agents,
   skills et commandes du pôle.
3. Avant toute production significative, proposer à l'utilisateur de lancer
   la commande **`geoid:cadrer-projet`**, qui mènera l'entretien de cadrage
   et remplacera ce fichier par le CLAUDE.md du projet (objectif, données,
   livrables, équipe d'agents retenue, points à arbitrer).
4. En attendant le cadrage : répondre aux questions, explorer l'existant,
   mais ne pas engager de développement structurant.

Agents fournis par le plugin `geoid` (invocables `@geoid:<agent>`) :
`architecte`, `developpeur`, `analyste_sig`, `revieweur`, `documentaliste`,
`chef_projet`, `mentor`. Les agents skill-builder (`interviewer_skill`,
`redacteur_skill`, `critique_skill`) vivent dans le plugin `geoid-meta`,
réservé au mainteneur du socle : ils sont absents des projets d'équipe par
construction. Des spécialisations du développeur sont disponibles dans
`specialisations/` (template résiduel) et la seule retenue est copiée au
cadrage selon la famille de projet.
