import os
from dataclasses import dataclass

OFFLINE_METHODS = {
    "economat": "Paiement à l'économat du Collège",
    "virement": "Virement bancaire",
}


class PaymentProviderError(Exception):
    pass


@dataclass
class CheckoutStart:
    """Ce que l'opérateur renvoie au lancement d'un paiement."""
    transaction_id: str
    checkout_url: str | None = None  # page de paiement à ouvrir, si l'opérateur en fournit une
    message: str | None = None       # ex. « Validez le paiement sur votre téléphone »


@dataclass
class WebhookResult:
    """Confirmation reçue de l'opérateur (jamais du client)."""
    transaction_id: str
    success: bool


class PaymentProvider:
    """Emplacement d'un opérateur. Il devient actif quand toutes ses variables d'environnement sont remplies.

    Pour brancher un opérateur : renseigner `env_vars`, puis écrire `start_payment` et `parse_webhook`
    d'après sa documentation (en vérifiant la signature du webhook).
    """
    key = ""
    label = ""
    env_vars: tuple[str, ...] = ()

    @property
    def configured(self) -> bool:
        return bool(self.env_vars) and all(os.getenv(v) for v in self.env_vars)

    def start_payment(self, reservation, amount: int, phone: str | None) -> CheckoutStart:
        raise PaymentProviderError(f"{self.label} : intégration pas encore disponible.")

    def parse_webhook(self, body: bytes, headers: dict) -> WebhookResult:
        raise PaymentProviderError(f"{self.label} : intégration pas encore disponible.")


class OrangeMoneyProvider(PaymentProvider):
    key = "orange_money"
    label = "Orange Money"
    env_vars = ("ORANGE_MONEY_CLIENT_ID", "ORANGE_MONEY_CLIENT_SECRET", "ORANGE_MONEY_MERCHANT_KEY")


class MtnMomoProvider(PaymentProvider):
    key = "mtn_momo"
    label = "MTN Mobile Money"
    env_vars = ("MTN_MOMO_SUBSCRIPTION_KEY", "MTN_MOMO_API_USER", "MTN_MOMO_API_KEY")


class AccessBankProvider(PaymentProvider):
    key = "access_bank"
    label = "Access Bank"
    env_vars = ("ACCESS_BANK_MERCHANT_ID", "ACCESS_BANK_API_KEY")


_PROVIDERS = {p.key: p for p in (OrangeMoneyProvider(), MtnMomoProvider(), AccessBankProvider())}


def get_provider(key: str) -> PaymentProvider | None:
    return _PROVIDERS.get(key)


def available_methods() -> list[dict]:
    """Moyens proposés au client : hors ligne toujours, en ligne seulement s'ils sont configurés."""
    methods = [{"key": k, "label": v, "online": False} for k, v in OFFLINE_METHODS.items()]
    methods += [{"key": p.key, "label": p.label, "online": True} for p in _PROVIDERS.values() if p.configured]
    return methods
