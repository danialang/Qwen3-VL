# Questions de soutenance – fiche de révision

Application de réservation des salles du Collège Catholique Bilingue de la Retraite.
À relire le matin : chaque question a une réponse courte (à dire en premier) puis les détails si le jury creuse.

---

## 1. Quelle est l'architecture de l'application ?

**Réponse courte :** une architecture client-serveur en trois couches : une application mobile Flutter, une API REST en Python (FastAPI) et une base MySQL.

**Détails :**
- **Client** : appli Android en Flutter (`retraite_mobile`), utilisée par les clients et par l'administration.
- **Serveur** : API FastAPI (`retraite-backend`). Elle gère l'inscription, la connexion, les réservations, la validation, les reçus PDF avec QR code, les emails et l'assistant IA.
- **Données** : MySQL.
- Le mobile ne touche jamais la base. Il envoie des requêtes HTTP, l'API vérifie le jeton JWT et les droits, applique les règles, puis lit ou écrit dans la base.
- Découpage du code : routes (`auth_router`, `reservations_router`, `admin_router`, `verify_router`), modèles (`models.py`), validation (`schemas.py`), sécurité (`security.py`), dossier `assistant/` pour l'IA.
- Déploiement : Docker (API + MySQL) et Caddy pour le HTTPS.

**À retenir :** Flutter → FastAPI → MySQL.

---

## 2. C'est quoi la base de données ?

**Réponse courte :** MySQL, à laquelle j'accède avec SQLAlchemy (ORM) et le pilote PyMySQL.

**Détails :**
- En local : MySQL via WampServer. En production : MySQL dans Docker.
- SQLAlchemy permet de manipuler des classes Python au lieu d'écrire du SQL à la main.
- Les tables sont créées automatiquement au démarrage du serveur.

| Table | Rôle |
|---|---|
| `users` | comptes (client, admin, développeur) |
| `reservations` | salle, date, heures, statut de la réservation |
| `security_codes` | code de sécurité de chaque réservation |
| `receipts` | reçus PDF générés à la validation |
| `password_resets` | codes « mot de passe oublié » envoyés par email |

**À retenir :** MySQL, 5 tables, SQLAlchemy.

---

## 3. Pourquoi avoir utilisé FastAPI ?

**Réponse courte :** parce que c'est du Python, qu'il est rapide, qu'il valide les données tout seul et qu'il génère la documentation de l'API automatiquement.

**Détails :**
- Un seul langage pour tout le backend, IA comprise.
- Rapide à l'exécution et rapide à coder.
- Validation automatique avec Pydantic : un email mal formé ou une date invalide sont refusés avant d'arriver dans mon code.
- Documentation générée sur `/docs` : j'ai pu tester chaque route avant même que l'appli mobile soit prête.
- L'authentification JWT et les rôles (client/admin) s'intègrent facilement.
- Plus léger que Django : je n'avais pas besoin de pages web, seulement d'une API pour le mobile.

**À retenir :** Python, rapidité, validation, doc automatique.

---

## 4. Quel est l'objectif général de l'application ?

**Réponse courte :** informatiser la réservation du gymnase et de la salle des fêtes du Collège, qui se faisait jusque-là à la main.

**Détails :**
- Le client réserve un créneau depuis son téléphone et accepte le règlement intérieur.
- L'administration valide la réservation, et un reçu PDF avec QR code est généré.
- Le QR code permet de vérifier que le reçu est authentique.
- Résultat : plus de doubles réservations, plus de papiers perdus, plus de faux reçus, et des statistiques pour l'administration.

**À retenir :** réserver, valider, prouver (reçu + QR code), suivre (statistiques).

---

## 5. L'assistant IA, c'est quoi son intervention ?

**Réponse courte :** il y a deux assistants. Celui du client l'aide à réserver en langage naturel. Celui de l'admin répond à des questions sur les réservations et produit le bilan annuel.

**Assistant client** (`/assistant/client`), par exemple : « Je veux le gymnase samedi de 14h à 18h ». Il peut :
- vérifier si le créneau est libre, et proposer une autre date sinon (`check_availability`) ;
- créer la réservation, uniquement après confirmation que le client accepte le règlement (`create_reservation`) ;
- afficher les réservations du client (`list_my_reservations`).

**Assistant admin** (`/assistant/admin`), réservé au rôle admin. Il peut :
- compter les réservations du mois (`count_reservations_this_month`) ;
- lister celles qui sont en attente (`list_pending_reservations`) ;
- générer le bilan de fin d'année : taux d'occupation, revenus, nombre par type (`get_annual_report`) ;
- lire les logs pour aider à trouver un bug (`read_app_logs`).

**Point fort à dire :** l'IA n'invente pas les chiffres et n'accède pas librement à la base. Elle peut seulement appeler les fonctions que j'ai codées, et ces fonctions passent par les mêmes règles de sécurité que le reste de l'application.

---

## 6. Comment l'assistant IA a-t-il été créé et mis sur pied ?

**Réponse courte :** je n'ai pas entraîné de modèle. J'utilise le modèle Claude d'Anthropic via son API, et je lui ai donné un rôle (prompt système) et des outils, c'est-à-dire des fonctions Python reliées à ma base.

**Étapes :**
1. **Modèle** : API Claude, appelée avec la bibliothèque Python officielle `anthropic`.
2. **Clé API** : stockée dans le fichier `.env` du serveur, jamais dans l'appli mobile, pour qu'on ne puisse pas la voler en décompilant l'APK.
3. **Prompt système** : il donne son rôle à l'assistant et ses règles, par exemple : vérifier la disponibilité avant de réserver, répondre en français.
4. **Outils (tool use)** : chaque fonction est décrite avec ses paramètres, et c'est le modèle qui choisit laquelle appeler.
5. **Boucle de traitement** (`run_tool_loop` dans `assistant/common.py`) :
   - le message de l'utilisateur part vers Claude ;
   - si Claude demande un outil, mon code l'exécute sur MySQL et lui renvoie le résultat ;
   - on recommence jusqu'à la réponse finale, avec 6 tours au maximum pour éviter une boucle infinie.
6. **Erreurs gérées** : si la clé est invalide, si le service est surchargé ou si la connexion échoue, l'utilisateur reçoit un message clair au lieu d'un plantage.
7. **Sécurité** : deux routes séparées, et la route admin vérifie le rôle.

**À retenir :** API Claude + prompt système + outils + boucle.

---

## Mémo express (30 secondes avant d'entrer)

- Architecture : **Flutter → FastAPI → MySQL**
- Base : **MySQL, 5 tables, SQLAlchemy**
- FastAPI : **Python, rapide, validation Pydantic, doc `/docs`**
- Objectif : **informatiser la réservation du gymnase et de la salle des fêtes**
- IA : **2 assistants (client / admin), qui n'agissent que via mes fonctions**
- Création de l'IA : **API Claude + prompt système + outils + boucle de 6 tours max**
