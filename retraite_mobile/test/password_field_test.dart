import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:retraite_mobile/widgets/password_field.dart';

void main() {
  testWidgets("L'œil affiche puis masque le mot de passe", (tester) async {
    final controller = TextEditingController(text: 'Secret123!');
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(body: PasswordField(controller: controller, label: 'Mot de passe')),
    ));

    bool obscured() => tester.widget<EditableText>(find.byType(EditableText)).obscureText;

    expect(obscured(), isTrue);
    await tester.tap(find.byIcon(Icons.visibility_outlined));
    await tester.pump();
    expect(obscured(), isFalse);
    await tester.tap(find.byIcon(Icons.visibility_off_outlined));
    await tester.pump();
    expect(obscured(), isTrue);
  });
}
