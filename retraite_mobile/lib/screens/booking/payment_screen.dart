import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../core/theme.dart';
import '../../models/reservation.dart';
import '../../services/payment_service.dart';
import '../reservations/reservation_detail_screen.dart';

class PaymentScreen extends StatefulWidget {
  final Reservation reservation;
  const PaymentScreen({super.key, required this.reservation});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  late final PaymentService _paymentService;
  bool _processing = false;

  @override
  void initState() {
    super.initState();
    _paymentService = PaymentService(context.read<SessionProvider>().api);
  }

  Future<void> _pay(PaymentMethod method) async {
    final confirmed = await showDialog<bool>(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Paiement en mode test'),
            content: Text(
              "Aucun véritable prélèvement n'est effectué (sandbox). "
              'Confirmer le paiement test via ${method.label} ?',
            ),
            actions: [
              TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
              ElevatedButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Confirmer')),
            ],
          ),
        ) ??
        false;
    if (!confirmed) return;

    setState(() => _processing = true);
    try {
      final updated = await _paymentService.confirmTestPayment(widget.reservation.id, method);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => ReservationDetailScreen(reservation: updated)),
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
                  const SizedBox(height: 8),
                  Text(
                    'Montant à régler : ${r.amount.toStringAsFixed(0)} FCFA',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: CollegeColors.green),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (!_paymentService.isGatewayConfigured)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Text(
                'Mode démonstration : la passerelle PaySika/PayPal Sandbox n\'est pas encore '
                'configurée (identifiants à venir). Le paiement est simulé pour ce MVP.',
                style: TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
              ),
            ),
          const SizedBox(height: 12),
          Text('Choisir un moyen de paiement', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 12),
          _PaymentMethodTile(
            icon: Icons.phone_android,
            label: PaymentMethod.paysikaOrangeMoney.label,
            onTap: _processing ? null : () => _pay(PaymentMethod.paysikaOrangeMoney),
          ),
          _PaymentMethodTile(
            icon: Icons.phone_android,
            label: PaymentMethod.paysikaMtnMomo.label,
            onTap: _processing ? null : () => _pay(PaymentMethod.paysikaMtnMomo),
          ),
          _PaymentMethodTile(
            icon: Icons.account_balance_wallet,
            label: PaymentMethod.paypalSandbox.label,
            onTap: _processing ? null : () => _pay(PaymentMethod.paypalSandbox),
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
