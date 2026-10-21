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
  toujours pour objet : « Post P&W à valider ». Rien d'éditorial (étoiles, briefs) n'est
  poussé dans `data/` avant sa validation, sauf la règle de 18h50 ci-dessous.
  **Exception : les verdicts du matin sont publiés sans attendre** (consigne d'Alexandre du
  14 octobre 2026) ; il les corrige après coup s'il le souhaite.
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

## 1. Le matin (7h15) : les verdicts de la nuit D-1

Alexandre veut les verdicts en ligne le plus tôt possible (consigne du 21 octobre 2026) :
la tâche part à 7h12, heure de Paris, et vise une mise en ligne avant 8h. Si un match n'est
pas encore terminé (`STATUS_FINAL` sur ESPN), publier tout de suite les autres, puis revérifier
toutes les 15 minutes et ajouter le dernier verdict dès la fin du match. Si
`data/verdicts/<D-1>.json` existe déjà (publié à la main), ne pas le réécrire : vérifier
seulement que le site l'affiche.

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
4. Publier tout de suite, sans attendre de validation : écrire `data/verdicts/<D-1>.json`
   (format de `data/verdicts/2026-10-07.json`, `"_statut": "publié le … (sans validation préalable)"`),
   vérifier qu'aucun texte ne déclenche `pipeline.instagram.SCORE_RE`, commit, push, puis lancer le site :
   `gh api -X POST repos/Pickandwatch/pickandwatch/actions/workflows/programme.yml/dispatches -f ref=main`
   (ou l'outil GitHub `actions_run_trigger`, méthode `run_workflow`). Vérifier que la rubrique
   « Verdicts d'hier » de https://pickandwatch.fr/ affiche bien les verdicts.
5. **Story Instagram de 8h** (validée par Alexandre le 21 octobre 2026 : publication automatique,
   sans validation). Avant le push de l'étape 4, lancer `python3 studio/story.py <D-1>` : il écrit
   `posts/<D-1>-verdicts/` (01.jpg = récapitulatif de la nuit, puis une carte par match, tous
   verdicts confondus : replay, résumé, zapper — consigne d'Alexandre du 21/10 ; 1080x1920) et `post.json` (`"type": "story"`, `publier_a` = D à 8h, ou dans 15 min si
   8h est passé). Regarder chaque image ; le script signale tout débordement et bloque tout score.
   Pousser avec les verdicts, relancer le site, vérifier que `https://pickandwatch.fr/posts/<D-1>-verdicts/01.jpg`
   répond 200. Le robot `instagram.yml` publie les stories à l'heure (une par image, dans l'ordre ;
   un nouvel essai reprend après la dernière story partie). Les passages programmés de GitHub
   partent souvent en retard ou sautent : entre 7h47 et 7h59, lancer aussi `instagram.yml` en mode
   `publish-due` (il attend 8h pile) ; si la story est en retard sur 8h, le lancer tout de suite. Pas de sticker lien : l'API ne le permet
   pas, la carte renvoie vers pickandwatch.fr et le lien en bio. Après 8h05, vérifier `"statut": "publie"`
   (après `git pull`) ; sinon appliquer les règles d'échec de la section 3.
   Rediffusions (consigne d'Alexandre du 21/10 : tous les matchs passent sur beIN, rediffusions dès
   le matin) : le robot relit chaque matin le guide beIN pour la nuit D-1 (`refresh_tv`). Les créneaux
   « Basket-ball : NBA » sans affiche après les directs sont annoncés comme « rediffusions de matchs
   de la nuit », sans jamais deviner lequel. Lancer `programme.yml` AVANT `story.py` pour en profiter.
   Si Alexandre corrige un verdict avant 8h : relancer `story.py`, push. Après publication, une story
   ne se modifie pas : seul le site est corrigé.
6. Présenter les verdicts dans la conversation et envoyer la notification « Verdicts P&W publiés »
   (une ligne par match, et la story : programmée ou publiée). Si Alexandre corrige : modifier le
   fichier, push, relancer le site.

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
   **Chaînes** : le robot ne lit que le guide TV de beIN SPORTS. Prime Video diffuse aussi des
   matchs NBA en France (inclus dans Prime, depuis 2025-26) : vérifier chaque soir le programme
   NBA de Prime Video France (page Prime Video ou annonce Amazon, recoupée avec agendatv-basket.com)
   et l'ajouter à la main dans `data/diffuseurs.json` (`"live"`, `"source"`). Ne jamais écrire
   « pas de chaîne TV française » sans avoir vérifié Prime Video. Un replay n'est annoncé que
   s'il est confirmé par une source lue (chaîne, horaire ou plateforme) ; le NBA League Pass
   (y compris via Prime Video Channels) est une option payante, jamais présenté comme « Prime ».
3. **Briefs** : une à deux phrases d'enjeu par match, sourcées (NBA.com, previews ESPN).
   Les commentateurs ne sont indiqués que s'ils sont annoncés par le diffuseur.
