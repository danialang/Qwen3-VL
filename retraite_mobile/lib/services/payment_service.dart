import 'package:url_launcher/url_launcher.dart';

import '../core/api_client.dart';
import '../models/reservation.dart';

class PaymentMethodOption {
  final String key;
  final String label;
  final bool online;

  PaymentMethodOption({required this.key, required this.label, required this.online});

  factory PaymentMethodOption.fromJson(Map<String, dynamic> json) => PaymentMethodOption(
        key: json['key'] as String,
        label: json['label'] as String,
        online: json['online'] as bool? ?? false,
      );
}

class PaymentOptions {
  final List<PaymentMethodOption> methods;
  final String instructions;

  PaymentOptions({required this.methods, required this.instructions});

  factory PaymentOptions.fromJson(Map<String, dynamic> json) => PaymentOptions(
        methods: (json['methods'] as List).map((e) => PaymentMethodOption.fromJson(e as Map<String, dynamic>)).toList(),
        instructions: json['instructions'] as String? ?? '',
      );
}

class PaymentStart {
  final Reservation reservation;
  final String? checkoutUrl;
  final String message;

  PaymentStart({required this.reservation, required this.checkoutUrl, required this.message});
}

/// Paiement : le serveur décide des moyens proposés (économat, virement, puis Orange/MTN/Access
/// quand leurs API seront branchées). Le paiement n'est confirmé que par l'administrateur ou l'opérateur.
class PaymentService {
  final ApiClient api;
  PaymentService(this.api);

  Future<PaymentOptions> options() async =>
      PaymentOptions.fromJson(await api.get('/payments/options') as Map<String, dynamic>);

  Future<PaymentStart> choose(int reservationId, String method, {String? phone}) async {
    final json = await api.post('/reservations/$reservationId/pay', body: {
      'method': method,
      if (phone != null && phone.isNotEmpty) 'phone': phone,
    }) as Map<String, dynamic>;
    final start = PaymentStart(
      reservation: Reservation.fromJson(json['reservation'] as Map<String, dynamic>),
      checkoutUrl: json['checkout_url'] as String?,
      message: json['message'] as String? ?? '',
    );
    if (start.checkoutUrl != null) {
      await launchUrl(Uri.parse(start.checkoutUrl!), mode: LaunchMode.externalApplication);
    }
    return start;
  }
}
