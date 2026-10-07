# Pick & Watch

Le programme NBA pour les fans en France : quoi regarder, où, quand. Zéro spoiler. Jamais.

Site : [pickandwatch.fr](https://pickandwatch.fr) (bientôt) · Instagram : [@pickandwatch](https://www.instagram.com/pickandwatch/)

## Comment ça marche

Deux fois par jour, un robot (GitHub Actions, onglet **Actions**) :

1. récupère le **calendrier officiel** des matchs de la nuit (horaire, salle, ville, terrain neutre) ;
2. récupère le **guide TV français** des chaînes beIN SPORTS (direct et différés) ;
3. **recoupe** les deux, convertit tout en heure de Paris et liste ce qui reste à confirmer ;
4. **génère le site** dans la charte « papier » et l'enregistre ici.

Le résumé de chaque passage (matchs + points à vérifier) s'affiche dans l'onglet **Actions**,
en cliquant sur le dernier passage du robot « Programme de la nuit ».

**Règle absolue : aucun score n'est jamais lu ni affiché.**

## Où sont les choses

| Dossier | Contenu |
|---|---|
| `pipeline/` | Le robot (Python, sans dépendance externe) |
| `data/nuits/` | Le programme vérifié de chaque nuit (un fichier par nuit) |
| `data/editorial/` | Nos choix éditoriaux par nuit : étoiles, briefing, commentateurs |
| `data/diffuseurs.json` | Diffusions annoncées hors guide TV (ex. Prime Video) |
| `site/` | Le site généré (ne pas modifier à la main : il est régénéré à chaque passage) |
| `assets/` | Logo, favicon, feuille de style |

### Ajouter les étoiles et le briefing d'une nuit

Créer `data/editorial/AAAA-MM-JJ.json` (la date est celle du soir) :

```json
{
  "matchs": {
    "401914123": { "stars": 2, "brief": "Une phrase d'enjeu, sourcée.", "commentators": "Prénom Nom et Prénom Nom" }
  }
}
```

L'identifiant du match figure dans `data/nuits/AAAA-MM-JJ.json`. Les commentateurs ne sont
renseignés que s'ils ont été annoncés par le diffuseur.

## Lancer le robot à la main

Onglet **Actions** → « Programme de la nuit » → **Run workflow** (on peut préciser une date).

En local : `python -m pipeline.run --night 2026-10-07`

## Sources

- Calendrier : API publique du scoreboard NBA d'ESPN (non officielle).
- Diffusion en France : guide TV XMLTV France ([xmltvfr.fr](https://xmltvfr.fr)), chaînes beIN SPORTS.