4. **Carrousel** : écrire `posts/<D>/spec.json` sur le modèle de `posts/2026-10-08/spec.json`
   (couverture : le ★★★ en tête puis les autres matchs triés par heure ; une slide par match
   ★★★ et ★★, au plus 4 ; couleurs de l'équipe à domicile). Puis :
   `python3 studio/carrousel.py posts/<D>/spec.json` → `01.jpg` … ; le script signale tout
   débordement. Regarder chaque image avant d'aller plus loin.
5. **Légende** : modèle de `posts/2026-10-08/post.json`. Doit passer le garde-fou anti-score
   (`pipeline.instagram.SCORE_RE`) : écrire les heures « 1h30 », jamais « 01:30 – 02:00 ».
   **2 200 caractères au maximum** (limite Instagram, espaces et sauts de ligne compris) :
   vérifier `len(legende)` ; au-delà, Meta refuse le post et rien ne part. Viser 2 000.
6. Écrire `posts/<D>/post.json` :
   `{"publier_a": "<D>T19:00:00+02:00", "statut": "propose", "images": [...], "legende": "..."}`
   (heure d'hiver à partir du 25 octobre : `+01:00`). Garder l'éditorial du site dans
   `posts/<D>/editorial.json` (même format que `data/editorial/`).
7. **Story du soir** (demandée par Alexandre le 21 octobre 2026) : lancer
   `python3 studio/story_soir.py <D>`. Il reprend les images du carrousel, chacune centrée sur un
   fond 1080x1920 de sa couleur, dans `posts/<D>-story/` (`post.json` : `"type": "story"`,
   `"suit": "<D>"`, même heure, même statut). Mêmes règles que le carrousel : publication
   automatique à 19h sans réponse ; le robot annule la story si le carrousel est `annule`.
   Relancer le script après toute correction d'image du carrousel. Pas de sticker lien (API).
8. Lancer `python3 -m pipeline.instagram verify` (contrôle hors ligne de la légende et des
   images de chaque post en attente) : il doit répondre OK, sinon corriger avant de pousser.
   Commit et push de `posts/<D>/` et `posts/<D>-story/`, lancer `programme.yml`, vérifier que chaque
   `https://pickandwatch.fr/posts/<D>/0N.jpg` et `…/posts/<D>-story/0N.jpg` répond 200.
9. Envoyer les images et la légende dans la conversation (SendUserFile + texte, en précisant
   que les mêmes visuels partent aussi en story à 19h), puis la
   notification « Post P&W à valider — publication automatique à 19h sans réponse de ta part ».

**Si Alexandre répond** (chaque réponse vaut pour le carrousel ET la story) : « ok » →
`"statut": "valide"` dans les deux `post.json`, et copier `posts/<D>/editorial.json`
vers `data/editorial/<D>.json` (`"_statut": "validé le …"`), push, relancer le site.
Une correction → refaire l'image ou la légende, relancer `story_soir.py <D>`, push. « Annule » →
`"statut": "annule"` dans les deux `post.json`, push. Il peut aussi ne viser que l'un des deux
(« pas de story ce soir ») : n'appliquer qu'à celui-là.

**Matchs en journée** (Macao, Europe, matinées du week-end) : un match qui commence avant
19h le lendemain est déjà joué quand le carrousel de sa nuit est publié. Annonce-le donc dans
le carrousel de la veille (« demain à 12h10 en direct sur … »), avec son heure et sa chaîne.

## 3. 18h50 : filet de sécurité

Lancer d'abord `python3 -m pipeline.instagram verify` et corriger tout PROBLÈME signalé
(sinon Meta refuse le post à 19h), sans attendre de réponse : légende trop longue → resserrer
les briefs ★★ et ★ jusqu'à environ 2 000 caractères, sans rien ajouter ni changer sur le fond ;
décalage horaire faux → le corriger ; image absente → la régénérer. Push, puis notification
« Post P&W corrigé avant 19h » avec ce qui a été coupé. (`verifier-posts.yml` refait ce contrôle
à chaque push dans `posts/` et ouvre une issue s'il échoue.) Si le post de D est encore `propose` : copier `posts/<D>/editorial.json` vers
`data/editorial/<D>.json` avec `"_statut": "publié sans réponse (règle de 19h)"`, push,
relancer le site (le site et le post doivent dire la même chose). Si `annule` : ne rien faire.
Si `posts/<D>-story/` manque alors que le carrousel existe, lancer `story_soir.py <D>` et pousser.
**À 19h00 pile** (attendre si besoin), lancer `instagram.yml` en mode `publish-due` sans attendre le cron, qui peut passer avec 30 min de retard :
`gh api -X POST repos/Pickandwatch/pickandwatch/actions/workflows/instagram.yml/dispatches -f ref=main -f inputs[mode]=publish-due`.
Après 19h05, vérifier le statut dans `posts/<D>/post.json` et `posts/<D>-story/post.json` (après `git pull`) :
- `publie` avec un `media_id` : rien à faire.
- `propose` avec un champ `erreur` : erreur passagère, le robot réessaie au passage suivant
  (3 essais au plus) ; revérifier vers 19h40.
- `echec` : le robot a abandonné et a ouvert une issue GitHub « Post P&W non publié ».
  **Prévenir Alexandre tout de suite** (notification « Post P&W non publié », avec l'erreur).
  Si la cause se corrige (légende trop longue, image manquante) et qu'il est moins de 22h :
  corriger, remettre `"statut": "propose"`, retirer `tentatives` et `erreur`, push, puis lancer
  `instagram.yml` en mode `publish-due`
  (`gh api -X POST …/workflows/instagram.yml/dispatches -f ref=main -f inputs[mode]=publish-due`).
- Toujours `propose` sans `erreur` à 19h15 : lancer `instagram.yml` en mode `publish-due`.

Le robot n'essaie plus un post resté sans publication 3 h après l'heure prévue (statut `echec`)
et un post en échec ne bloque plus ceux des jours suivants.
