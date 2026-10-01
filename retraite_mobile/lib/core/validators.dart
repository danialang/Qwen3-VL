/// Fournisseurs d'email acceptés à l'inscription (garder cette liste identique à celle du serveur).
const allowedEmailDomains = {
  'gmail.com', 'googlemail.com',
  'icloud.com', 'me.com', 'mac.com',
  'outlook.com', 'outlook.fr', 'hotmail.com', 'hotmail.fr', 'live.com', 'live.fr',
  'yahoo.com', 'yahoo.fr',
  'proton.me', 'protonmail.com',
};

final _emailShape = RegExp(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$');
final _namePattern = RegExp(r"^\p{L}+(?:[ '’\-]\p{L}+)*$", unicode: true);

/// Renvoie un message d'erreur, ou null si le nom est valide (lettres seulement, pas de chiffres).
String? validateFullName(String? value) {
  final name = (value ?? '').trim();
  if (name.isEmpty) return 'Champ obligatoire';
  if (name.length < 2 || !_namePattern.hasMatch(name)) {
    return 'Le nom ne doit contenir que des lettres (pas de chiffres)';
  }
  return null;
}

/// Renvoie un message d'erreur, ou null si l'email est une vraie adresse d'un fournisseur connu.
String? validateEmailAddress(String? value) {
  final email = (value ?? '').trim();
  if (email.isEmpty) return 'Champ obligatoire';
  if (!_emailShape.hasMatch(email)) return 'Adresse email invalide';
  final domain = email.split('@').last.toLowerCase();
  if (!allowedEmailDomains.contains(domain)) {
    return 'Utilisez une vraie adresse, par exemple nom@gmail.com ou nom@icloud.com';
  }
  return null;
}
