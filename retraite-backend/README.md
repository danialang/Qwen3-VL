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

Au démarrage, les tables sont créées automatiquement et les comptes `DEV_EMAIL`/`ADMIN_EMAIL`
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
- `POST /reservations` — créer une réservation (créneau, salle, acceptation du règlement)
- `GET /reservations` — liste (client : les siennes / admin-dev : toutes)
- `GET /reservations/{id}` — détail
- `POST /reservations/{id}/validate` — validation admin (génère le reçu PDF)
- `POST /reservations/{id}/cancel` — annulation
- `GET /reservations/{id}/receipt` — téléchargement du reçu PDF

## Règles de réservation

- Montant fixe : 5 000 000 FCFA (0 pour une réservation interne du Collège).
- Une réservation admin/dev est automatiquement interne, validée et gratuite.
- Une réservation externe est bloquée si elle chevauche un créneau déjà pris
  (interne ou externe) ; l'API renvoie alors la prochaine date disponible.
- Un code de sécurité unique est généré à la création de chaque réservation.
- Le reçu PDF est généré dès que le statut passe à "validated".
