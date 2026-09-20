import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../booking/rules_screen.dart';

class RoomSelectionScreen extends StatelessWidget {
  const RoomSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Choisir une salle')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          _RoomCard(room: Room.gymnase, equipments: kEquipmentsGymnase, icon: Icons.sports_basketball),
          SizedBox(height: 16),
          _RoomCard(room: Room.salleFetes, equipments: kEquipmentsSalleDesFetes, icon: Icons.celebration),
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
      child: ExpansionTile(
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
    );
  }
}
