import 'package:flutter/material.dart';

import 'tariff.dart';

enum Room {
  gymnase,
  salleFetes,
  salleReunionRepas,
  salleReunion,
  coursExterneGymnase,
  salleFeteCollege,
  salleReunionCollege,
  salleClasse,
  terrainMultisport,
  tatami,
  coursCollege,
}

extension RoomApi on Room {
  String get apiValue {
    switch (this) {
      case Room.gymnase:
        return 'gymnase';
      case Room.salleFetes:
        return 'salle_fetes';
      case Room.salleReunionRepas:
        return 'salle_reunion_repas';
      case Room.salleReunion:
        return 'salle_reunion';
      case Room.coursExterneGymnase:
        return 'cours_externe_gymnase';
      case Room.salleFeteCollege:
        return 'salle_fete_college';
      case Room.salleReunionCollege:
        return 'salle_reunion_college';
      case Room.salleClasse:
        return 'salle_classe';
      case Room.terrainMultisport:
        return 'terrain_multisport';
      case Room.tatami:
        return 'tatami';
      case Room.coursCollege:
        return 'cours_college';
    }
  }

  String get label {
    switch (this) {
      case Room.gymnase:
        return 'Gymnase';
      case Room.salleFetes:
        return 'Salle des fêtes';
      case Room.salleReunionRepas:
        return 'Salle de réunion avec repas';
      case Room.salleReunion:
        return 'Salle de réunion';
      case Room.coursExterneGymnase:
        return 'Cours externes au gymnase';
      case Room.salleFeteCollege:
        return 'Salle de fête du Collège';
      case Room.salleReunionCollege:
        return 'Salle de réunion du Collège';
      case Room.salleClasse:
        return 'Salle de classe';
      case Room.terrainMultisport:
        return 'Terrain multisport';
      case Room.tatami:
        return 'Tatami';
      case Room.coursCollege:
        return 'Cours du Collège';
    }
  }

  /// Précision affichée sous le nom dans la liste des autres espaces.
  String get description {
    switch (this) {
      case Room.salleReunionRepas:
        return '400 chaises, tables et repas dans la salle';
      case Room.salleReunion:
        return '400 chaises et tables';
      case Room.coursExterneGymnase:
        return 'Cours donnés dans le gymnase par un organisme extérieur';
      case Room.salleFeteCollege:
        return 'Petite salle de fête du Collège';
      case Room.salleReunionCollege:
        return 'Réunions de petite taille';
      case Room.salleClasse:
        return 'Une salle de classe du Collège';
      case Room.terrainMultisport:
        return 'Terrain de sport en plein air';
      case Room.tatami:
        return 'Espace d\'arts martiaux';
      case Room.coursCollege:
        return 'Locaux du Collège pour des cours';
      case Room.gymnase:
      case Room.salleFetes:
        return '';
    }
  }

  IconData get icon {
    switch (this) {
      case Room.gymnase:
      case Room.coursExterneGymnase:
        return Icons.sports_basketball;
      case Room.salleFetes:
      case Room.salleFeteCollege:
        return Icons.celebration;
      case Room.salleReunionRepas:
      case Room.salleReunion:
      case Room.salleReunionCollege:
        return Icons.groups;
      case Room.salleClasse:
      case Room.coursCollege:
        return Icons.school;
      case Room.terrainMultisport:
        return Icons.sports_soccer;
      case Room.tatami:
        return Icons.sports_martial_arts;
    }
  }

  String get imageAsset => this == Room.gymnase ? 'assets/images/gymnase.jpg' : 'assets/images/salle_fetes.jpg';

  static Room fromApi(String value) => Room.values.firstWhere(
        (r) => r.apiValue == value,
        orElse: () => Room.salleFetes,
      );
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
  final double deposit;
  final String? clientCategoryLabel;
  final String? durationLabel;
  final List<QuoteLine> extras;
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
    this.deposit = 0,
    this.clientCategoryLabel,
    this.durationLabel,
    this.extras = const [],
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
        deposit: double.tryParse(json['deposit']?.toString() ?? '') ?? 0,
        clientCategoryLabel: json['client_category_label'] as String?,
        durationLabel: json['duration_label'] as String?,
        extras: ((json['extras'] as List?) ?? const [])
            .map((e) => QuoteLine.fromJson(e as Map<String, dynamic>))
            .toList(),
        isInternal: json['is_internal'] as bool,
        userId: json['user_id'] as int,
        securityCode: json['security_code'] as String?,
        paymentMethod: json['payment_method'] as String?,
        paymentReference: json['payment_reference'] as String?,
        hasReceipt: json['has_receipt'] as bool? ?? false,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  bool get isPaid => paymentReference != null;

  /// Ce que le client verse : location + prestations + caution remboursable.
  double get totalDue => amount + deposit;
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
