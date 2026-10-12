import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';
import 'package:retraite_mobile/core/api_client.dart';
import 'package:retraite_mobile/core/session.dart';
import 'package:retraite_mobile/models/user.dart';
import 'package:retraite_mobile/screens/home/home_screen.dart';
import 'package:retraite_mobile/core/theme_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

AppUser _user(UserRole role) => AppUser(
      id: 1,
      email: 'cl@gmail.com',
      fullName: 'Client Test',
      phone: null,
      role: role,
      createdAt: DateTime(2026),
    );

Widget _app(SessionProvider session) => MultiProvider(
      providers: [
        ChangeNotifierProvider<SessionProvider>.value(value: session),
        ChangeNotifierProvider<ThemeModeProvider>(create: (_) => ThemeModeProvider()),
      ],
      child: const MaterialApp(home: HomeScreen()),
    );

void main() {
  testWidgets('le client peut supprimer son compte avec son mot de passe, puis il est déconnecté', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(360, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    String? sentPassword;
    final client = MockClient((request) async {
      if (request.url.path == '/auth/delete-account') {
        sentPassword = (jsonDecode(request.body) as Map<String, dynamic>)['password'] as String?;
        return http.Response('{"detail":"Compte supprimé."}', 200, headers: {'content-type': 'application/json; charset=utf-8'});
      }
      return http.Response('[]', 200);
    });

    await http.runWithClient(() async {
      final api = ApiClient();
      final session = SessionProvider(api);
      await session.setSession('jeton', _user(UserRole.client));
      await tester.pumpWidget(_app(session));
      await tester.pumpAndSettle();

      expect(find.text('Politique de confidentialité'), findsOneWidget);
      await tester.tap(find.text('Supprimer mon compte'));
      await tester.pumpAndSettle();

      // Le bouton reste bloqué tant que la case n'est pas cochée.
      final button = find.widgetWithText(ElevatedButton, 'Supprimer définitivement mon compte');
      expect(tester.widget<ElevatedButton>(button).onPressed, isNull);

      await tester.enterText(find.byType(TextFormField), 'MonMotDePasse1!');
      await tester.tap(find.byType(Checkbox));
      await tester.pump();
      expect(tester.widget<ElevatedButton>(button).onPressed, isNotNull);

      await tester.tap(button);
      await tester.pumpAndSettle();

      expect(sentPassword, 'MonMotDePasse1!');
      expect(session.isAuthenticated, isFalse);
      expect(find.text('Votre compte a été supprimé.'), findsOneWidget);
    }, () => client);
  });

  testWidgets("l'administrateur n'a pas le bouton de suppression de compte", (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(360, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final session = SessionProvider(ApiClient());
    await session.setSession('jeton', _user(UserRole.admin));
    await tester.pumpWidget(_app(session));
    await tester.pumpAndSettle();
    expect(find.text('Supprimer mon compte'), findsNothing);
    expect(find.text('Politique de confidentialité'), findsOneWidget);
  });
}
