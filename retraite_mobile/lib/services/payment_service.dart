import '../core/api_client.dart';
import '../models/reservation.dart';
import 'reservation_service.dart';

enum PaymentMethod { paysikaOrangeMoney, paysikaMtnMomo, paypalSandbox }

extension PaymentMethodApi on PaymentMethod {
  String get apiValue {
    switch (this) {
      case PaymentMethod.paysikaOrangeMoney:
        return 'paysika_orange_money';
      case PaymentMethod.paysikaMtnMomo:
        return 'paysika_mtn_momo';
      case PaymentMethod.paypalSandbox:
        return 'paypal_sandbox';
    }
  }

  String get label {
    switch (this) {
      case PaymentMethod.paysikaOrangeMoney:
        return 'Orange Money (via PaySika)';
      case PaymentMethod.paysikaMtnMomo:
        return 'MTN Mobile Money (via PaySika)';
      case PaymentMethod.paypalSandbox:
        return 'PayPal Sandbox';
    }
  }
}

/// Intégration de paiement en mode test.
///
/// Aucun identifiant sandbox PaySika/PayPal n'est disponible pour ce MVP :
/// [gatewayCheckoutUrl] reste vide tant qu'il n'est pas renseigné. En
/// attendant, [confirmTestPayment] simule un paiement réussi et enregistre
/// une référence de test côté backend, pour ne pas bloquer le parcours.
class PaymentService {
  final ReservationService reservationService;
  PaymentService(ApiClient api) : reservationService = ReservationService(api);

  /// URL de la page de paiement sandbox (PaySika ou PayPal) à renseigner
  /// une fois les identifiants obtenus. Vide = mode simulation locale.
  static const String gatewayCheckoutUrl = '';

  bool get isGatewayConfigured => gatewayCheckoutUrl.isNotEmpty;

  Future<Reservation> confirmTestPayment(int reservationId, PaymentMethod method) {
    final reference = 'TEST-${method.apiValue.toUpperCase()}-${DateTime.now().millisecondsSinceEpoch}';
    return reservationService.pay(reservationId, method: method.apiValue, reference: reference);
  }
}
