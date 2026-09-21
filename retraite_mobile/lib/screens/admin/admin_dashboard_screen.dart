import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../services/admin_stats_service.dart';
import '../assistant/chat_screen.dart';
import 'admin_reservations_screen.dart';
import 'admin_users_screen.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  late final AdminStatsService _statsService;
  AdminOverview? _overview;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _statsService = AdminStatsService(context.read<SessionProvider>().api);
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final overview = await _statsService.getOverview();
      setState(() => _overview = overview);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Impossible de charger les statistiques.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatFcfa(double amount) {
    final s = amount.toStringAsFixed(0);
    final buffer = StringBuffer();
    for (int i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) buffer.write(' ');
      buffer.write(s[i]);
    }
    return '$buffer FCFA';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tableau de bord admin'),
        actions: [IconButton(onPressed: _load, icon: const Icon(Icons.refresh))],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('Ce mois-ci', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 12),
            if (_loading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              )
            else if (_overview != null)
              _StatsGrid(overview: _overview!, formatFcfa: _formatFcfa),
            const SizedBox(height: 24),
            Text('Gestion', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 12),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.1,
              children: [
                _DashboardTile(
                  icon: Icons.people,
                  label: 'Comptes inscrits',
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminUsersScreen())),
                ),
                _DashboardTile(
                  icon: Icons.event_note,
                  label: 'Réservations\n& validations',
                  onTap: () =>
                      Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminReservationsScreen())),
                ),
                _DashboardTile(
                  icon: Icons.receipt_long,
                  label: 'Reçus\n(via une réservation validée)',
                  onTap: () =>
                      Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminReservationsScreen())),
                ),
                _DashboardTile(
                  icon: Icons.smart_toy,
                  label: 'Assistant IA\nadmin',
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const ChatScreen(
                        title: 'Assistant admin',
                        path: '/assistant/admin',
                        welcomeMessage:
                            'Posez une question sur les réservations (ex. "combien ce mois-ci ?"), '
                            'demandez le bilan annuel, ou consultez les derniers logs applicatifs.',
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatsGrid extends StatelessWidget {
  final AdminOverview overview;
  final String Function(double) formatFcfa;

  const _StatsGrid({required this.overview, required this.formatFcfa});

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.4,
      children: [
        _StatCard(
          icon: Icons.hourglass_top,
          label: 'Réservations en attente',
          value: '${overview.pendingReservationsCount}',
          color: CollegeColors.statusPending,
        ),
        _StatCard(
          icon: Icons.payments,
          label: 'Revenus du mois',
          value: formatFcfa(overview.revenueThisMonthFcfa),
          color: CollegeColors.green,
        ),
        _StatCard(
          icon: Icons.sports_basketball,
          label: 'Occupation Gymnase',
          value: '${overview.occupancyRateThisMonthPercent['gymnase']?.toStringAsFixed(0) ?? '0'} %',
          color: CollegeColors.greenDark,
        ),
        _StatCard(
          icon: Icons.celebration,
          label: 'Occupation Salle des fêtes',
          value: '${overview.occupancyRateThisMonthPercent['salle_fetes']?.toStringAsFixed(0) ?? '0'} %',
          color: CollegeColors.gold,
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({required this.icon, required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: color, size: 22),
            Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              label,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _DashboardTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _DashboardTile({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 36, color: CollegeColors.green),
              const SizedBox(height: 10),
              Text(label, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}
