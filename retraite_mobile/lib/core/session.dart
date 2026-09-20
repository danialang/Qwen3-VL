import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/user.dart';
import '../services/auth_service.dart';
import 'api_client.dart';

/// État d'authentification global de l'app, partagé via Provider.
class SessionProvider extends ChangeNotifier {
  final ApiClient api;
  late final AuthService _authService;

  AppUser? user;
  String? token;
  bool restoring = true;

  SessionProvider(this.api) {
    _authService = AuthService(api);
  }

  bool get isAuthenticated => token != null && user != null;

  Future<void> restore() async {
    final prefs = await SharedPreferences.getInstance();
    final savedToken = prefs.getString('token');
    if (savedToken != null) {
      api.setToken(savedToken);
      try {
        user = await _authService.me();
        token = savedToken;
      } catch (_) {
        await prefs.remove('token');
        api.setToken(null);
      }
    }
    restoring = false;
    notifyListeners();
  }

  Future<void> setSession(String newToken, AppUser newUser) async {
    token = newToken;
    user = newUser;
    api.setToken(newToken);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', newToken);
    notifyListeners();
  }

  Future<void> logout() async {
    token = null;
    user = null;
    api.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    notifyListeners();
  }
}
