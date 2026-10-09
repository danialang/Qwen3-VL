import 'package:shared_preferences/shared_preferences.dart';

import 'constants.dart';

const String _prefsKey = 'api_base_url';

/// Adresse du serveur choisie par l'utilisateur (ex. IP du PC sur le Wi-Fi),
/// ou l'adresse par défaut si aucune n'a été enregistrée.
Future<String> loadServerAddress() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_prefsKey) ?? kApiBaseUrl;
}

Future<void> saveServerAddress(String address) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(_prefsKey, address);
}

/// Accepte "192.168.1.20:8000" ou "http://192.168.1.20:8000/" et renvoie
/// une adresse propre (avec http://, sans "/" final).
String normalizeServerAddress(String input) {
  var value = input.trim();
  if (value.isEmpty) return kApiBaseUrl;
  if (!value.startsWith('http://') && !value.startsWith('https://')) {
    value = 'http://$value';
  }
  while (value.endsWith('/')) {
    value = value.substring(0, value.length - 1);
  }
  return value;
}
