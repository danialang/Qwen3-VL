import 'package:flutter/material.dart';

import '../../core/format.dart';
import '../../core/theme.dart';
import '../../services/admin_stats_service.dart';

const _monthNames = [
  'Janvier',
  'Février',
  'Mars',
  'Avril',
  'Mai',
  'Juin',
  'Juillet',
  'Août',
  'Septembre',
  'Octobre',
  'Novembre',
  'Décembre',
];

class AdminYearReportScreen extends StatelessWidget {
  final AdminOverview overview;

  const AdminYearReportScreen({super.key, required this.overview});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Revenus ${overview.year}')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: CollegeColors.green,
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Total de l\'année', style: TextStyle(color: Colors.white70)),
                  const SizedBox(height: 6),
                  Text(
                    formatFcfa(overview.revenueYearFcfa),
                    style: const TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text('Mois par mois', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                for (int i = 0; i < 12; i++)
                  ListTile(
                    dense: true,
                    selected: i + 1 == overview.month,
                    title: Text(_monthNames[i]),
                    trailing: Text(
                      formatFcfa(i < overview.revenueByMonth.length ? overview.revenueByMonth[i] : 0),
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Seules les réservations validées par l\'administration sont comptées. '
            'Les réservations internes (gratuites) ne rapportent rien.',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
