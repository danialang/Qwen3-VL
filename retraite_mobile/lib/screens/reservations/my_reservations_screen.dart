import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../models/reservation.dart';
import '../../services/reservation_service.dart';
import '../../widgets/status_badge.dart';
import 'reservation_detail_screen.dart';

class MyReservationsScreen extends StatefulWidget {
  const MyReservationsScreen({super.key});

  @override
  State<MyReservationsScreen> createState() => _MyReservationsScreenState();
}

class _MyReservationsScreenState extends State<MyReservationsScreen> {
  late final ReservationService _service;
  List<Reservation> _reservations = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _service = ReservationService(context.read<SessionProvider>().api);
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await _service.list();
      setState(() => _reservations = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Impossible de charger vos réservations.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mes réservations')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? ListView(children: [Padding(padding: const EdgeInsets.all(24), child: Text(_error!))])
                : _reservations.isEmpty
                    ? ListView(
                        children: const [
                          Padding(
                            padding: EdgeInsets.all(24),
                            child: Text('Aucune réservation pour le moment.'),
                          ),
                        ],
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: _reservations.length,
                        itemBuilder: (context, index) {
                          final r = _reservations[index];
                          return Card(
                            child: ListTile(
                              title: Text('${r.room.label} — ${r.eventDate.day}/${r.eventDate.month}/${r.eventDate.year}'),
                              subtitle: Text('${formatTime(r.startTime)} - ${formatTime(r.endTime)}'),
                              trailing: StatusBadge(status: r.status),
                              onTap: () async {
                                await Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => ReservationDetailScreen(reservation: r)),
                                );
                                _load();
                              },
                            ),
                          );
                        },
                      ),
      ),
    );
  }
}
