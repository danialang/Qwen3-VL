import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:retraite_mobile/main.dart';

void main() {
  testWidgets('RetraiteApp démarre sur l\'écran de connexion ou l\'accueil', (WidgetTester tester) async {
    await tester.pumpWidget(const RetraiteApp());
    await tester.pump();

    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
