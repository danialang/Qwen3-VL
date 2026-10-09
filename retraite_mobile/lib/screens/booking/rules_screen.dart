import 'package:flutter/material.dart';

import '../../core/constants.dart';
import '../../models/reservation.dart';
import 'calendar_screen.dart';

class RulesScreen extends StatefulWidget {
  final Room room;
  const RulesScreen({super.key, required this.room});

  @override
  State<RulesScreen> createState() => _RulesScreenState();
}

class _RulesScreenState extends State<RulesScreen> {
  bool _accepted = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Règlement intérieur')),
      body: Column(
        children: [
          const Expanded(
            child: SingleChildScrollView(
              padding: EdgeInsets.all(20),
              child: Text(kReglementInterieur, style: TextStyle(height: 1.4)),
            ),
          ),
          SafeArea(
            top: false,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border(top: BorderSide(color: Theme.of(context).dividerColor)),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CheckboxListTile(
                    value: _accepted,
                    onChanged: (v) => setState(() => _accepted = v ?? false),
                    controlAffinity: ListTileControlAffinity.leading,
                    contentPadding: EdgeInsets.zero,
                    title: const Text("J'ai lu et j'accepte le règlement intérieur."),
                  ),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _accepted
                          ? () => Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => CalendarScreen(room: widget.room)),
                              )
                          : null,
                      child: const Text('Continuer vers le calendrier'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
