# Backend — Réservation Collège de la Retraite

## Setup

```bash
cd retraite-backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # puis éditer .env
```

Dans WampServer, démarrer uniquement le service MySQL et créer la base :

```sql
CREATE DATABASE retraite_db CHARACTER SET utf8mb4;
```

## Lancer l'API

```bash
uvicorn app.main:app --reload
```

Au démarrage, les tables sont créées automatiquement (et mises à jour sans perte de données si une nouvelle version
ajoute des colonnes : voir `app/migrations.py`) et les comptes `DEV_EMAIL`/`ADMIN_EMAIL`
(définis dans `.env`) sont créés s'ils n'existent pas encore.

Documentation interactive : http://127.0.0.1:8000/docs

## Docker (base MySQL + API en une commande)

```bash
cp .env.example .env     # puis remplir MYSQL_PASSWORD, MYSQL_ROOT_PASSWORD, SECRET_KEY, ADMIN_PASSWORD...
docker compose up -d --build
```

L'API répond sur http://localhost:8000 (documentation : `/docs`). La base MySQL est créée automatiquement ;
les données (base, reçus PDF, logs) sont conservées dans des volumes Docker, même après `docker compose down`
(seul `docker compose down -v` les efface).

HTTPS automatique avec un nom de domaine (certificat Let's Encrypt via Caddy) :

```bash
# dans .env : DOMAIN=retraite.exemple.com   et   PUBLIC_BASE_URL=https://retraite.exemple.com
docker compose --profile https up -d --build
```

Avec une base MySQL hébergée (TiDB, Aiven...), on n'utilise que le service `api` : fournir `DATABASE_URL`
(format `mysql://utilisateur:motdepasse@hote:port/base`) et lancer l'image seule (`docker build -t retraite-api .`).

## Endpoints principaux

- `POST /auth/register` — inscription client
- `POST /auth/login` — connexion, retourne un JWT
- `GET /auth/me` — profil courant
- `GET /tariffs` — grille tarifaire complète (publique), lue par l'application
- `POST /reservations/quote` — prix détaillé d'une location avant de réserver
- `POST /reservations` — créer une réservation (espace, créneau, catégorie du client, prestations, acceptation du règlement)
- `GET /reservations` — liste (client : les siennes / admin-dev : toutes)
- `GET /reservations/{id}` — détail
- `POST /reservations/{id}/validate` — validation admin (génère le reçu PDF)
- `POST /reservations/{id}/cancel` — annulation
- `GET /reservations/{id}/receipt` — téléchargement du reçu PDF

## Tests

```bash
pip install pytest httpx
python -m pytest tests
```

## Règles de réservation

- Le prix suit la grille tarifaire de l'économat (fichier `app/tariffs.py`) :
  espace × catégorie du client (personnel du Collège, personnel extérieur, partenaire public,
  partenaire privé / ONG / fédération sportive) × durée (jusqu'à 5 h : « moins de 5 heures », au-delà : « journée »).
  On y ajoute les prestations choisies (chaises, tables, sonorisation) et une caution remboursable de 500 000 FCFA,
  versée en même temps que la location. Le chiffre d'affaires du tableau de bord compte la location et les
  prestations, jamais la caution. Les appartements, chambres et la cuisine ne sont pas proposés.
- Pour changer un prix : modifier la valeur dans `app/tariffs.py` et redémarrer le serveur (l'application mobile
  lit les prix depuis l'API, rien d'autre à toucher). Les réservations déjà faites gardent leur prix.
- Location mensuelle ou annuelle : taux forfaitaire négocié avec l'administration (pas de prix automatique).
- Réservation interne du Collège (compte admin/dev) : 0 FCFA, sans caution.
- Une réservation admin/dev est automatiquement interne, validée et gratuite.
- Une réservation externe est bloquée si elle chevauche un créneau déjà pris
  (interne ou externe) ; l'API renvoie alors la prochaine date disponible.
- Un code de sécurité unique est généré à la création de chaque réservation.
- Le reçu PDF est généré dès que le statut passe à "validated".

## Déploiement en ligne (Railway + MySQL)

Le dossier contient un `Dockerfile` et un `railway.json` : l'hébergeur construit l'image tout seul.

1. Pousser la branche sur GitHub, puis sur Railway : **New Project → Deploy from GitHub repo**.
2. Dans le service du backend, régler **Root Directory** sur `retraite-backend`.
3. Ajouter à ce projet un service **MySQL** (New → Database → MySQL).
4. Variables du service backend (onglet *Variables*) :

   | Variable | Valeur |
   |---|---|
   | `DATABASE_URL` | `${{MySQL.MYSQL_URL}}` (référence au service MySQL ; le préfixe `mysql://` est converti automatiquement) |
   | `SECRET_KEY` | longue valeur aléatoire : `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
   | `ADMIN_EMAIL` / `ADMIN_PASSWORD` | compte admin créé au premier démarrage (mot de passe fort exigé) |
   | `DEV_EMAIL` / `DEV_PASSWORD` | compte développeur (facultatif) |
   | `ANTHROPIC_API_KEY` | clé de l'assistant IA (facultatif, sans elle l'assistant est désactivé) |

   `APP_ENV=production` est déjà fixé dans le `Dockerfile` : sans `SECRET_KEY`, le serveur refuse de démarrer.
5. **Settings → Networking → Generate Domain** : l'API est alors disponible en HTTPS, par exemple
   `https://xxx.up.railway.app/health` doit répondre `{"status":"ok"}`.
6. Dans l'application mobile, saisir cette adresse dans les réglages du serveur (ou compiler l'APK avec
   `--dart-define=API_BASE_URL=https://xxx.up.railway.app`).

Points à connaître :

- Les tables sont créées au démarrage ; si MySQL n'est pas encore prêt, le serveur réessaie pendant environ 30 secondes.
- Le disque du conteneur est temporaire : les reçus PDF sont régénérés à la demande s'ils ont disparu, et les logs
  sont aussi écrits dans la console de l'hébergeur.
- Un seul processus uvicorn tourne dans le conteneur (nécessaire pour la création des tables au démarrage).
- Essai local de l'image : `docker build -t retraite-api . && docker run --rm -p 8000:8000 -e SECRET_KEY=test -e DATABASE_URL=... retraite-api`.
