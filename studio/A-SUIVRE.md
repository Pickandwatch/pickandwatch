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

## Plan de croissance validé le 25/10/2026 (hors Threads, X/TikTok et canal d'alerte : refusés)

Fait le 25/10 : guide épinglé (publié 25/10), Reel du lundi (routine § 4), pages Mon équipe,
agendas .ics, page NBA Cup (classement caché), routine Hors parquet (§ 5 + tâches jeudi/vendredi),
liste des Français (data/francais.json, `valide: false` tant qu'Alexandre n'a pas validé).

À faire, par ordre :
- **27/10** « Nouveau sur le site » (post + story) et **28/10** explication NBA Cup : en attente de
  validation et du test iPhone d'Alexandre (abonnement agenda, « + Agenda »).
- **Semaine du 26/10 — Claude** : liste de 15 médias, podcasts et créateurs basket français à
  approcher (tags et publications à deux) + messages d'approche rédigés pour Alexandre ; Reel
  « meilleurs podcasts basket » (idée d'Alexandre du 25/10).
- **Après le 27/10 — Alexandre** : sponsoriser le guide (~20 €, 25-44 ans) ; Claude calcule le coût
  par abonné à partir de ses captures. Règle : budget ~50 €/mois, couper au-delà de 0,80 €/abonné.
- **Novembre — Claude** : plan du site pour Google (sitemap.xml, titres et descriptions des pages
  équipes et matchs) ; Alexandre ouvre Google Search Console et ajoute la ligne TXT chez OVH.
- **Novembre — Claude** : dossier de présentation pour beIN SPORTS et Prime Video (chiffres, captures,
  ce qu'on fait pour leurs diffusions) ; pitch presse et liste de journalistes. Envoi : Alexandre.
- **Séance Meta (Alexandre, 10 min)** : ajouter `instagram_manage_comments` (réponses aux
  commentaires rédigées par Claude, validées par Alexandre) et `instagram_manage_insights` (bilan
  mensuel automatique). Pas de Threads.
- **Grands rendez-vous** (contenus préparés ~5 jours avant) : quarts NBA Cup 4-5 déc., finale 11 déc.
  (Indianapolis), Christmas Day 25 déc. (Knicks – Spurs 18h), Paris Game 14 janv. (dispositif
  complet), Manchester 17 janv., All-Star, date limite des transferts, play-in et playoffs.
