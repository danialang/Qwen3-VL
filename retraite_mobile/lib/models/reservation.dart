import 'package:flutter/material.dart';

enum Room { gymnase, salleFetes }

extension RoomApi on Room {
  String get apiValue => this == Room.gymnase ? 'gymnase' : 'salle_fetes';

  String get label => this == Room.gymnase ? 'Gymnase' : 'Salle des fêtes';

  static Room fromApi(String value) => value == 'gymnase' ? Room.gymnase : Room.salleFetes;
}

enum ReservationStatus { pending, validated, cancelled }

extension ReservationStatusX on ReservationStatus {
  static ReservationStatus fromApi(String value) => ReservationStatus.values.firstWhere(
        (s) => s.name == value,
        orElse: () => ReservationStatus.pending,
      );

  String get label {
    switch (this) {
      case ReservationStatus.validated:
        return 'Validée';
      case ReservationStatus.pending:
        return 'En attente';
      case ReservationStatus.cancelled:
        return 'Annulée';
    }
  }

  Color get color {
    switch (this) {
      case ReservationStatus.validated:
        return const Color(0xFF2E7D32);
      case ReservationStatus.pending:
        return const Color(0xFFF9A825);
      case ReservationStatus.cancelled:
        return const Color(0xFFC62828);
    }
  }
}

TimeOfDay _parseTime(String value) {
  final parts = value.split(':');
  return TimeOfDay(hour: int.parse(parts[0]), minute: int.parse(parts[1]));
}

String formatTime(TimeOfDay t) => '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';

class Reservation {
  final int id;
  final Room room;
  final DateTime eventDate;
  final TimeOfDay startTime;
  final TimeOfDay endTime;
  final ReservationStatus status;
  final double amount;
  final bool isInternal;
  final int userId;
  final String? securityCode;
  final String? paymentMethod;
  final String? paymentReference;
  final bool hasReceipt;
  final DateTime createdAt;

  Reservation({
    required this.id,
    required this.room,
    required this.eventDate,
    required this.startTime,
    required this.endTime,
    required this.status,
    required this.amount,
    required this.isInternal,
    required this.userId,
    required this.securityCode,
    required this.paymentMethod,
    required this.paymentReference,
    required this.hasReceipt,
    required this.createdAt,
  });

  factory Reservation.fromJson(Map<String, dynamic> json) => Reservation(
        id: json['id'] as int,
        room: RoomApi.fromApi(json['room'] as String),
        eventDate: DateTime.parse(json['event_date'] as String),
        startTime: _parseTime(json['start_time'] as String),
        endTime: _parseTime(json['end_time'] as String),
        status: ReservationStatusX.fromApi(json['status'] as String),
        amount: double.parse(json['amount'].toString()),
        isInternal: json['is_internal'] as bool,
        userId: json['user_id'] as int,
        securityCode: json['security_code'] as String?,
        paymentMethod: json['payment_method'] as String?,
        paymentReference: json['payment_reference'] as String?,
        hasReceipt: json['has_receipt'] as bool? ?? false,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  bool get isPaid => paymentReference != null;
}

/// Créneau occupé, anonymisé (utilisé pour le calendrier client).
class AvailabilitySlot {
  final Room room;
  final DateTime eventDate;
  final TimeOfDay startTime;
  final TimeOfDay endTime;
  final bool isInternal;
  final ReservationStatus status;

  AvailabilitySlot({
    required this.room,
    required this.eventDate,
    required this.startTime,
    required this.endTime,
    required this.isInternal,
    required this.status,
  });

  factory AvailabilitySlot.fromJson(Map<String, dynamic> json) => AvailabilitySlot(
        room: RoomApi.fromApi(json['room'] as String),
        eventDate: DateTime.parse(json['event_date'] as String),
        startTime: _parseTime(json['start_time'] as String),
        endTime: _parseTime(json['end_time'] as String),
        isInternal: json['is_internal'] as bool,
        status: ReservationStatusX.fromApi(json['status'] as String),
      );
}
