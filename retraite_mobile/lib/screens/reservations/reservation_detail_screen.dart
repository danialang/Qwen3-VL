import 'dart:io';

import 'package:flutter/material.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../../models/user.dart';
import '../../services/reservation_service.dart';
import '../../widgets/price_breakdown.dart';
import '../../widgets/status_badge.dart';

class ReservationDetailScreen extends StatefulWidget {
  final Reservation reservation;
  const ReservationDetailScreen({super.key, required this.reservation});

  @override
  State<ReservationDetailScreen> createState() => _ReservationDetailScreenState();
}

class _ReservationDetailScreenState extends State<ReservationDetailScreen> {
  late Reservation _reservation;
  late final ReservationService _service;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _reservation = widget.reservation;
    _service = ReservationService(context.read<SessionProvider>().api);
  }

  Future<void> _run(Future<void> Function() action) async {
    setState(() => _busy = true);
    try {
      await action();
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur réseau, réessayez.')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _validate() async {
    String? reference;
    if (!_reservation.isInternal && !_reservation.isPaid) {
      final controller = TextEditingController();
      reference = await showDialog<String>(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Paiement reçu ?'),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('Confirmez que le client a payé ${_reservation.totalDue.toStringAsFixed(0)} FCFA.'),
            TextField(
              controller: controller,
              decoration: const InputDecoration(labelText: 'N° du reçu de caisse (facultatif)'),
            ),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Annuler')),
            ElevatedButton(onPressed: () => Navigator.of(context).pop(controller.text.trim()), child: const Text('Paiement reçu')),
          ],
        ),
      );
      if (reference == null) return;
    }
    await _run(() async {
      final updated = await _service.validate(_reservation.id, reference: reference);
      setState(() => _reservation = updated);
    });
  }

  Future<void> _cancel() => _run(() async {
        final updated = await _service.cancel(_reservation.id);
        setState(() => _reservation = updated);
      });

  Future<void> _downloadReceipt() => _run(() async {
        final bytes = await _service.receiptBytes(_reservation.id);
        final dir = await getApplicationDocumentsDirectory();
        final file = File('${dir.path}/recu_${_reservation.id}.pdf');
        await file.writeAsBytes(bytes);
        await OpenFilex.open(file.path);
      });

  String _paymentText(Reservation r) {
    final details = [
      if (r.paymentMethodLabel != null) r.paymentMethodLabel!,
      if (r.isPaid && r.paymentReference != null) 'réf. ${r.paymentReference}',
    ].join(', ');
    final state = r.isPaid ? 'Reçu' : 'En attente';
    return details.isEmpty ? state : '$state ($details)';
  }

  @override
  Widget build(BuildContext context) {
    final r = _reservation;
    final user = context.watch<SessionProvider>().user;
    final isAdmin = user?.role == UserRole.admin || user?.role == UserRole.dev;
    final canValidate = isAdmin && !r.isInternal && r.status == ReservationStatus.pending;
    final canCancel = r.status != ReservationStatus.cancelled;

    return Scaffold(
      appBar: AppBar(title: const Text('Détail de la réservation')),
      body: AbsorbPointer(
        absorbing: _busy,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(r.room.label, style: Theme.of(context).textTheme.titleLarge),
                StatusBadge(status: r.status),
              ],
            ),
            if (r.isInternal) ...[
              const SizedBox(height: 4),
              const Chip(
                avatar: Icon(Icons.school, size: 18, color: Colors.white),
                label: Text('Réservation interne — Collège (gratuite)'),
                backgroundColor: CollegeColors.gold,
                labelStyle: TextStyle(color: Colors.white),
              ),
            ],
            const SizedBox(height: 16),
            _InfoRow(label: 'Date', value: '${r.eventDate.day}/${r.eventDate.month}/${r.eventDate.year}'),
            _InfoRow(label: 'Horaire', value: '${formatTime(r.startTime)} - ${formatTime(r.endTime)}'),
            if (r.isInternal)
              const _InfoRow(label: 'Montant', value: 'Gratuit')
            else ...[
              const SizedBox(height: 4),
              Card(
                color: CollegeColors.greenLight,
                margin: EdgeInsets.zero,
                child: Padding(padding: const EdgeInsets.all(14), child: PriceBreakdown.fromReservation(r)),
              ),
              const SizedBox(height: 8),
            ],
            _InfoRow(label: 'Code de sécurité', value: r.securityCode ?? '—'),
            if (!r.isInternal)
              _InfoRow(label: 'Paiement', value: _paymentText(r)),
            const SizedBox(height: 24),
            if (r.hasReceipt)
              ElevatedButton.icon(
                onPressed: _downloadReceipt,
                icon: const Icon(Icons.picture_as_pdf),
                label: const Text('Télécharger le reçu PDF'),
              ),
            if (canValidate) ...[
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _validate,
                icon: const Icon(Icons.check_circle),
                label: const Text('Valider la réservation'),
              ),
            ],
            if (canCancel) ...[
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: _cancel,
                icon: const Icon(Icons.cancel, color: Colors.red),
                label: const Text('Annuler', style: TextStyle(color: Colors.red)),
              ),
            ],
            if (_busy) const Padding(
              padding: EdgeInsets.only(top: 20),
              child: Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          SizedBox(width: 140, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w600))),
        ],
      ),
    );
  }
}
