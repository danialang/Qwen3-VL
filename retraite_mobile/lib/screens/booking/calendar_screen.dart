import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:table_calendar/table_calendar.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../../services/reservation_service.dart';
import 'payment_screen.dart';

class CalendarScreen extends StatefulWidget {
  final Room room;
  const CalendarScreen({super.key, required this.room});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  late final ReservationService _service;
  List<AvailabilitySlot> _slots = [];
  bool _loading = true;
  String? _loadError;

  DateTime _focusedDay = DateTime.now();
  DateTime _selectedDay = DateTime.now();
  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime = const TimeOfDay(hour: 12, minute: 0);
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _service = ReservationService(context.read<SessionProvider>().api);
    _loadAvailability();
  }

  Future<void> _loadAvailability() async {
    setState(() {
      _loading = true;
      _loadError = null;
    });
    try {
      final slots = await _service.availability(room: widget.room);
      setState(() => _slots = slots);
    } on ApiException catch (e) {
      setState(() => _loadError = e.message);
    } catch (_) {
      setState(() => _loadError = 'Impossible de charger le calendrier.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<AvailabilitySlot> _slotsForDay(DateTime day) =>
      _slots.where((s) => isSameDay(s.eventDate, day)).toList();

  Future<void> _pickTime({required bool isStart}) async {
    final picked = await showTimePicker(context: context, initialTime: isStart ? _startTime : _endTime);
    if (picked == null) return;
    setState(() {
      if (isStart) {
        _startTime = picked;
      } else {
        _endTime = picked;
      }
    });
  }

  Future<void> _submit() async {
    final startMinutes = _startTime.hour * 60 + _startTime.minute;
    final endMinutes = _endTime.hour * 60 + _endTime.minute;
    if (endMinutes <= startMinutes) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("L'heure de fin doit être après l'heure de début.")),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      final reservation = await _service.create(
        room: widget.room,
        date: _selectedDay,
        start: _startTime,
        end: _endTime,
        acceptedRules: true,
      );
      if (!mounted) return;
      if (reservation.isInternal) {
        await showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Réservation interne créée'),
            content: const Text('Réservation gratuite pour le Collège, validée automatiquement.'),
            actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
          ),
        );
        if (!mounted) return;
        Navigator.of(context).popUntil((route) => route.isFirst);
      } else {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => PaymentScreen(reservation: reservation)),
        );
      }
    } on ApiException catch (e) {
      if (!mounted) return;
      await showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Créneau indisponible'),
          content: Text(e.message),
          actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
        ),
      );
      _loadAvailability();
    } catch (_) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Erreur réseau, réessayez.')),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final daySlots = _slotsForDay(_selectedDay);

    return Scaffold(
      appBar: AppBar(title: Text('Calendrier - ${widget.room.label}')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(12),
              children: [
                if (_loadError != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(_loadError!, style: const TextStyle(color: Colors.red)),
                  ),
                TableCalendar<AvailabilitySlot>(
                  firstDay: DateTime.now().subtract(const Duration(days: 1)),
                  lastDay: DateTime.now().add(const Duration(days: 365)),
                  focusedDay: _focusedDay,
                  selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                  eventLoader: _slotsForDay,
                  onDaySelected: (selected, focused) {
                    setState(() {
                      _selectedDay = selected;
                      _focusedDay = focused;
                    });
                  },
                  calendarStyle: const CalendarStyle(
                    selectedDecoration: BoxDecoration(color: CollegeColors.green, shape: BoxShape.circle),
                    todayDecoration: BoxDecoration(color: CollegeColors.greenLight, shape: BoxShape.circle),
                    todayTextStyle: TextStyle(color: CollegeColors.greenDark),
                  ),
                  calendarBuilders: CalendarBuilders(
                    markerBuilder: (context, day, slots) {
                      if (slots.isEmpty) return null;
                      final hasInternal = slots.any((s) => s.isInternal);
                      return Positioned(
                        bottom: 1,
                        child: Container(
                          width: 7,
                          height: 7,
                          decoration: BoxDecoration(
                            color: hasInternal ? CollegeColors.gold : CollegeColors.statusPending,
                            shape: BoxShape.circle,
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 16),
                Text('Créneaux déjà pris ce jour-là', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 8),
                if (daySlots.isEmpty)
                  const Text('Aucun créneau réservé pour cette date.')
                else
                  ...daySlots.map(
                    (s) => Card(
                      child: ListTile(
                        leading: Icon(
                          s.isInternal ? Icons.school : Icons.person,
                          color: s.isInternal ? CollegeColors.gold : s.status.color,
                        ),
                        title: Text('${formatTime(s.startTime)} - ${formatTime(s.endTime)}'),
                        subtitle: Text(s.isInternal ? 'Événement du Collège' : s.status.label),
                      ),
                    ),
                  ),
                const SizedBox(height: 16),
                Text('Choisir un créneau', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => _pickTime(isStart: true),
                        child: Text('Début : ${formatTime(_startTime)}'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => _pickTime(isStart: false),
                        child: Text('Fin : ${formatTime(_endTime)}'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _submitting ? null : _submit,
                  child: _submitting
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Text('Réserver ce créneau'),
                ),
              ],
            ),
    );
  }
}
