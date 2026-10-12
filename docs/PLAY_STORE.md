# Publier l'application sur le Google Play Store

Guide pas à pas. Rien de secret ne s'écrit dans ce fichier : mots de passe et clés restent dans GitHub (Secrets), jamais dans le dépôt.

**Les 6 étapes**

1. Mettre le serveur en ligne (adresse `https://...`).
2. Créer le compte Google Play Console.
3. Fabriquer la clé de signature de l'application.
4. Construire le fichier `.aab` avec GitHub.
5. Remplir la fiche de l'application dans la Play Console.
6. Tester, puis publier.

---

## 1. Mettre le serveur en ligne (exemple Railway)

Le Play Store exige que l'application parle à un serveur en **HTTPS**. Ton PC ne peut pas faire ça : il faut un hébergeur.
Les écrans de Railway changent parfois un peu, mais les idées restent les mêmes.

1. Créer un compte sur railway.com (le plus simple : « Login with GitHub »).
2. **New Project > Deploy from GitHub repo** > choisir `danialang/Qwen3-VL`.
3. Dans le service créé : **Settings** :
   - *Root Directory* : `retraite-backend` (Railway trouve alors le `Dockerfile` tout seul) ;
   - *Branch* : `claude/retraite-backend-day1-lv91aj` (ou ta branche principale plus tard) ;
   - *Healthcheck Path* : `/health`.
4. Ajouter la base : **+ New > Database > MySQL**.
5. Dans le service de l'API, onglet **Variables**, ajouter :

| Variable | Valeur |
|---|---|
| `DATABASE_URL` | `${{MySQL.MYSQL_URL}}` (référence à la base créée) |
| `SECRET_KEY` | une longue chaîne au hasard (voir ci-dessous) |
| `ADMIN_EMAIL` | l'email du compte administrateur du Collège |
| `ADMIN_PASSWORD` | un mot de passe solide (8 caractères minimum, 1 majuscule, 1 chiffre, 1 symbole) |
| `CONTACT_EMAIL` | l'email affiché dans la politique de confidentialité |
| `PUBLIC_BASE_URL` | l'adresse HTTPS du serveur (à remplir à l'étape suivante) |
| `ANTHROPIC_API_KEY` | une **nouvelle** clé (l'assistant IA ; il faut aussi des crédits chez Anthropic) |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_FROM` | pour l'email « mot de passe oublié » (Gmail : `smtp.gmail.com`, `587`, et un **mot de passe d'application**) |

   Fabriquer `SECRET_KEY` : `python -c "import secrets; print(secrets.token_hex(32))"`.
6. **Settings > Networking > Generate Domain** : Railway donne une adresse du genre `https://xxxx.up.railway.app`.
   La recopier dans `PUBLIC_BASE_URL` (sans `/` à la fin).
7. Vérifier dans un navigateur : `https://xxxx.up.railway.app/health` répond `{"status":"ok"}`, `/privacy` affiche la politique de
   confidentialité, `/account-deletion` la page de suppression de compte.

> Les reçus PDF sont refabriqués automatiquement s'ils disparaissent (le disque de l'hébergeur est temporaire).
> Les données importantes sont dans MySQL, qui est conservé par Railway.

Plus tard, un nom de domaine à toi (ex. `api.collegedelaretraite.com`) est possible : on le branche dans Railway sans
changer l'application, seulement la variable GitHub `API_BASE_URL` (étape 4).

## 2. Créer le compte Google Play Console

1. Aller sur play.google.com/console/signup avec le compte Google qui servira à publier.
2. Choisir le **type de compte** :
   - *Personnel* : plus rapide, mais pour un compte personnel récent Google demande d'abord un **test fermé** (environ
     12 testeurs pendant 14 jours consécutifs) avant d'autoriser la publication publique. À vérifier dans la console,
     la règle peut changer.
   - *Organisation* (au nom du Collège ou de l'Archidiocèse) : demande un numéro D-U-N-S et plus de papiers, mais pas
     cette obligation de testeurs.
3. Payer les **25 $** (une seule fois) et vérifier l'identité (pièce d'identité, téléphone). La vérification peut durer
   quelques jours.

## 3. Fabriquer la clé de signature (une seule fois, à garder toute la vie de l'application)

