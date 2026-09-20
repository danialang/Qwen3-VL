# Guide d'installation et de test sur téléphone Android (depuis VS Code)

Ce guide explique comment installer et tester l'application de réservation sur un
téléphone Android, à partir de VS Code sous Windows.

---

## 1. Prérequis (une seule fois)

1. Installer **VS Code** (https://code.visualstudio.com/).
2. Dans VS Code, installer les extensions **Flutter** et **Dart** (icône Extensions dans la
   barre latérale, rechercher "Flutter", cliquer sur Installer — l'extension Dart s'installe
   automatiquement avec).
3. Installer le **SDK Flutter** (https://docs.flutter.dev/get-started/install/windows) et
   l'ajouter au PATH Windows.
4. Installer **Android Studio** (juste pour obtenir les outils "Android SDK" et
   "platform-tools"/ADB — pas besoin de l'utiliser comme éditeur).
5. Ouvrir un terminal et vérifier que tout est en ordre :
   ```
   flutter doctor
   ```
   Corriger les éventuelles croix rouges affichées (licences Android à accepter :
   `flutter doctor --android-licenses`).

---

## 2. Démarrer le backend

L'application mobile a besoin du backend FastAPI en cours d'exécution.

1. Démarrer **WampServer** (le service MySQL doit être vert/actif).
2. Dans un terminal, dans le dossier `retraite-backend` :
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
   Éditer `.env` : renseigner `DATABASE_URL`, `SECRET_KEY`, les comptes `DEV_EMAIL`/`ADMIN_EMAIL`,
   et `ANTHROPIC_API_KEY` si vous voulez tester l'assistant IA.
3. Lancer le serveur :
   ```
   uvicorn app.main:app --host 0.0.0.0 --reload
   ```
   `--host 0.0.0.0` est important : cela permet au téléphone de joindre le serveur sur le réseau.
4. Vérifier que ça répond : ouvrir http://127.0.0.1:8000/health dans un navigateur (doit
   afficher `{"status":"ok"}`).

---

## 3. Connecter le téléphone Android en USB

1. Sur le téléphone : **Paramètres → À propos du téléphone**, taper 7 fois sur "Numéro de
   build" pour activer le **mode développeur**.
2. **Paramètres → Options pour les développeurs** : activer **Débogage USB**.
3. Brancher le téléphone au PC avec un câble USB.
4. Sur le téléphone, autoriser l'ordinateur quand la pop-up "Autoriser le débogage USB ?"
   apparaît (cocher "Toujours autoriser").
5. Vérifier la détection, dans un terminal :
   ```
   adb devices
   ```
   Le téléphone doit apparaître avec le statut `device` (pas `unauthorized` ni `offline`).

---

## 4. Configurer l'adresse du serveur pour le téléphone

Le téléphone physique ne peut pas utiliser `10.0.2.2` (réservé aux émulateurs). Deux options :

**Option A — adb reverse (recommandé, le plus simple) :**
```
adb reverse tcp:8000 tcp:8000
```
Le téléphone pourra alors joindre le backend via `http://127.0.0.1:8000` comme s'il tournait
localement (à refaire à chaque redémarrage du téléphone/câble).

**Option B — IP locale du PC :**
Trouver l'IP du PC sur le Wi-Fi (`ipconfig`, ligne "Adresse IPv4", ex. `192.168.1.20`) et
utiliser cette IP au lancement (voir étape 5). Le téléphone et le PC doivent être sur le même
réseau Wi-Fi, et le pare-feu Windows doit autoriser le port 8000.

---

## 5. Lancer l'application depuis VS Code

1. Ouvrir le dossier `retraite_mobile` dans VS Code (**Fichier → Ouvrir un dossier**).
2. Dans un terminal VS Code, installer les dépendances :
   ```
   flutter pub get
   ```
3. En bas à droite de VS Code, choisir le téléphone comme cible d'exécution (au lieu de
   "Chrome" ou d'un émulateur).
4. Lancer l'app :
   - Avec **adb reverse** (option A) : appuyer sur **F5** (ou "Run and Debug"), ou en
     terminal :
     ```
     flutter run
     ```
   - Avec l'**IP locale** (option B) :
     ```
     flutter run --dart-define=API_BASE_URL=http://192.168.1.20:8000
     ```
     (remplacer par votre IP).
5. L'application s'installe et se lance automatiquement sur le téléphone. Les modifications de
   code sont rechargeables à chaud avec la touche `r` dans le terminal (hot reload).

---

## 6. Alternative : générer un APK et l'installer manuellement

Si vous ne voulez pas garder VS Code/le câble branchés en permanence :

1. Générer l'APK :
   ```
   flutter build apk --release --dart-define=API_BASE_URL=http://192.168.1.20:8000
   ```
   (utiliser l'IP du PC ou celle du serveur si le backend est hébergé ailleurs).
2. Le fichier est créé dans `build\app\outputs\flutter-apk\app-release.apk`.
3. Installer sur le téléphone connecté en USB :
   ```
   adb install build\app\outputs\flutter-apk\app-release.apk
   ```
   Ou transférer le fichier `.apk` sur le téléphone (câble, email, cloud) et l'ouvrir
   directement depuis le gestionnaire de fichiers du téléphone (autoriser "Installer des
   applications inconnues" si demandé).

---

## 7. Comptes de test

- **Admin Collège** : email `ADMIN_EMAIL` défini dans `.env` du backend (par défaut
  `ecoretraite@gmail.com`), mot de passe `ADMIN_PASSWORD`.
- **Développeur** : email/mot de passe `DEV_EMAIL`/`DEV_PASSWORD` du `.env`.
- **Client** : à créer via l'écran "Inscription" de l'application.

## 8. Parcours à tester

1. Inscription d'un compte client → redirection directe vers l'accueil.
2. Réservation du Gymnase, puis de la Salle des fêtes (choisir une date/heure libre).
3. Tenter de réserver sur un créneau déjà pris → message de conflit avec date suggérée.
4. Paiement test (Orange Money / MTN via PaySika, ou PayPal Sandbox).
5. Se connecter en admin, valider la réservation externe → le reçu PDF devient disponible.
6. Se connecter en admin et créer une réservation (elle est gratuite et validée automatiquement,
   visible comme "réservation interne" dans le calendrier).
7. Vérifier les couleurs de statut dans "Mes réservations" (vert = validée, jaune = en attente,
   rouge = annulée).
8. Tester l'assistant IA (bouton "Assistant IA" sur l'accueil) : demander une réservation en
   langage naturel.
9. En admin, tester l'assistant IA admin (ex. "combien de réservations ce mois-ci ?", "fais-moi
   le bilan 2026").

---

## 9. Dépannage

| Problème | Solution |
|---|---|
| `adb devices` n'affiche rien | Réinstaller le pilote USB du téléphone, essayer un autre câble/port, vérifier le débogage USB activé |
| L'app ne contacte pas le serveur | Vérifier que `uvicorn` tourne avec `--host 0.0.0.0`, refaire `adb reverse tcp:8000 tcp:8000`, vérifier le pare-feu Windows |
| `flutter doctor` signale Android non configuré | Ouvrir Android Studio une fois pour terminer l'installation du SDK, puis relancer `flutter doctor --android-licenses` |
| Erreur 503 sur l'assistant IA | La clé `ANTHROPIC_API_KEY` n'est pas renseignée dans le `.env` du backend |
| Écran blanc / crash au lancement | Vérifier la sortie du terminal `flutter run` pour l'erreur exacte, relancer avec `flutter clean && flutter pub get` |
