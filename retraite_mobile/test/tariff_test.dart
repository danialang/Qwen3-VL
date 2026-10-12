import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:retraite_mobile/models/reservation.dart';
import 'package:retraite_mobile/models/tariff.dart';
import 'package:retraite_mobile/widgets/price_breakdown.dart';

void main() {
  test('chaque espace a une valeur API unique et se retrouve depuis le serveur', () {
    final values = Room.values.map((r) => r.apiValue).toSet();
    expect(values.length, Room.values.length);
    for (final room in Room.values) {
      expect(RoomApi.fromApi(room.apiValue), room);
      expect(room.label, isNotEmpty);
    }
  });

  test('le catalogue des tarifs est lu depuis le JSON du serveur', () {
    final catalog = TariffCatalog.fromJson({
      'categories': [
        {'key': 'personnel_exterieur', 'label': 'Personnel extérieur'},
      ],
      'extras': [
        {'key': 'table_simple', 'label': 'Table simple', 'group': 'tables', 'unit_price': 2000},
      ],
      'spaces': [
        {'key': 'gymnase', 'extras_allowed': true},
        {'key': 'tatami', 'extras_allowed': false},
      ],
      'deposit': 500000,
      'note': 'forfait',
    });
    expect(catalog.categories.single.label, 'Personnel extérieur');
    expect(catalog.extras.single.unitPrice, 2000);
    expect(catalog.allowsExtras('gymnase'), isTrue);
    expect(catalog.allowsExtras('tatami'), isFalse);
    expect(catalog.deposit, 500000);
  });

  test("une réservation d'ancienne version (sans tarifs) se lit toujours", () {
    final r = Reservation.fromJson({
      'id': 1,
      'room': 'gymnase',
      'event_date': '2026-01-01',
      'start_time': '08:00:00',
      'end_time': '10:00:00',
      'status': 'pending',
      'amount': '5000000.00',
      'is_internal': false,
      'user_id': 2,
      'created_at': '2026-01-01T08:00:00',
    });
    expect(r.deposit, 0);
    expect(r.extras, isEmpty);
    expect(r.totalDue, 5000000);
  });

  test('la réservation détaille location, prestations, caution et montant à verser', () {
    final r = Reservation.fromJson({
      'id': 2,
      'room': 'salle_fetes',
      'event_date': '2026-01-01',
      'start_time': '08:00:00',
      'end_time': '23:00:00',
      'status': 'pending',
      'amount': '5100000.00',
      'deposit': '500000.00',
      'client_category_label': 'Personnel extérieur',
      'duration_label': 'Journée',
      'extras': [
        {'key': 'chaise_vip_prestige', 'label': 'Chaise VIP Prestige', 'quantity': 20, 'unit_price': 5000, 'total': 100000},
      ],
      'is_internal': false,
      'user_id': 2,
      'created_at': '2026-01-01T08:00:00',
    });
    expect(r.room, Room.salleFetes);
    expect(r.totalDue, 5600000);
    final p = PriceBreakdown.fromReservation(r);
    expect(p.rental, 5000000);
    expect(p.total, 5100000);
    expect(p.totalDue, 5600000);
  });

  testWidgets('le détail du prix affiche le montant à verser', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: PriceBreakdown(
          categoryLabel: 'Partenaire public',
          durationLabel: 'Moins de 5 heures',
          rental: 1000000,
          extras: [QuoteLine(key: 'table_simple', label: 'Table simple', quantity: 10, unitPrice: 2000, total: 20000)],
          total: 1020000,
          deposit: 500000,
          totalDue: 1520000,
        ),
      ),
    ));
    expect(find.text('Partenaire public'), findsOneWidget);
    expect(find.text('Table simple × 10'), findsOneWidget);
    expect(find.text('1 520 000 FCFA'), findsOneWidget);
    expect(find.text('Caution remboursable'), findsOneWidget);
  });
}