Sans cette clé, impossible de mettre à jour l'application. **Sauvegarde-la dans au moins deux endroits** (clé USB,
cloud privé). Ne l'envoie jamais à personne et ne la mets jamais sur GitHub.

1. Installer Java (JDK 17) s'il n'est pas déjà là. Sous Windows, dans PowerShell : `winget install EclipseAdoptium.Temurin.17.JDK`.
   Fermer puis rouvrir PowerShell.
2. Fabriquer la clé (choisir un mot de passe solide, le noter) :

```powershell
keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

3. Transformer le fichier en texte pour GitHub (il est copié dans le presse-papiers) :

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("upload-keystore.jks")) | Set-Clipboard
```

4. Sur GitHub : dépôt > **Settings > Secrets and variables > Actions > New repository secret**. Créer 4 secrets :

| Nom | Valeur |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | le texte copié à l'étape 3 |
| `ANDROID_KEYSTORE_PASSWORD` | le mot de passe choisi à l'étape 2 |
| `ANDROID_KEY_ALIAS` | `upload` |
| `ANDROID_KEY_PASSWORD` | le même mot de passe (ou celui demandé pour la clé) |

5. Dans l'onglet **Variables** (juste à côté de Secrets) : créer la variable `API_BASE_URL` = l'adresse HTTPS du serveur
   (étape 1), sans `/` à la fin.

Dans la Play Console, laisser **Play App Signing** activé (c'est le choix par défaut) : Google garde la clé finale et ta
clé « upload » ne sert qu'à envoyer les versions.

## 4. Construire le fichier `.aab`

1. Sur GitHub : onglet **Actions > Build Play Store (AAB signé) > Run workflow**.
2. Attendre la fin (quelques minutes). Si ça échoue sur « Secrets manquants » ou « API_BASE_URL », revenir à l'étape 3.
3. Ouvrir l'exécution terminée, télécharger l'artefact **retraite-playstore-aab** (un zip qui contient `app-release.aab`).

Chaque exécution augmente le numéro de version automatiquement, comme le Play Store l'exige.

## 5. Remplir la fiche dans la Play Console

1. **Créer l'application** : nom, langue par défaut français, type *Application*, gratuite.
2. **Accès à l'application** : l'application demande une connexion. Créer un compte client de démonstration
   (inscription normale dans l'application) et donner son email et son mot de passe dans cette rubrique, pour que les
   examinateurs de Google puissent entrer.
3. **Politique de confidentialité** : `https://VOTRE-SERVEUR/privacy`.
4. **Suppression de compte** (section sécurité des données) : suppression possible dans l'application et via
   `https://VOTRE-SERVEUR/account-deletion`.
5. **Sécurité des données** (le formulaire de déclaration) : données recueillies = nom, email, téléphone (facultatif),
   historique de réservations/paiements, messages envoyés à l'assistant ; chiffrées pendant le transfert (HTTPS) ;
   partagées avec l'hébergeur et Anthropic (assistant) ; l'utilisateur peut demander la suppression.
6. **Publicités** : aucune. **Public cible** : adultes (18 ans et plus). **Classification du contenu** : remplir le questionnaire (aucun contenu sensible).
7. **Fiche principale** : les textes prêts à copier sont dans `docs/fiche-boutique.md`. Il faut aussi : une icône 512x512,
   une image de présentation 1024x500 et au moins 2 captures d'écran de téléphone.
8. **Pays** : Cameroun (et d'autres si besoin).
9. Importer le `.aab` dans **Tests internes** d'abord (c'est immédiat), puis passer en **Tests fermés**, puis en **Production**.

## 6. Avant la publication publique

- **Paiement** : aujourd'hui le paiement est une simulation (« mode test »). Avant d'ouvrir l'application au public, il
  faut soit brancher un vrai paiement Mobile Money, soit afficher clairement que le paiement se fait auprès de
  l'économat. Ne pas écrire dans la fiche « paiement Mobile Money » tant qu'il n'est pas réel (Google refuse les
  descriptions trompeuses).
- Vérifier le rapport « Pre-launch » de la Play Console (plantages, accessibilité).
- Garder à jour la politique de confidentialité si de nouvelles données sont recueillies.
- **App Store (iPhone)** : plus tard. Il faudra un compte Apple Developer (99 $/an) et un Mac (ou un service qui construit
  l'application iOS dans le cloud).
