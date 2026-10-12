import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../booking/rules_screen.dart';

const List<Room> _otherRooms = [
  Room.salleReunionRepas,
  Room.salleReunion,
  Room.coursExterneGymnase,
  Room.salleFeteCollege,
  Room.salleReunionCollege,
  Room.salleClasse,
  Room.terrainMultisport,
  Room.tatami,
  Room.coursCollege,
];

class RoomSelectionScreen extends StatelessWidget {
  const RoomSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Choisir une salle')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const _RoomCard(room: Room.gymnase, equipments: kEquipmentsGymnase, icon: Icons.sports_basketball),
          const SizedBox(height: 16),
          const _RoomCard(room: Room.salleFetes, equipments: kEquipmentsSalleDesFetes, icon: Icons.celebration),
          const SizedBox(height: 24),
          Text('Autres espaces et activités', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          const Text('Le prix est calculé selon votre catégorie et la durée choisie.'),
          const SizedBox(height: 8),
          Card(
            margin: EdgeInsets.zero,
            child: Column(
              children: [
                for (final room in _otherRooms)
                  ListTile(
                    leading: CircleAvatar(
                      backgroundColor: CollegeColors.greenLight,
                      child: Icon(room.icon, color: CollegeColors.green),
                    ),
                    title: Text(room.label),
                    subtitle: Text(room.description),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => RulesScreen(room: room)),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _RoomCard extends StatelessWidget {
  final Room room;
  final List<String> equipments;
  final IconData icon;

  const _RoomCard({required this.room, required this.equipments, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      margin: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AspectRatio(
            aspectRatio: 16 / 9,
            child: Image.asset(
              room.imageAsset,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [CollegeColors.green, CollegeColors.greenDark],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                alignment: Alignment.center,
                child: Icon(icon, color: Colors.white, size: 48),
              ),
            ),
          ),
          ExpansionTile(
            shape: const RoundedRectangleBorder(side: BorderSide.none),
            collapsedShape: const RoundedRectangleBorder(side: BorderSide.none),
            leading: CircleAvatar(backgroundColor: CollegeColors.greenLight, child: Icon(icon, color: CollegeColors.green)),
            title: Text(room.label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            subtitle: const Text('Voir le matériel disponible'),
            childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            children: [
              ...equipments.map(
                (e) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, size: 18, color: CollegeColors.green),
                      const SizedBox(width: 8),
                      Expanded(child: Text(e)),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('Réserver cette salle'),
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => RulesScreen(room: room)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
