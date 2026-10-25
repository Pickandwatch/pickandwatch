# À suivre : consignes éditoriales d'Alexandre

Chaque session qui écrit des briefs, des verdicts ou une légende lit ce fichier d'abord.
Une consigne est retirée quand elle est traitée (noter la date dans le commit).

- **Diffuseurs (Alexandre, 17/10)** : être vigilant sur les chaînes. Il pense que tous les matchs
  sont disponibles en replay (VO) sur Amazon : non confirmé à ce jour (aucune source lue ne le dit).
  Chercher une source Amazon / Prime Video France qui le confirme ; tant que ce n'est pas fait,
  ne pas l'écrire. Voir la règle « Chaînes » de ROUTINE.md.
  Vérifié le 21/10 (Insidebasket 20/10/2026, SportBuzzBusiness 19/10/2026) : Prime inclut
  86 matchs de saison régulière (doubles affiches du vendredi dès le 23/10, jeudis dès janvier,
  samedis dès février, NBA Cup, play-in, une partie des playoffs), pas tous les matchs. Tous les
  matchs en direct et en replay : NBA League Pass seulement (payant, aussi via Prime Video avec
  un abonnement supplémentaire). Alexandre pense que Prime diffuse « généralement tous les matchs »
  (21/10) : toujours non confirmé, ne pas l'écrire. beIN : jusqu'à 9 matchs par semaine.

- **Prime Video : repérage automatique** (22/10 ; règle CONFIRMÉE le 25/10, clé passée à `true` : Insidebasket 20/10 confirme Knicks – 76ers le 30/10 et indique 67 matchs du calendrier américain + 20 affiches en prime time européen à annoncer — les saisir dès leur annonce). Le robot repère les matchs « NBA on Prime » des
  États-Unis dans le calendrier ESPN (diffusion nationale « Prime Video »). Saison 2025-26 : la
  France avait ces matchs + 20 affiches propres (86 au total) ; 2026-27 : 86 annoncés, règle à
  confirmer. Tant que `prime_usa_en_france` vaut `false` dans `data/diffuseurs.json`, ces matchs
  apparaissent seulement dans les points à vérifier : ne pas écrire « Prime Video » sans
  confirmation. Alexandre vérifie dans son application Prime Video France si Knicks – Celtics
  (nuit du 23 au 24/10, 1h) et Rockets – Spurs (3h30) y figurent ; si oui, passer la clé à `true`.
  Les affiches propres à la France (dimanches 19h, matchs de Paris et Manchester) se saisissent
  à la main dans `matchs` dès leur annonce par Prime Video France.
