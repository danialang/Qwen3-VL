import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../../services/reservation_service.dart';
import '../../widgets/status_badge.dart';
import '../reservations/reservation_detail_screen.dart';

class AdminReservationsScreen extends StatefulWidget {
  const AdminReservationsScreen({super.key});

  @override
  State<AdminReservationsScreen> createState() => _AdminReservationsScreenState();
}

class _AdminReservationsScreenState extends State<AdminReservationsScreen> with SingleTickerProviderStateMixin {
  late final ReservationService _service;
  late final TabController _tabController;
  List<Reservation> _reservations = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _service = ReservationService(context.read<SessionProvider>().api);
    _load();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await _service.list();
      list.sort((a, b) => b.eventDate.compareTo(a.eventDate));
      setState(() => _reservations = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Impossible de charger les réservations.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<Reservation> get _pendingExternal =>
      _reservations.where((r) => !r.isInternal && r.status == ReservationStatus.pending).toList();

  Widget _buildList(List<Reservation> items) {
    if (items.isEmpty) {
      return const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('Aucune réservation.')));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final r = items[index];
        return Card(
          child: ListTile(
            leading: r.isInternal ? const Icon(Icons.school, color: CollegeColors.gold) : const Icon(Icons.person),
            title: Text('${r.room.label} — ${r.eventDate.day}/${r.eventDate.month}/${r.eventDate.year}'),
            subtitle: Text(
              '${formatTime(r.startTime)} - ${formatTime(r.endTime)}'
              '${r.isInternal ? ' • Collège (gratuit)' : ' • ${r.amount.toStringAsFixed(0)} FCFA'}',
            ),
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
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Réservations'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'À valider (${_pendingExternal.length})'),
            const Tab(text: 'Toutes'),
          ],
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(_error!)))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildList(_pendingExternal),
                      _buildList(_reservations),
                    ],
                  ),
                ),
    );
  }
}
