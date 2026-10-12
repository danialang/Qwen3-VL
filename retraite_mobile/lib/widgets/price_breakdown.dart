import 'package:flutter/material.dart';

import '../core/format.dart';
import '../core/theme.dart';
import '../models/reservation.dart';
import '../models/tariff.dart';

/// Détail d'un prix : location, prestations, total, caution remboursable et montant à verser.
class PriceBreakdown extends StatelessWidget {
  final String? categoryLabel;
  final String? durationLabel;
  final int rental;
  final List<QuoteLine> extras;
  final int total;
  final int deposit;
  final int totalDue;

  const PriceBreakdown({
    super.key,
    required this.categoryLabel,
    required this.durationLabel,
    required this.rental,
    required this.extras,
    required this.total,
    required this.deposit,
    required this.totalDue,
  });

  factory PriceBreakdown.fromQuote(Quote q) => PriceBreakdown(
        categoryLabel: q.categoryLabel,
        durationLabel: q.durationLabel,
        rental: q.rental,
        extras: q.extras,
        total: q.total,
        deposit: q.deposit,
        totalDue: q.totalDue,
      );

  factory PriceBreakdown.fromReservation(Reservation r) {
    final extrasTotal = r.extras.fold<int>(0, (sum, e) => sum + e.total);
    return PriceBreakdown(
      categoryLabel: r.clientCategoryLabel,
      durationLabel: r.durationLabel,
      rental: r.amount.round() - extrasTotal,
      extras: r.extras,
      total: r.amount.round(),
      deposit: r.deposit.round(),
      totalDue: r.totalDue.round(),
    );
  }

  Widget _row(String label, String value, {bool bold = false, Color? color}) {
    final style = TextStyle(fontWeight: bold ? FontWeight.bold : FontWeight.normal, color: color);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: Text(label, style: style)),
          const SizedBox(width: 12),
          Text(value, style: style),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (categoryLabel != null) _row('Catégorie', categoryLabel!),
        if (durationLabel != null) _row('Durée', durationLabel!),
        _row('Location', formatFcfa(rental.toDouble())),
        for (final e in extras) _row('${e.label} × ${e.quantity}', formatFcfa(e.total.toDouble())),
        const Divider(height: 16),
        _row('Total location', formatFcfa(total.toDouble()), bold: true),
        _row('Caution remboursable', formatFcfa(deposit.toDouble())),
        const Divider(height: 16),
        _row('À verser', formatFcfa(totalDue.toDouble()), bold: true, color: CollegeColors.green),
      ],
    );
  }
}
