import 'package:flutter/material.dart';

import '../../core/theme.dart';
import '../assistant/chat_screen.dart';
import 'admin_reservations_screen.dart';
import 'admin_users_screen.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tableau de bord admin')),
      body: GridView.count(
        padding: const EdgeInsets.all(16),
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
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminReservationsScreen())),
          ),
          _DashboardTile(
            icon: Icons.receipt_long,
            label: 'Reçus\n(via une réservation validée)',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminReservationsScreen())),
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
