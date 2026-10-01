import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:retraite_mobile/models/reservation.dart';

void main() {
  test('formatTime donne toujours le format 24 h', () {
    expect(formatTime(const TimeOfDay(hour: 0, minute: 0)), '00:00');
    expect(formatTime(const TimeOfDay(hour: 9, minute: 5)), '09:05');
    expect(formatTime(const TimeOfDay(hour: 12, minute: 0)), '12:00');
    expect(formatTime(const TimeOfDay(hour: 14, minute: 30)), '14:30');
    expect(formatTime(const TimeOfDay(hour: 23, minute: 59)), '23:59');
  });

  testWidgets("Le sélecteur d'heure s'ouvre en 24 h (pas de AM/PM)", (tester) async {
    await tester.pumpWidget(MaterialApp(
      builder: (context, child) => MediaQuery(
        data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: true),
        child: child!,
      ),
      home: Builder(
        builder: (context) => ElevatedButton(
          onPressed: () => showTimePicker(context: context, initialTime: const TimeOfDay(hour: 14, minute: 0)),
          child: const Text('ouvrir'),
        ),
      ),
    ));
    await tester.tap(find.text('ouvrir'));
    await tester.pumpAndSettle();
    expect(find.text('AM'), findsNothing);
    expect(find.text('PM'), findsNothing);
    expect(find.text('14'), findsWidgets);
  });
}
