import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../../services/payment_service.dart';
import '../../widgets/price_breakdown.dart';
import '../reservations/reservation_detail_screen.dart';

class PaymentScreen extends StatefulWidget {
  final Reservation reservation;
  const PaymentScreen({super.key, required this.reservation});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  late final PaymentService _paymentService;
  late Future<PaymentOptions> _options;
  bool _processing = false;

  @override
  void initState() {
    super.initState();
    _paymentService = PaymentService(context.read<SessionProvider>().api);
    _options = _paymentService.options();
  }

  Future<String?> _askPhone(String label) {
    final controller = TextEditingController();
    return showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(label),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(labelText: 'Numéro de téléphone'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Annuler')),
          ElevatedButton(onPressed: () => Navigator.of(context).pop(controller.text.trim()), child: const Text('Payer')),
        ],
      ),
    );
  }

  Future<void> _choose(PaymentMethodOption method) async {
    String? phone;
    if (method.online) {
      phone = await _askPhone(method.label);
      if (phone == null || phone.isEmpty) return;
    }
    setState(() => _processing = true);
    try {
      final start = await _paymentService.choose(widget.reservation.id, method.key, phone: phone);
      if (!mounted) return;
      await showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Réservation enregistrée'),
          content: Text(start.message),
          actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
        ),
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => ReservationDetailScreen(reservation: start.reservation)),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur réseau, réessayez.')));
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.reservation;
    return Scaffold(
      appBar: AppBar(title: const Text('Paiement')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            color: CollegeColors.greenLight,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${r.room.label} — ${r.eventDate.day}/${r.eventDate.month}/${r.eventDate.year}',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text('${formatTime(r.startTime)} - ${formatTime(r.endTime)}'),
                  const SizedBox(height: 12),
                  PriceBreakdown.fromReservation(r),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          FutureBuilder<PaymentOptions>(
            future: _options,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Column(children: [
                  const Text('Impossible de charger les moyens de paiement.'),
                  TextButton(
                    onPressed: () => setState(() => _options = _paymentService.options()),
                    child: const Text('Réessayer'),
                  ),
                ]);
              }
              final options = snapshot.data!;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Choisir un moyen de paiement', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 4),
                  Text(options.instructions, style: const TextStyle(color: Colors.grey)),
                  const SizedBox(height: 12),
                  for (final m in options.methods)
                    _PaymentMethodTile(
                      icon: m.online
                          ? Icons.phone_android
                          : (m.key == 'virement' ? Icons.account_balance : Icons.storefront),
                      label: m.label,
                      onTap: _processing ? null : () => _choose(m),
                    ),
                ],
              );
            },
          ),
          if (_processing) const Padding(
            padding: EdgeInsets.only(top: 16),
            child: Center(child: CircularProgressIndicator()),
          ),
        ],
      ),
    );
  }
}

class _PaymentMethodTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  const _PaymentMethodTile({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: CollegeColors.green),
        title: Text(label),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
