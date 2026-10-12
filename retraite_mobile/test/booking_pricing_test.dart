import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';
import 'package:retraite_mobile/core/api_client.dart';
import 'package:retraite_mobile/core/session.dart';
import 'package:retraite_mobile/models/reservation.dart';
import 'package:retraite_mobile/models/user.dart';
import 'package:retraite_mobile/screens/booking/calendar_screen.dart';
import 'package:retraite_mobile/screens/rooms/room_selection_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _catalog = {
  'categories': [
    {'key': 'personnel_college', 'label': 'Personnel du Collège'},
    {'key': 'personnel_exterieur', 'label': 'Personnel extérieur'},
    {'key': 'partenaire_public', 'label': 'Partenaire public'},
  ],
  'extras': [
    {'key': 'table_simple', 'label': 'Table simple', 'group': 'tables', 'unit_price': 2000},
  ],
  'spaces': [
    {'key': 'gymnase', 'extras_allowed': true},
    {'key': 'tatami', 'extras_allowed': false},
  ],
  'deposit': 500000,
  'note': '',
};

http.Response _json(Object body, [int status = 200]) =>
    http.Response(jsonEncode(body), status, headers: {'content-type': 'application/json; charset=utf-8'});

Map<String, dynamic> _quoteFor(Map<String, dynamic> body) {
  final isPublic = body['client_category'] == 'partenaire_public';
  final extras = (body['extras'] as List).cast<Map<String, dynamic>>();
  final tables = extras.fold<int>(0, (s, e) => s + (e['quantity'] as int));
  final rental = isPublic ? 1000000 : 750000;
  final extrasTotal = tables * 2000;
  return {
    'room': body['room'],
    'client_category': body['client_category'],
    'client_category_label': isPublic ? 'Partenaire public' : 'Personnel extérieur',
    'duration_type': 'short',
    'duration_label': 'Moins de 5 heures',
    'rental': rental,
    'extras': [
      for (final e in extras)
        {'key': e['key'], 'label': 'Table simple', 'quantity': e['quantity'], 'unit_price': 2000, 'total': (e['quantity'] as int) * 2000},
    ],
    'extras_total': extrasTotal,
    'total': rental + extrasTotal,
    'deposit': 500000,
    'total_due': rental + extrasTotal + 500000,
  };
}

void main() {
  testWidgets('le client voit le prix, choisit sa catégorie et ses prestations, puis réserve', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(360, 3200));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final posted = <Map<String, dynamic>>[];
    final client = MockClient((request) async {
      final path = request.url.path;
      if (path == '/tariffs') return _json(_catalog);
      if (path == '/reservations/availability') return http.Response('[]', 200);
      if (path == '/reservations/quote') {
        return _json(_quoteFor(jsonDecode(request.body) as Map<String, dynamic>));
      }
      if (path == '/reservations' && request.method == 'POST') {
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        posted.add(body);
        final quote = _quoteFor(body);
        return _json(
          {
            'id': 7,
            'room': body['room'],
            'event_date': body['event_date'],
            'start_time': body['start_time'],
            'end_time': body['end_time'],
            'status': 'pending',
            'amount': '${quote['total']}.00',
            'deposit': '500000.00',
            'client_category_label': quote['client_category_label'],
            'duration_label': quote['duration_label'],
            'extras': quote['extras'],
            'is_internal': false,
            'user_id': 1,
            'created_at': '2026-01-01T08:00:00',
          },
          201,
        );
      }
      return http.Response('{"detail":"inattendu: $path"}', 404);
    });

    await http.runWithClient(() async {
      final api = ApiClient();
      final session = SessionProvider(api)
        ..user = AppUser(
          id: 1,
          email: 'cl@gmail.com',
          fullName: 'Client Test',
          phone: null,
          role: UserRole.client,
          createdAt: DateTime(2026),
        );
      await tester.pumpWidget(
        ChangeNotifierProvider<SessionProvider>.value(
          value: session,
          child: const MaterialApp(home: CalendarScreen(room: Room.gymnase)),
        ),
      );
      await tester.pumpAndSettle();

      // Prix initial : personnel extérieur, moins de 5 heures (9 h - 12 h).
      expect(find.text('Moins de 5 heures'), findsOneWidget);
      expect(find.text('750 000 FCFA'), findsWidgets);
      expect(find.text('1 250 000 FCFA'), findsOneWidget); // 750 000 + caution 500 000

      // Changement de catégorie.
      await tester.tap(find.text('Personnel extérieur').first);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Partenaire public').last);
      await tester.pumpAndSettle();
      expect(find.text('1 500 000 FCFA'), findsOneWidget); // 1 000 000 + caution

      // Prestations : 2 tables.
      await tester.tap(find.text('Prestations en plus (chaises, tables, sonorisation)'));
      await tester.pumpAndSettle();
      await tester.tap(find.byIcon(Icons.add_circle_outline));
      await tester.pumpAndSettle();
      await tester.tap(find.byIcon(Icons.add_circle_outline));
      await tester.pumpAndSettle();
      expect(find.text('Table simple × 2'), findsOneWidget);
      expect(find.text('1 504 000 FCFA'), findsOneWidget);

      await tester.tap(find.text('Réserver ce créneau'));
      await tester.pumpAndSettle();

      expect(posted, hasLength(1));
      expect(posted.single['client_category'], 'partenaire_public');
      expect(posted.single['extras'], [
        {'key': 'table_simple', 'quantity': 2},
      ]);
      // L'écran de paiement affiche le détail avec le montant à verser.
      expect(find.text('Paiement'), findsOneWidget);
      expect(find.text('1 504 000 FCFA'), findsOneWidget);
    }, () => client);
  });

  testWidgets('le personnel du Collège (admin) n\'a ni catégorie ni prix à choisir', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(360, 3200));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final client = MockClient((request) async {
      if (request.url.path == '/tariffs') return _json(_catalog);
      return http.Response('[]', 200);
    });
    await http.runWithClient(() async {
      final session = SessionProvider(ApiClient())
        ..user = AppUser(
          id: 2,
          email: 'ecoretraite@gmail.com',
          fullName: 'Admin',
          phone: null,
          role: UserRole.admin,
          createdAt: DateTime(2026),
        );
      await tester.pumpWidget(
        ChangeNotifierProvider<SessionProvider>.value(
          value: session,
          child: const MaterialApp(home: CalendarScreen(room: Room.gymnase)),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('Réservation interne du Collège'), findsOneWidget);
      expect(find.text('Votre catégorie'), findsNothing);
    }, () => client);
  });

  testWidgets('la liste des espaces propose le gymnase, la salle des fêtes et les autres espaces', (tester) async {
    await tester.binding.setSurfaceSize(const Size(360, 3200));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(const MaterialApp(home: RoomSelectionScreen()));
    await tester.pumpAndSettle();

    expect(find.text('Gymnase'), findsOneWidget);
    expect(find.text('Salle des fêtes'), findsOneWidget);
    expect(find.text('Autres espaces et activités'), findsOneWidget);
    for (final label in ['Salle de réunion', 'Tatami', 'Terrain multisport', 'Cours du Collège', 'Salle de classe']) {
      expect(find.text(label), findsOneWidget, reason: label);
    }
    // Les appartements, chambres et la cuisine ne sont pas proposés à la location.
    expect(find.textContaining('Appartement'), findsNothing);
    expect(find.textContaining('Chambre'), findsNothing);

    await tester.tap(find.text('Tatami'));
    await tester.pumpAndSettle();
    expect(find.text('Règlement intérieur'), findsWidgets);
  });
}
