import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../models/reservation.dart';
import '../models/tariff.dart';

String _dateStr(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

List<Map<String, dynamic>> _extrasJson(Map<String, int> extras) => [
      for (final e in extras.entries)
        if (e.value > 0) {'key': e.key, 'quantity': e.value},
    ];

class ReservationService {
  final ApiClient api;
  ReservationService(this.api);

  Future<Reservation> create({
    required Room room,
    required DateTime date,
    required TimeOfDay start,
    required TimeOfDay end,
    required bool acceptedRules,
    String clientCategory = 'personnel_exterieur',
    Map<String, int> extras = const {},
  }) async {
    final json = await api.post('/reservations', body: {
      'room': room.apiValue,
      'event_date': _dateStr(date),
      'start_time': '${formatTime(start)}:00',
      'end_time': '${formatTime(end)}:00',
      'accepted_rules': acceptedRules,
      'client_category': clientCategory,
      'extras': _extrasJson(extras),
    });
    return Reservation.fromJson(json as Map<String, dynamic>);
  }

  Future<TariffCatalog> catalog() async =>
      TariffCatalog.fromJson(await api.get('/tariffs') as Map<String, dynamic>);

  /// Prix détaillé calculé par le serveur (grille de l'économat) avant de réserver.
  Future<Quote> quote({
    required Room room,
    required TimeOfDay start,
    required TimeOfDay end,
    required String clientCategory,
    required Map<String, int> extras,
  }) async {
    final json = await api.post('/reservations/quote', body: {
      'room': room.apiValue,
      'start_time': '${formatTime(start)}:00',
      'end_time': '${formatTime(end)}:00',
      'client_category': clientCategory,
      'extras': _extrasJson(extras),
    });
    return Quote.fromJson(json as Map<String, dynamic>);
  }

  Future<List<Reservation>> list() async {
    final json = await api.get('/reservations') as List;
    return json.map((e) => Reservation.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Reservation> get(int id) async =>
      Reservation.fromJson(await api.get('/reservations/$id') as Map<String, dynamic>);

  Future<Reservation> validate(int id) async =>
      Reservation.fromJson(await api.post('/reservations/$id/validate') as Map<String, dynamic>);

  Future<Reservation> cancel(int id) async =>
      Reservation.fromJson(await api.post('/reservations/$id/cancel') as Map<String, dynamic>);

  Future<Reservation> pay(int id, {required String method, required String reference}) async {
    final json = await api.post('/reservations/$id/pay', body: {'method': method, 'reference': reference});
    return Reservation.fromJson(json as Map<String, dynamic>);
  }

  Future<List<AvailabilitySlot>> availability({Room? room}) async {
    final json = await api.get('/reservations/availability', query: {
      if (room != null) 'room': room.apiValue,
    }) as List;
    return json.map((e) => AvailabilitySlot.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<int>> receiptBytes(int id) => api.getBytes('/reservations/$id/receipt');
}
