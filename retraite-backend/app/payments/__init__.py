"""Moyens de paiement.

Deux familles :
- hors ligne (économat, virement) : le client paie au Collège, l'administrateur confirme dans l'appli ;
- en ligne (Orange Money, MTN MoMo, Access Bank) : branchés dans providers.py dès réception des API.
"""
from .providers import OFFLINE_METHODS, PaymentProviderError, available_methods, get_provider

__all__ = ["OFFLINE_METHODS", "PaymentProviderError", "available_methods", "get_provider"]
