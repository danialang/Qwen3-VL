import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/session.dart';
import '../../core/theme_provider.dart';
import '../../widgets/college_logo.dart';
import '../admin/admin_dashboard_screen.dart';
import '../assistant/chat_screen.dart';
import '../auth/login_screen.dart';
import '../reservations/my_reservations_screen.dart';
import '../rooms/room_selection_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final session = context.watch<SessionProvider>();
    final themeProvider = context.watch<ThemeModeProvider>();
    final user = session.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Accueil'),
        actions: [
          IconButton(
            tooltip: 'Mode sombre',
            icon: Icon(themeProvider.mode == ThemeMode.dark ? Icons.dark_mode : Icons.light_mode),
            onPressed: () => themeProvider.toggle(),
          ),
          IconButton(
            tooltip: 'Déconnexion',
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await session.logout();
              if (!context.mounted) return;
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const CollegeHeroBanner(),
          const SizedBox(height: 20),
          Text(
            'Bienvenue${user != null ? ', ${user.fullName}' : ''} !',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 4),
          const Text('Réservez le gymnase ou la salle des fêtes du Collège.'),
          const SizedBox(height: 24),
          _ActionCard(
            icon: Icons.event_available,
            title: 'Réserver une salle',
            subtitle: 'Gymnase ou salle des fêtes',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RoomSelectionScreen())),
          ),
          const SizedBox(height: 12),
          _ActionCard(
            icon: Icons.list_alt,
            title: 'Mes réservations',
            subtitle: 'Historique et statuts',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const MyReservationsScreen())),
          ),
          const SizedBox(height: 12),
          _ActionCard(
            icon: Icons.smart_toy,
            title: 'Assistant IA',
            subtitle: 'Réservez en langage naturel',
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => const ChatScreen(
                  title: 'Assistant de réservation',
                  path: '/assistant/client',
                  welcomeMessage:
                      'Bonjour ! Dites-moi quelle salle, quelle date et quel horaire vous souhaitez, '
                      "et je m'occupe de vérifier la disponibilité et créer votre réservation.",
                ),
              ),
            ),
          ),
          if (user?.isAdminOrDev == true) ...[
            const SizedBox(height: 12),
            _ActionCard(
              icon: Icons.admin_panel_settings,
              title: 'Tableau de bord admin',
              subtitle: 'Comptes, reçus, validations',
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AdminDashboardScreen())),
            ),
          ],
        ],
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ActionCard({required this.icon, required this.title, required this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primaryContainer,
          child: Icon(icon, color: Theme.of(context).colorScheme.primary),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
