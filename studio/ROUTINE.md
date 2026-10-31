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
- **Publication Instagram automatique à 18h** si Alexandre n'a pas répondu, sauf s'il a
  demandé l'annulation (`"statut": "annule"` dans `posts/AAAA-MM-JJ/post.json`).
  **Heure du soir : 18h à partir du programme de la nuit du lundi 2 novembre 2026** (décision
  d'Alexandre du 31/10, test de deux semaines). Jusqu'au dimanche 1er novembre inclus : 19h.
  Même fonctionnement qu'avant : sans validation à 18h, le carrousel et la story partent seuls.
- Jamais de mot de passe ni de clé dans la conversation. La clé Instagram est un secret GitHub.
- Ton : direct, sobre, tutoiement du lecteur, pas de superlatifs. Charte « papier ».

- **Diffuseurs et commentateurs (Alexandre, 25/10/2026)** : chaque fois qu'une légende cite beIN SPORTS,
  taguer @beinsports_fr et ses commentateurs (`data/comptes-instagram.json` : Rémi Reverchon, Fred Weis,
  Xavier Vaution, Chris Singleton ; Jacques Monclar cité sans tag) ; chaque fois qu'elle cite Prime Video,
  taguer @primevideosportfr. Jamais de pseudo deviné.
- **Le site d'abord nommé (Alexandre, 31/10/2026)** : partir du principe que les abonnés connaissent
  le compte Instagram, pas le site. Tout contenu qui parle d'une fonction du site dit explicitement
  que Pick & Watch, c'est aussi un site, et fait apparaître **pickandwatch.fr** en grand (couverture
  et slide de fin), pas seulement en petit : jamais « onglet Mon équipe » seul, toujours « sur notre
  site pickandwatch.fr, onglet Mon équipe ». Légende : le nom du site dès la première ligne, avec
  « (lien en bio) ». Pour présenter une fonction du site : `studio/site_tuto.py` (mode d'emploi
  en étapes, avec de vraies captures d'écran du site dans un téléphone ; modèle :
  `posts/2026-10-31-mon-equipe/`).
