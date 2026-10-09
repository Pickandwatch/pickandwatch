# Routine éditoriale quotidienne Pick & Watch

Ce fichier est le mode d'emploi des tâches programmées. Il fait foi : toute session qui
prépare du contenu Pick & Watch le lit en entier avant de commencer.

## Règles absolues

- **Zéro spoiler.** Aucun score, aucun vainqueur, aucun écart ne sort jamais, nulle part :
  site, légende, slide, message à Alexandre compris. Les scores peuvent être lus en interne
  pour juger un match ; ils ne sont jamais écrits dans un fichier du dépôt.
- **N'invente rien.** Chaque fait d'un brief ou d'un verdict (transfert, blessure, minutes
  jouées, retour) est vérifié dans une source ouverte et lue. Dans le doute, on retire.
- **Validation.** Alexandre valide dans la conversation de la tâche. La notification a
  toujours pour objet : « Post P&W à valider ». Rien d'éditorial (étoiles, briefs,
  verdicts) n'est poussé dans `data/` avant sa validation, sauf la règle de 18h50 ci-dessous.
- **Publication Instagram automatique à 19h** si Alexandre n'a pas répondu, sauf s'il a
  demandé l'annulation (`"statut": "annule"` dans `posts/AAAA-MM-JJ/post.json`).
- Jamais de mot de passe ni de clé dans la conversation. La clé Instagram est un secret GitHub.
- Ton : direct, sobre, tutoiement du lecteur, pas de superlatifs. Charte « papier ».

## Mise en route d'une session

```
cd ~ && [ -d pickandwatch ] || git clone https://github.com/Pickandwatch/pickandwatch
cd pickandwatch && git pull --rebase
python3 -c "import PIL, playwright" || pip install --break-system-packages pillow playwright
```
Lire ensuite `studio/A-SUIVRE.md` : consignes éditoriales en cours d'Alexandre.
Chromium est préinstallé (ne pas lancer `playwright install`). Dates : la « nuit D » est le
soir D en France (matchs de D 12h à D+1 12h, heure de Paris).

## 1. Le matin (10h) : les verdicts de la nuit D-1

