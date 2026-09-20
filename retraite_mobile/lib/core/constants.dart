/// Adresse du backend FastAPI. En développement Android via émulateur,
/// 10.0.2.2 pointe vers le localhost de la machine hôte (WampServer).
/// Sur un téléphone physique en USB/ADB reverse : garder 127.0.0.1 avec
/// `adb reverse tcp:8000 tcp:8000`, ou remplacer par l'IP locale du PC.
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

const String kAppName = 'Réservation - Collège de la Retraite';

const List<String> kEquipmentsGymnase = [
  'Paniers de basket',
  'Petits buts',
  'Filets de volley',
];

const List<String> kEquipmentsSalleDesFetes = [
  'Chaises, tables, couverts',
  'Sonorisation',
  'Sécurité',
  '2 appartements modernes (repos)',
  'Cuisine',
  'Toilettes externes',
];

const String kReglementInterieur = '''
RÈGLEMENT INTÉRIEUR — LOCATION DU GYMNASE ET DE LA SALLE DES FÊTES

1. Objet
Le présent règlement encadre l'utilisation du gymnase et de la salle des fêtes
du Collège Catholique Bilingue de la Retraite par toute personne ou organisation
externe, dans le respect des valeurs de l'établissement.

2. Réservation et priorité
Le Collège reste prioritaire pour ses propres activités (sport, réunions, fêtes
internes). Toute réservation externe est soumise à validation par l'administration
et peut être refusée en cas de chevauchement avec un événement interne.

3. Paiement
Le montant de la location est fixe et dû avant la validation définitive de la
réservation. Un reçu et un code de sécurité uniques sont délivrés après validation.

4. Utilisation des lieux
Le locataire s'engage à utiliser les équipements mis à disposition avec soin,
à respecter les horaires réservés et à restituer les lieux propres et en bon état.
Tout dommage constaté sera facturé au locataire.

5. Sécurité
Le respect des consignes de sécurité du Collège est obligatoire. L'accès aux zones
non concernées par la réservation est interdit.

6. Annulation
Toute annulation doit être signalée à l'administration dans les meilleurs délais.

En cochant la case d'acceptation, vous reconnaissez avoir lu et accepté
l'intégralité du présent règlement.
''';
