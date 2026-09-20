# App mobile — Réservation Collège de la Retraite (Flutter)

## Prérequis

- Flutter SDK (stable) installé, `flutter doctor` sans erreur bloquante.
- Le backend FastAPI (`../retraite-backend`) doit tourner et être accessible depuis le
  téléphone/émulateur.

## Setup

```bash
cd retraite_mobile
flutter pub get
```

## Lancer sur émulateur Android

Par défaut l'app pointe vers `http://10.0.2.2:8000` (équivalent de `localhost:8000` de la
machine hôte depuis l'émulateur Android) :

```bash
flutter run
```

## Lancer sur téléphone Android physique (USB/ADB)

Rediriger le port du téléphone vers le backend local, puis lancer avec l'IP loopback :

```bash
adb reverse tcp:8000 tcp:8000
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

Ou, si le téléphone est sur le même Wi-Fi que le PC, utiliser l'IP locale du PC
(ex. `192.168.1.20`) :

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.1.20:8000
```

## Comptes de test

Utiliser les comptes seedés par le backend (`.env` du backend) :
- Admin Collège : `ecoretraite@gmail.com`
- Dev : `DEV_EMAIL` défini dans `.env`
- Ou inscrire un compte client via l'écran d'inscription.

## Images du Collège

Aucune image officielle n'est encore intégrée. Le logo (`assets/images/logo.png`) et la
bannière d'accueil (`assets/images/accueil.jpg`) affichent un repli visuel (dégradé vert +
icône) tant que ces fichiers ne sont pas déposés dans `assets/images/`. Aucune autre
modification de code n'est nécessaire une fois les visuels reçus.

## Paiement (mode test)

Aucun identifiant sandbox PaySika/PayPal n'était disponible pour ce MVP : l'écran de
paiement simule un paiement réussi et enregistre une référence de test côté backend
(`POST /reservations/{id}/pay`). Pour brancher la vraie passerelle : renseigner
`PaymentService.gatewayCheckoutUrl` dans `lib/services/payment_service.dart` et adapter
l'écran `lib/screens/booking/payment_screen.dart` pour ouvrir cette URL via `url_launcher`.

## Écrans

- Connexion / Inscription (redirection directe vers l'accueil)
- Accueil (accès admin conditionnel, mode sombre)
- Choix de salle avec matériel dépliable (flèche)
- Règlement intérieur + case à cocher obligatoire
- Calendrier (créneaux occupés visibles, création de réservation)
- Paiement test
- Mes réservations (code couleur vert/jaune/rouge) + détail + téléchargement du reçu PDF
- Admin : comptes inscrits, réservations à valider / toutes (internes visibles distinctement)