- **Hashtags et mots-clés (31/10/2026)** : 3 à 5 hashtags ciblés au maximum (Instagram n'en accepte
  plus que 5 ; au-delà, le robot coupe après le 5e) : `#NBA #NBAFrance #BasketFrance`, plus un ou deux
  du sujet (`#NBACup`, `#Wembanyama`…). Les hashtags n'apportent presque pas de portée : ce qui compte,
  ce sont les mots-clés en clair dans la première ligne de la légende et sur la couverture (« NBA »,
  « heure de Paris », « où regarder », noms d'équipes et de joueurs), que la recherche Instagram lit.

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
   `{"publier_a": "<D>T18:00:00+01:00", "statut": "propose", "images": [...], "legende": "..."}`
   (heure d'hiver : `+01:00` ; 18h à partir du 2 novembre 2026, 19h avant). Garder l'éditorial du site dans
   `posts/<D>/editorial.json` (même format que `data/editorial/`).
7. **Story du soir** (demandée par Alexandre le 21 octobre 2026 ; règle confirmée le 25 octobre : toute annonce de match part **systématiquement en post ET en story**, y compris une annonce exceptionnelle hors carrousel du soir, par exemple un match en journée) : lancer
   `python3 studio/story_soir.py <D>`. Il reprend les images du carrousel, chacune centrée sur un
   fond 1080x1920 de sa couleur, dans `posts/<D>-story/` (`post.json` : `"type": "story"`,
   `"suit": "<D>"`, même heure, même statut). Mêmes règles que le carrousel : publication
   automatique à 18h sans réponse ; le robot annule la story si le carrousel est `annule`.
   Relancer le script après toute correction d'image du carrousel. Pas de sticker lien (API).
8. Lancer `python3 -m pipeline.instagram verify` (contrôle hors ligne de la légende et des
   images de chaque post en attente) : il doit répondre OK, sinon corriger avant de pousser.
   Commit et push de `posts/<D>/` et `posts/<D>-story/`, lancer `programme.yml`, vérifier que chaque
   `https://pickandwatch.fr/posts/<D>/0N.jpg` et `…/posts/<D>-story/0N.jpg` répond 200.
9. Envoyer les images et la légende dans la conversation (SendUserFile + texte, en précisant
   que les mêmes visuels partent aussi en story à 18h), puis la
   notification « Post P&W à valider — publication automatique à 18h sans réponse de ta part ».

**Si Alexandre répond** (chaque réponse vaut pour le carrousel ET la story) : « ok » →
`"statut": "valide"` dans les deux `post.json`, et copier `posts/<D>/editorial.json`
vers `data/editorial/<D>.json` (`"_statut": "validé le …"`), push, relancer le site.
Une correction → refaire l'image ou la légende, relancer `story_soir.py <D>`, push. « Annule » →
`"statut": "annule"` dans les deux `post.json`, push. Il peut aussi ne viser que l'un des deux
(« pas de story ce soir ») : n'appliquer qu'à celui-là.

**Matchs en journée** (Macao, Europe, matinées du week-end) : un match qui commence avant
18h le lendemain est déjà joué quand le carrousel de sa nuit est publié. Annonce-le donc dans
le carrousel de la veille (« demain à 12h10 en direct sur … »), avec son heure et sa chaîne.

## 3. 17h50 : filet de sécurité (18h50 jusqu'au 1er novembre 2026)

Lancer d'abord `python3 -m pipeline.instagram verify` et corriger tout PROBLÈME signalé
(sinon Meta refuse le post à 18h), sans attendre de réponse : légende trop longue → resserrer
les briefs ★★ et ★ jusqu'à environ 2 000 caractères, sans rien ajouter ni changer sur le fond ;
décalage horaire faux → le corriger ; image absente → la régénérer. Push, puis notification
« Post P&W corrigé avant 18h » avec ce qui a été coupé. (`verifier-posts.yml` refait ce contrôle
à chaque push dans `posts/` et ouvre une issue s'il échoue.) Si le post de D est encore `propose` : copier `posts/<D>/editorial.json` vers
`data/editorial/<D>.json` avec `"_statut": "publié sans réponse (règle de 18h)"`, push,
relancer le site (le site et le post doivent dire la même chose). Si `annule` : ne rien faire.
Si `posts/<D>-story/` manque alors que le carrousel existe, lancer `story_soir.py <D>` et pousser.
**À l'heure pile de `publier_a`** (18h00 ; attendre si besoin), lancer `instagram.yml` en mode `publish-due` sans attendre le cron, qui peut passer avec 30 min de retard :
`gh api -X POST repos/Pickandwatch/pickandwatch/actions/workflows/instagram.yml/dispatches -f ref=main -f inputs[mode]=publish-due`.
Cinq minutes après, vérifier le statut dans `posts/<D>/post.json` et `posts/<D>-story/post.json` (après `git pull`) :
- `publie` avec un `media_id` : rien à faire.
- `propose` avec un champ `erreur` : erreur passagère, le robot réessaie au passage suivant
  (3 essais au plus) ; revérifier 40 minutes après l'heure prévue.
- `echec` : le robot a abandonné et a ouvert une issue GitHub « Post P&W non publié ».
  **Prévenir Alexandre tout de suite** (notification « Post P&W non publié », avec l'erreur).
  Si la cause se corrige (légende trop longue, image manquante) et qu'il est moins de 22h :
  corriger, remettre `"statut": "propose"`, retirer `tentatives` et `erreur`, push, puis lancer
  `instagram.yml` en mode `publish-due`
  (`gh api -X POST …/workflows/instagram.yml/dispatches -f ref=main -f inputs[mode]=publish-due`).
- Toujours `propose` sans `erreur` un quart d'heure après l'heure prévue : lancer `instagram.yml` en mode `publish-due`.

Le robot n'essaie plus un post resté sans publication 3 h après l'heure prévue (statut `echec`)
et un post en échec ne bloque plus ceux des jours suivants.

## 4. Le lundi : Reel « les matchs à ne pas rater cette semaine »

Validé par Alexandre le 25 octobre 2026 (premier Reel le lundi 26). Chaque lundi, dans la tâche
du matin :
1. `python3 studio/semaine.py <lundi>` classe les matchs des sept nuits (grille d'étoiles, sans le
   bonus événement) avec leur diffusion. Retenir **3 affiches**, une par nuit au plus : les mieux
   notées, en préférant à note égale un match visible à la télé française (beIN, Prime Video).
2. Écrire `posts/<lundi>-reel/spec.json` sur le modèle de `posts/2026-10-26-reel/spec.json`
   (quand, équipes, chaîne, différé ou mention, une phrase d'enjeu sourcée, étoiles), puis
   `python3 studio/reel_semaine.py posts/<lundi>-reel/spec.json` → `reel.mp4` + `cover.jpg`.
   Regarder des images extraites de la vidéo avant de proposer.
3. `post.json` : `{"type": "reel", "publier_a": "<lundi>T12:30:00+01:00", "statut": "propose",
   "images": ["cover.jpg"], "video": "reel.mp4", "legende": ...}` (légende sur le modèle du 26/10),
   `python3 -m pipeline.instagram verify`, push, lancer `programme.yml`, vérifier que la vidéo répond 200.
4. Envoyer la vidéo et la légende à Alexandre avec la notification « Post P&W à valider ». Sans
   réponse, publication automatique à 12h30 (Reel muet ; Alexandre a choisi l'automatique).
5. **Reels tirés d'un carrousel** (`studio/reel_carrousel.py`) : toujours `"grille": false` dans
   leur `post.json` (31/10/2026) : ils restent dans l'onglet Reels sans doubler le carrousel dans la
   grille du profil. Le Reel du lundi, contenu original, garde la grille (champ absent).
   Heure : **20h** (pas avant le programme du soir de 18h ; décision du 31/10/2026).

## 5. Le jeudi : Hors parquet du vendredi

Rubrique phare (Alexandre, 23 et 25 octobre 2026) : chaque vendredi à **12h**, le meilleur de l'actu
basket **hors des matchs** de la semaine : livres, films et documentaires, séries, podcasts,
événements en France (expositions, tournées, billetteries), interviews, initiatives de médias et de
créateurs français. Jamais de score ni de résultat, jamais de rumeur de transfert non confirmée.
1. **Sujets d'Alexandre d'abord** : lire `studio/hors-parquet-sujets.md` ; ses sujets passent en
   priorité (faits revérifiés), puis marquer « publié le <date> » après publication.
   **Veille** sur la semaine (lundi → jeudi) : Basket Session, First Team, TrashTalk, NBA Extra
   (beIN SPORTS), Basket USA, BeBasket, Insidebasket, L'Équipe (uniquement par les liens qu'envoie
   Alexandre), Netflix / Prime Video / Canal+ (documentaires), éditeurs (Solar, Marabout, Talent
   Sport…), billetteries et salles (Accor Arena, LDLC Arena), comptes des joueurs français. Ouvrir et
   lire chaque page citée ; recouper tout chiffre ou toute date.
2. **Sélection** : 3 sujets (un « dossier de la semaine » + deux « à lire / à voir / à suivre »),
   au moins un sujet hors Basket Session, et un sujet d'un autre format que l'écrit si possible.
   Une semaine creuse : 2 sujets, jamais de remplissage.
3. **Fabrication** : `posts/<vendredi>-hors-parquet/spec.json` sur le modèle de
   `studio/hors_parquet.py` (chaque sujet : `rubrique`, `titre`, `chiffres`, `texte`, `source`,
   plus `lien` et `lien_titre` pour la page du site), puis
   `python3 studio/hors_parquet.py posts/<vendredi>-hors-parquet/spec.json`. Regarder chaque image.
4. **Légende** : un paragraphe par sujet, sources citées, tags uniquement depuis
   `data/comptes-instagram.json` (jamais un pseudo deviné : demander à Alexandre et l'ajouter au
   fichier une fois donné).
5. `post.json` : `{"publier_a": "<vendredi>T12:00:00+01:00", "statut": "brouillon", ...}` —
   **brouillon : le robot ne le publie jamais sans validation.** Push, `programme.yml`, images en ligne
   vérifiées, puis notification « Post P&W à valider — Hors parquet, vendredi 12h ».
6. **Validation** : « ok » → `"statut": "valide"` (publication à 12h). Corrections → refaire, push.
   Sans réponse le vendredi à 11h45 : rien ne part ; prévenir Alexandre que le numéro attend.
7. Après publication, la page `pickandwatch.fr/hors-parquet.html` se met à jour toute seule
   (numéros publiés, avec les liens des sources).

## 6. Le dernier jour du mois : le programme du mois suivant

Décision d'Alexandre (25 octobre 2026) : « Mon équipe » ne montre que le
mois publié (`data/mois-publie.json`), pas toute la saison.
1. Le dernier jour du mois, mettre `mois` sur le mois de demain (ex. le 30 novembre → `"2026-12"` ; s'il y est déjà, ne rien changer), push, lancer
   `programme.yml` et vérifier une page équipe (ex. `pickandwatch.fr/equipes/sa.html` : « Le programme
   jusqu'à fin décembre »).
2. Annonce Instagram, **post + story** à **12h30** : carrousel avec `studio/guide.py` (couverture
   « Le programme de <mois> est en ligne », une slide « les affiches du mois » : 4 ou 5 matchs les
   mieux notés selon la grille, avec chaîne si connue, une slide « + Agenda : ajoute les matchs
   qui te tentent, un par un (Google, Outlook, Apple) », slide de fin). Pas d'abonnement à l'agenda d'une
   équipe : supprimé le 25/10/2026 pour garder l'intérêt du compte Instagram). Si le mois contient des matchs de NBA Cup,
   les signaler. Story : `python3 studio/story_soir.py <dossier>`.
3. `post.json` en `"statut": "brouillon"` (jamais publié sans validation), notification « Post P&W
   à valider — programme de <mois> ». « ok » → `valide` (carrousel ET story). Dossier :
   `posts/<jour>-programme-mois/`. S'il existe déjà (annonce déjà préparée), ne rien refaire.

## 7. NBA Cup (30 octobre → 11 décembre 2026)

Validé par Alexandre le 25 octobre 2026 : charte NBA Cup (version nuit et or, `studio/cup_theme.py`)
et **« NBA CUP » bien visible en haut** des visuels des soirs et des verdicts de Cup.
Soirs de Cup : vendredis 30 oct., 6, 13, 20, 27 nov. ; mardi 24 et mercredi 25 nov. ; quarts 4-5 déc. ;
demies 8-9 déc. ; finale 11 déc. (Hinkle Fieldhouse, Indianapolis). Les matchs de Cup portent
`"cup": "NBA Cup"` dans `data/nuits/<D>.json` (calendrier ESPN).
- **Carrousel du soir (§ 2)** : si la nuit compte des matchs de Cup, `spec.json` avec
  `"theme": "cup"` et, dans `cover`, `"bandeau": "NBA CUP 2026 · <PHASE DE GROUPES / QUARTS…>"` et
  `"title": "CE SOIR, NBA CUP"` ; les matchs de Cup en tête (le ★★★ de préférence parmi eux) ; sur
  leurs slides, `label` commence par « NBA CUP · ». La story suit (`story_soir.py`), comme d'habitude.
  Légende : commencer par la NBA Cup, `#NBACup`, tags depuis `data/comptes-instagram.json`
  (@primevideosportfr pour les matchs Prime).
- **Verdicts du lendemain (§ 1)** : `story.py` détecte la Cup tout seul (bandeau, Cup en tête,
  récapitulatif en charte Cup). **En plus**, les matins de Cup : `python3 studio/story.py <D-1> --post`
  → carrousel du fil `posts/<D-1>-verdicts-post/` (même règle de publication que la story : 8h,
  sans validation préalable), légende générée, vérifiée par `pipeline.instagram verify`.
- **Jamais de classement** sur Instagram : il reste caché sur `pickandwatch.fr/nba-cup.html`.

## 8. Nuit d'Halloween (31 octobre)

Demande d'Alexandre (25/10/2026), version 2 (la première, en clip-art, a été refusée : « trop
cheap »). « Édition Halloween », sobre et éditoriale, automatique pour `posts/AAAA-10-31/` et pour les
verdicts de cette nuit (`story.py`) : couvertures en version nuit de la charte (fond encre, l'orange
de la marque comme seule couleur), toile d'araignée et croissant de lune au trait fin, mention
« ÉDITION HALLOWEEN · 31.10 » ; slides de match et cartes : seulement la toile au trait, discrète.
Légende du soir : commencer par « Édition Halloween » et ajouter #Halloween. Aucun changement de
contenu ni de règle anti-spoiler.