1. Lire `data/nuits/<D-1>.json` (matchs, identifiants, diffusions).
2. Se faire un avis sur chaque match, en interne :
   - feuille de match ESPN (`site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event=<id>`,
     en-tête `User-Agent: Mozilla/5.0`) : minutes des stars, écart, dernier quart-temps ;
   - comptes rendus NBA.com et ESPN.com ;
   - l'épisode CQFR du podcast BasketSession (flux Acast, émission `67ebdac502e789100f7f411e`),
     transcrit avec `studio/transcrire.py` si `faster-whisper` est disponible, sinon on passe ;
   - réactions sur Instagram et X via la recherche web ;
   - L'Équipe uniquement par les liens qu'Alexandre envoie (le site n'est pas accessible aux outils).
3. Verdict par match : `replay` (à voir en replay), `resume` (le résumé suffit) ou `zapper`.
   Texte de 1 à 2 phrases qui dit pourquoi, sans score ni vainqueur. Pas de « match serré
   jusqu'au bout gagné par… » : on parle de ce qui vaut le coup d'œil (un retour, un rookie,
   un dernier quart-temps à regarder).
4. Proposer les verdicts dans la conversation, envoyer la notification « Post P&W à valider ».
5. Après validation : écrire `data/verdicts/<D-1>.json` (format de `data/verdicts/2026-10-07.json`,
   `"_statut": "validé le …"`), commit, push, puis lancer le site :
   `gh api -X POST repos/Pickandwatch/pickandwatch/actions/workflows/programme.yml/dispatches -f ref=main`.

## 2. L'après-midi (15h30) : étoiles, briefs et carrousel de la nuit D

1. `data/nuits/<D>.json` est produit par le robot vers 15h20. S'il manque, lancer
   `programme.yml` (commande ci-dessus) et attendre.
2. **Étoiles** (grille validée) : par équipe, sur la saison précédente,
   - classement : top 4 de conférence = 2, 5e à 8e = 1, sinon 0 ;
   - playoffs : Finale = 3, finale de conférence = 2, demi-finale = 1, sinon 0 ;
   - aura des stars : superstar = 3, All-Star = 2, bons joueurs = 1, reconstruction = 0.
   Match = somme des deux équipes, + 2 si événement (retour de blessure, débuts d'une recrue
   majeure, Français à suivre, match à l'étranger…). 9 et plus = ★★★, 6 à 8 = ★★, 5 et moins = ★.
   **Un seul ★★★ par nuit** (départager : diffusion TV française, puis événement). Noter le
   calcul dans `"score"` de chaque match. Réutiliser et compléter `data/grille-equipes.json`
   pour que la note d'une équipe reste la même d'un soir à l'autre.
3. **Briefs** : une à deux phrases d'enjeu par match, sourcées (NBA.com, previews ESPN).
   Les commentateurs ne sont indiqués que s'ils sont annoncés par le diffuseur.
4. **Carrousel** : écrire `posts/<D>/spec.json` sur le modèle de `posts/2026-10-08/spec.json`
   (couverture : le ★★★ en tête puis les autres matchs triés par heure ; une slide par match
   ★★★ et ★★, au plus 4 ; couleurs de l'équipe à domicile). Puis :
   `python3 studio/carrousel.py posts/<D>/spec.json` → `01.jpg` … ; le script signale tout
   débordement. Regarder chaque image avant d'aller plus loin.
5. **Légende** : modèle de `posts/2026-10-08/post.json`. Doit passer le garde-fou anti-score
   (`pipeline.instagram.SCORE_RE`) : écrire les heures « 1h30 », jamais « 01:30 – 02:00 ».
6. Écrire `posts/<D>/post.json` :
   `{"publier_a": "<D>T19:00:00+02:00", "statut": "propose", "images": [...], "legende": "..."}`
   (heure d'hiver à partir du 25 octobre : `+01:00`). Garder l'éditorial du site dans
   `posts/<D>/editorial.json` (même format que `data/editorial/`).
7. Commit et push de `posts/<D>/`, lancer `programme.yml`, vérifier que chaque
   `https://pickandwatch.fr/posts/<D>/0N.jpg` répond 200.
8. Envoyer les images et la légende dans la conversation (SendUserFile + texte), puis la
   notification « Post P&W à valider — publication automatique à 19h sans réponse de ta part ».

**Si Alexandre répond** : « ok » → `"statut": "valide"` et copier `posts/<D>/editorial.json`
vers `data/editorial/<D>.json` (`"_statut": "validé le …"`), push, relancer le site.
Une correction → refaire l'image ou la légende, push. « Annule » → `"statut": "annule"`, push.

**Matchs en journée** (Macao, Europe, matinées du week-end) : un match qui commence avant
19h le lendemain est déjà joué quand le carrousel de sa nuit est publié. Annonce-le donc dans
le carrousel de la veille (« demain à 12h10 en direct sur … »), avec son heure et sa chaîne.

## 3. 18h50 : filet de sécurité

Si le post de D est encore `propose` : copier `posts/<D>/editorial.json` vers
`data/editorial/<D>.json` avec `"_statut": "publié sans réponse (règle de 19h)"`, push,
relancer le site (le site et le post doivent dire la même chose). Si `annule` : ne rien faire.
Après 19h05, vérifier le dernier passage de `instagram.yml` et le `media_id` dans `post.json`.
Si rien n'est parti à 19h15, lancer `instagram.yml` en mode `publish-due`
(`gh api -X POST …/workflows/instagram.yml/dispatches -f ref=main -f inputs[mode]=publish-due`)
et prévenir Alexandre en cas d'échec.
