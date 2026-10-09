# Questions de soutenance – fiche de révision

Application de réservation des salles du Collège Catholique Bilingue de la Retraite.
À relire le matin : chaque question a une réponse courte (à dire en premier) puis les détails si le jury creuse.

---

# PARTIE 1 – Questions de cette discussion

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

---

# PARTIE 2 – Questions posées dans les autres discussions

Ces questions reprennent celles que tu as posées dans tes discussions précédentes sur le projet, ainsi que le questionnaire jury de 59 questions préparé le 07/10. Les doublons avec la partie 1 ont été retirés.

## A. Présentation générale

**7. Le projet est fait en quoi ? C'est quoi le backend et le frontend ?**
- Backend : Python + FastAPI (`retraite-backend`). Il gère l'authentification, les conflits de créneaux, MySQL, le reçu PDF avec QR code et l'appel à Claude.
- Frontend : Flutter/Dart (`retraite_mobile`). Il contient les écrans, vérifie le format des saisies et appelle l'API.
- À dire au jury : « une application mobile Flutter reliée à un serveur Python FastAPI, avec les données dans MySQL ; les deux communiquent par une API REST ».

**8. Résumer le projet en un paragraphe.**
- Réservation du gymnase et de la salle des fêtes ; thème vert et doré, police Poppins, mode clair ou sombre.
- Connexion sécurisée (JWT + bcrypt) avec trois rôles : client, admin, dev.
- Parcours : vérification du créneau (une autre date est proposée s'il est pris), paiement simulé, validation par l'admin, reçu PDF avec code de sécurité et QR code.
- Tableau de bord (revenus, taux d'occupation), assistant IA, mot de passe oublié par code envoyé par email. L'APK est construit par GitHub Actions.

**9. C'est quoi un MVP ?**
Minimum Viable Product : on livre d'abord le cœur fonctionnel, vite et sans fioritures, puis on l'améliore.

**10. Pourquoi Flutter ?**
Un seul code en Dart pour Android (et le web), avec une interface identique sur tous les appareils.

**11. Pourquoi une appli mobile et pas un site web ?**
Presque tous les clients ont un téléphone. Et Flutter peut aussi produire une version web si besoin.

**12. Avez-vous utilisé Django ?**
**Non**, c'est FastAPI. Si on parle de MVT, j'explique la correspondance avec mon code (question 15), sans prétendre avoir utilisé Django.

**13. C'est quoi une API REST ? Quelles sont les routes principales ?**
- Chaque ressource a une URL : GET pour lire, POST pour créer, réponses en JSON.
- Authentification : `/auth/register`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/change-password`, `/auth/me`.
- Réservations : `/reservations`, plus `/availability`, `/{id}/pay`, `/{id}/validate`, `/{id}/cancel`, `/{id}/receipt`.
- Autres : `/admin/stats`, `/verify/{id}/{jeton}` et `/assistant/client` ou `/assistant/admin`.

## B. Architecture : MVT et MVC

**14. Quelle est l'architecture réelle ?**
Une architecture client-serveur en trois couches, avec une API REST : présentation (Flutter), métier (FastAPI), données (SQLAlchemy + MySQL). Les échanges se font en JSON sur HTTP, avec un JWT.

**15. MVT : que représentent M, V et T dans mon code ?**
- MVT est le modèle de Django, pas celui de mon projet ; je donne la correspondance.
- **M** : `models.py` (5 classes SQLAlchemy) et `schemas.py` (Pydantic).
- **V** : les routeurs FastAPI et `reservation_logic.py`. Chez Django, la « vue » est la logique, pas l'écran.
- **T** : les écrans Flutter (`lib/screens`, `lib/widgets`) et la page HTML de vérification des reçus.
- Exemple : M = classe `Reservation`, V = `create_reservation` (vérifie le conflit puis enregistre), T = écran `screens/booking`.

**16. Et en MVC ?**
M = `models.py`, V = écrans Flutter, C = routeurs FastAPI. La « Vue » de Django joue le rôle du Contrôleur en MVC.

## C. UML et méthode

**17. Pourquoi UML ?**
C'est une norme internationale, indépendante du langage et orientée objet.

**18. Pourquoi 2TUP et pas Merise ou une méthode agile ?**
2TUP mène en parallèle une branche fonctionnelle (les besoins) et une branche technique, qui se rejoignent à la conception. Merise sert surtout à modéliser les données. L'agile convient mieux à une équipe qui livre par petites versions.

**19. Expliquer le diagramme de cas d'utilisation.**
- Acteurs principaux : Utilisateur, Client, Administrateur.
- Acteurs secondaires : le service Mobile Money et le service d'IA.

**20. Que veut dire « include » vers S'authentifier ?**
Que l'action est obligatoire : il faut être connecté. Dans le code, c'est le JWT ; sans jeton valide, l'API répond 401.

**21. Acteur principal ou secondaire ?**
Le principal déclenche l'action. Le secondaire est sollicité par le système (paiement, IA).

**22. La flèche à triangle vide entre Client et Utilisateur ?**
Une généralisation, c'est-à-dire un héritage : le Client est un Utilisateur.

**23. Expliquer le diagramme de séquence « réserver et payer ».**
POST `/reservations` → recherche d'un chevauchement → statut « en attente » + code de sécurité → réponse 201. Ensuite POST `/{id}/pay`, puis validation par l'admin.

**24. Le cadre « alt » ?**
Un si/sinon : si le créneau est libre, la réservation est créée ; s'il est occupé, elle est refusée et la prochaine date libre est proposée.

**25. Diagramme de séquence ou de communication ?**
La séquence montre l'ordre des messages dans le temps. La communication montre les liens entre les objets, avec des messages numérotés.

**26. Diagramme d'activité ; différence avec un diagramme d'états ?**
- Activité : trois couloirs (Client, Système, Admin) ; les losanges sont des décisions.
- États : on suit un seul objet, la réservation, qui passe de « en attente » à « validée » ou « annulée ».

**27. Expliquer le diagramme de déploiement.**
Téléphone Android (Flutter) → HTTPS → FastAPI dans Docker → MySQL. Services externes : API Claude et serveur SMTP pour les emails. GitHub Actions construit l'APK. Mobile Money est indiqué comme « prévu ».

**28. Rôle de GitHub Actions ?**
Compiler automatiquement l'APK à chaque push.

**29. Le diagramme de classes ?**
Il est dans le rapport : 5 classes (User, Reservation, SecurityCode, Receipt, PasswordReset).

## D. Base de données (en plus de la question 2)

**30. Pourquoi MySQL ?**
Une base relationnelle, gratuite et stable, adaptée à des données liées entre elles (un client a plusieurs réservations). En développement, je l'ai utilisée avec WampServer.

**31. Comment les tables sont-elles créées ?**
`Base.metadata.create_all` au démarrage du serveur, puis création des comptes de départ. L'adresse de la base est dans `DATABASE_URL`, dans le `.env`.

**32. Relations entre les tables ?**
User 1–N Reservation ; Reservation 1–1 SecurityCode ; Reservation 1–(0..1) Receipt.

**33. Clé primaire / clé étrangère ?**
`id` identifie chaque ligne. `reservations.user_id` pointe vers `users.id`.

**34. Pourquoi une colonne `password_hash` ?**
bcrypt produit une empreinte irréversible : le mot de passe n'est jamais stocké en clair.

**35. Comment empêcher une double réservation ?**
- La fonction `find_conflict` cherche une réservation de la même salle, à la même date et non annulée, avec début existant < fin demandée ET fin existante > début demandé.
- En cas de conflit, une date libre dans les 30 jours est proposée.

**36. C'est quoi `is_internal` ?**
Une réservation du Collège (admin ou dev) : gratuite et validée tout de suite, mais elle bloque le créneau comme les autres.

**37. Quels sont les états d'une réservation ?**
pending (en attente), validated (validée), cancelled (annulée). Une réservation annulée libère le créneau.

**38. Le montant ?**
`RESERVATION_AMOUNT` = 5 000 000 FCFA, défini dans le `.env` et copié dans la colonne `amount` à la création.

**39. La table security_codes ?**
Un code de 8 caractères (`secrets.token_hex`), imprimé sur le reçu et utilisé dans la signature du QR code.

**40. Comment le QR code empêche-t-il la fraude ?**
Il contient le lien `/verify/{id}/{jeton}`. Le jeton est calculé en HMAC-SHA256 à partir de l'id, du code de sécurité et de la clé secrète du serveur. Sans cette clé, impossible de fabriquer un faux reçu valide.

**41. Mot de passe oublié côté base ?**
On stocke l'empreinte du code, sa date d'expiration, un compteur d'essais et un marqueur « déjà utilisé ».

**42. Sécuriser et sauvegarder la base ?**
- Les secrets sont dans le `.env`, jamais sur GitHub. SQLAlchemy protège contre l'injection SQL. Chaque requête a sa propre session (`get_db`).
- Sauvegarde : `mysqldump`, les volumes Docker, puis les sauvegardes automatiques de l'hébergeur.

**43. Pourquoi `email` en VARCHAR(191) ?**
En utf8mb4, MySQL limite la taille d'un index. Avec 255 caractères, j'avais l'erreur « clé trop longue » ; avec 191, ça passe.

## E. Sécurité, connexion et rôles

**44. Comment fonctionne la connexion ?**
Le mot de passe est vérifié avec bcrypt, puis le serveur renvoie un JWT signé, valable 120 minutes. L'appli l'envoie à chaque requête et `get_current_user` le vérifie.

**45. Comment sont gérés les rôles ?**
Les routes sensibles utilisent `require_roles(admin, dev)` ; sinon le serveur répond 403 (accès interdit).

**46. Pourquoi un nouvel inscrit est-il toujours client ?**
C'est voulu : sinon n'importe qui pourrait se déclarer admin. Le rôle admin est attribué à la main.

**47. Le rôle dev ?**
Le développeur a les mêmes droits que l'admin, et ses réservations sont internes, donc gratuites.

**48. Validations à l'inscription ; pourquoi les refaire côté serveur ?**
- Nom sans chiffres, email d'un fournisseur reconnu, mot de passe fort, confirmation du mot de passe.
- Elles sont vérifiées dans `validators.dart` puis revérifiées dans `validators.py`, car on peut appeler l'API sans passer par l'appli.

**49. L'application est-elle sécurisée ?**
- En place : bcrypt, JWT à durée limitée, rôles, reçus signés en HMAC, secrets dans le `.env`, validations côté serveur.
- Pour la production : HTTPS partout (prévu avec Caddy) et sauvegardes automatiques.

**50. La clé secrète de test pose-t-elle problème ?**
Elle suffit pour les tests. En production, il faut une clé longue et aléatoire ; le serveur refuse d'ailleurs de démarrer en mode production sans `SECRET_KEY`.

## F. IA (en plus des questions 5 et 6)

**51. Que se passe-t-il si l'IA ne marche pas ?**
L'application fonctionne sans elle : l'assistant est un confort. Ses outils appellent la même `reservation_logic.py` que l'API, donc les mêmes règles s'appliquent et il ne peut pas créer de double réservation.

**52. Pourquoi « assistant temporairement indisponible » ? Comment changer la clé API ?**
Le crédit Anthropic était épuisé. Il faut acheter du crédit (console Anthropic, Plans & Billing) et mettre la clé dans le `.env` (`ANTHROPIC_API_KEY`), puis redémarrer le serveur.

## G. Paiement, tableau de bord, déploiement, limites

**53. Le paiement Mobile Money est-il réel ?**
**Non**, il est simulé : la route `/pay` enregistre la méthode et la référence. Pour un vrai paiement (PaySika par exemple), il faudrait un compte marchand, des clés de test, une route de création du paiement et un webhook signé, donc un serveur hébergé en ligne.

**54. Comment est le tableau de bord admin ?**
Il affiche les réservations du mois, les revenus du mois, les revenus à venir, les revenus de l'année mois par mois, le nombre de réservations en attente et le taux d'occupation du mois. Un bilan annuel donne aussi les réservations par salle, par statut, internes ou externes, et le taux d'occupation de l'année (`stats.py`).

**55. Comment sont calculés les « revenus du mois » ?**
On compte seulement les réservations **validées** et payantes dont la date d'événement tombe dans le mois. Par prudence comptable, un revenu n'est compté qu'après validation.

**56. Comment héberger le serveur ?**
Avec Docker : un Dockerfile pour l'API (uvicorn), docker-compose pour l'API et MySQL, et Caddy pour le HTTPS. Railway est proposé comme hébergeur (fichier `railway.json`), avec une base MySQL hébergée.

**57. Et sur le Play Store ?**
Il faut un compte développeur Google Play (environ 25 $, à payer une fois), un APK ou AAB signé, une fiche (description, captures, politique de confidentialité) et un serveur en ligne : sur le Play Store, l'appli ne peut pas dépendre d'un PC local. C'est prévu : le reçu peut même afficher un 2e QR code qui mène à la page de téléchargement (`APP_DOWNLOAD_URL`).

**58. Pourquoi l'appli ne se connecte plus quand on change de réseau ?**
Le serveur tourne sur le PC, et son adresse IP change selon le Wi-Fi (172.20.10.x ou 192.168.x.x). La solution est l'hébergement en ligne, avec une adresse fixe.

**59. Comment proposer l'appli en français et en anglais ?**
Avec l'internationalisation de Flutter (`flutter_localizations` et des fichiers de traduction `.arb`). J'ai choisi de rester en français pour le moment, la langue des utilisateurs du Collège ; c'est une amélioration possible, d'autant plus que le Collège est bilingue.

**60. Comment sont gérées les erreurs ?**
Avec `HTTPException` et des messages en français (400, 401, 403, 404, 409). Un gestionnaire global traite les erreurs 500, et les détails partent dans les logs.

**61. Où est la configuration ?**
Dans le `.env`, lu par `config.py`. Seul `.env.example` (sans les secrets) est publié sur GitHub.

**62. Qu'est-ce qui est fini, qu'est-ce qui reste à faire ?**
- Reste : le vrai Mobile Money, l'hébergement en ligne, la publication sur le Play Store, des statistiques plus poussées.
- **Piège** : « gérer les remises » et « consulter les anomalies » figurent sur le diagramme mais ne sont pas développés. Si on te le demande, dis-le franchement : ce sont des évolutions prévues.

**63. Quelles difficultés as-tu rencontrées ?**
Garder une seule règle de réservation pour l'API et pour l'IA, détecter les chevauchements d'horaires, empêcher la falsification des reçus, et gérer l'IP du serveur qui change selon le réseau.

## H. Code Flutter et modification en direct

**64. Comment est organisé le code Flutter ?**
Le dossier `lib/` contient `core` (thème, client API, session, validations), `models`, `screens`, `services` et `widgets`.

**65. Comment l'appli parle-t-elle au serveur ? Gestion d'état ?**
`ApiClient` (paquet `http`, avec le JWT) et les services. Pour l'état, Provider : `SessionProvider` (l'utilisateur connecté) et `ThemeModeProvider` (clair ou sombre).

**66. Si on te demande de changer une couleur en direct ?**
1. Ouvrir `retraite_mobile/lib/core/theme.dart`, classe `CollegeColors`, par exemple `green = Color(0xFF0B6E4F)`.
2. Changer le code hexadécimal (`0xFF` = opaque, suivi de RRVVBB). Tout le thème suit grâce à `ColorScheme.fromSeed`.
3. Appuyer sur `r` dans le terminal (hot reload) ou reconstruire l'APK.
- Pour un seul écran : mettre la couleur directement sur le widget (à éviter).
- Le logo est dans `assets/images` ; le nom de l'appli dans `kAppName` (`constants.dart`).
- Les couleurs du reçu PDF sont dans `receipts.py` (ReportLab) ; les reçus déjà générés ne changent pas.

---

## Mémo express (30 secondes avant d'entrer)

- Architecture : **Flutter → FastAPI → MySQL**
- Base : **MySQL, 5 tables, SQLAlchemy**
- FastAPI : **Python, rapide, validation Pydantic, doc `/docs`**
- Objectif : **informatiser la réservation du gymnase et de la salle des fêtes**
- IA : **2 assistants (client / admin), qui n'agissent que via mes fonctions**
- Création de l'IA : **API Claude + prompt système + outils + boucle de 6 tours max**
- Sécurité : **bcrypt + JWT 120 min + rôles + reçu signé HMAC + secrets dans .env**
- Anti double réservation : **find_conflict (même salle, même date, horaires qui se chevauchent)**
- Pièges : **pas Django · paiement simulé · remises/anomalies pas développées**

---

## Confiance en soi et éloquence

### La veille au soir
- Relis seulement les « réponses courtes » et le mémo express. Pas de nouveau contenu : tu connais déjà ton projet mieux que le jury.
- Prépare tes affaires (clé USB, PC chargé, APK installé sur le téléphone, chargeur) pour ne rien avoir à chercher le matin.
- Dors. Une nuit complète vaut plus qu'une heure de révision en plus.

### Le matin
- Mange un peu, bois de l'eau, évite trop de café (il fait trembler la voix).
- Relis le mémo express une fois, à voix haute.
- Juste avant d'entrer : respiration 4-4-6 (inspirer 4 secondes, bloquer 4, souffler 6), trois fois. Ça calme le cœur.
- Posture : dos droit, épaules ouvertes, deux minutes. Le corps envoie au cerveau le message que tout va bien.

### Pendant la présentation
- **Les deux premières phrases** : apprends-les par cœur. Une fois lancé, le stress baisse tout seul.
- **Parle lentement.** Le stress fait accélérer ; si tu as l'impression de parler un peu trop lentement, c'est la bonne vitesse.
- **Fais des pauses.** Un silence d'une seconde après une idée importante montre que tu es sûr de toi.
- **Regarde les membres du jury**, à tour de rôle, pas l'écran ni tes notes.
- **Dis « j'ai »** : « j'ai choisi FastAPI parce que… », « j'ai sécurisé la clé API… ». C'est ton travail, assume-le.
- Les mains : posées ou qui accompagnent la parole, jamais dans les poches.

### Face aux questions
- **Écoute la question jusqu'au bout**, sans couper.
- **Prends deux secondes** avant de répondre. C'est normal, et ça paraît réfléchi.
- Commence par la **réponse courte**, puis donne un détail. Ne récite pas tout ce que tu sais.
- **Si tu ne sais pas** : « Je n'ai pas approfondi ce point, mais voici comment je m'y prendrais… ». C'est beaucoup mieux qu'inventer.
- **Si tu n'as pas compris** : « Pouvez-vous reformuler, s'il vous plaît ? ». C'est une question normale.
- Une critique du jury n'est pas une attaque. Réponds : « C'est une bonne remarque, c'est une amélioration que je peux prévoir », puis cite une piste.

### Phrases utiles
- « Pour faire simple, … »
- « Le choix s'explique par deux raisons : … et … »
- « Concrètement, dans l'application, ça donne… »
- « Avec plus de temps, j'aurais ajouté… »

### À se dire avant d'entrer
Tu as construit une application complète : un mobile, une API, une base de données, une IA, des reçus PDF avec QR code et un déploiement Docker. Le jury vient voir ce que tu as fait, pas te piéger. Tu es la personne qui connaît le mieux ce projet dans la salle.
