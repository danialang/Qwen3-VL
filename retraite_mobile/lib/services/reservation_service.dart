import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../models/reservation.dart';

String _dateStr(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

class ReservationService {
  final ApiClient api;
  ReservationService(this.api);

  Future<Reservation> create({
    required Room room,
    required DateTime date,
    required TimeOfDay start,
    required TimeOfDay end,
    required bool acceptedRules,
  }) async {
    final json = await api.post('/reservations', body: {
      'room': room.apiValue,
      'event_date': _dateStr(date),
      'start_time': '${formatTime(start)}:00',
      'end_time': '${formatTime(end)}:00',
      'accepted_rules': acceptedRules,
    });
    return Reservation.fromJson(json as Map<String, dynamic>);
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
