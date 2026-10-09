import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:retraite_mobile/core/api_client.dart';
import 'package:retraite_mobile/core/session.dart';
import 'package:retraite_mobile/screens/auth/login_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('Le lien "Mot de passe oublié ?" ouvre l\'écran de réinitialisation avec l\'email déjà saisi', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(800, 1400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => SessionProvider(ApiClient()),
        child: const MaterialApp(home: LoginScreen()),
      ),
    );
    await tester.pump();

    await tester.enterText(find.widgetWithText(TextFormField, 'Email'), 'cl@test.com');
    expect(find.text('Mot de passe oublié ?'), findsOneWidget);
    await tester.tap(find.text('Mot de passe oublié ?'));
    await tester.pumpAndSettle();

    expect(find.text('Envoyer le code'), findsOneWidget);
    expect(find.text('cl@test.com'), findsOneWidget);
  });
}
