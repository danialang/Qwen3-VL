"""Grille tarifaire des locations du Collège (source : service de l'économat).

Tous les prix sont en FCFA. Pour modifier un tarif, il suffit de changer la valeur ci-dessous puis
de redémarrer le serveur : rien d'autre n'est à toucher (l'application mobile lit les prix depuis l'API).

Le prix d'une location dépend de trois choses :
  1. l'espace loué (gymnase, salle des fêtes, ...),
  2. la catégorie du client (personnel du Collège, extérieur, partenaire public, partenaire privé / ONG / fédération),
  3. la durée : « moins de 5 heures » ou « journée » (au-delà de 5 heures).
À cela s'ajoutent les prestations en plus (chaises, tables, sonorisation) et une caution remboursable.
"""
from dataclasses import dataclass, field
from datetime import time

# Ordre des colonnes de la grille : personnel du Collège, extérieur, partenaire public, partenaire privé.
CATEGORY_LABELS = {
    "personnel_college": "Personnel du Collège",
    "personnel_exterieur": "Personnel extérieur",
    "partenaire_public": "Partenaire public",
    "partenaire_prive": "Partenaire privé / ONG / Fédération sportive",
}
CATEGORY_KEYS = tuple(CATEGORY_LABELS)
DEFAULT_CATEGORY = "personnel_exterieur"

DURATION_LABELS = {"short": "Moins de 5 heures", "day": "Journée"}
SHORT_MAX_MINUTES = 5 * 60  # jusqu'à 5 h pile : tarif « moins de 5 heures »

# Caution remboursable, à verser en même temps que la location (grille de l'économat).
DEPOSIT_FCFA = 500_000

MAX_EXTRA_QUANTITY = 5000


@dataclass(frozen=True)
class Space:
    key: str
    label: str
    venue: str  # lieu physique : deux offres du même lieu ne peuvent pas être réservées en même temps
    extras_allowed: bool
    day: tuple[int, int, int, int]  # tarif « journée », dans l'ordre de CATEGORY_KEYS
    short: tuple[int, int, int, int]  # tarif « moins de 5 heures »


SPACES: dict[str, Space] = {s.key: s for s in [
    Space("gymnase", "Gymnase", "gymnase", True,
          (1_000_000, 1_500_000, 2_000_000, 2_000_000),
          (500_000, 750_000, 1_000_000, 1_000_000)),
    Space("salle_fetes", "Salle des fêtes (400 chaises et tables)", "salle_fetes", True,
          (4_500_000, 5_000_000, 5_500_000, 5_500_000),
          (2_250_000, 2_500_000, 2_750_000, 2_750_000)),
    Space("salle_reunion_repas", "Salle de réunion (400 chaises, tables et repas dans la salle)", "salle_fetes", True,
          (4_500_000, 5_000_000, 5_500_000, 5_500_000),
          (2_250_000, 2_500_000, 2_750_000, 2_750_000)),
    Space("salle_reunion", "Salle de réunion (400 chaises et tables)", "salle_fetes", True,
          (3_000_000, 3_500_000, 4_000_000, 4_000_000),
          (1_500_000, 1_750_000, 2_000_000, 2_000_000)),
    Space("cours_externe_gymnase", "Cours externes au gymnase", "gymnase", False,
          (500_000, 600_000, 700_000, 700_000),
          (250_000, 300_000, 350_000, 350_000)),
    Space("salle_fete_college", "Salle de fête du Collège", "salle_fete_college", True,
          (200_000, 250_000, 300_000, 300_000),
          # À CONFIRMER auprès de l'économat : 300 000 est la valeur écrite sur la grille « moins de 5 heures »
          # pour le partenaire privé (on attendrait 150 000, comme le partenaire public).
          (100_000, 125_000, 150_000, 300_000)),
    Space("salle_reunion_college", "Salle de réunion du Collège", "salle_reunion_college", True,
          (150_000, 200_000, 250_000, 250_000),
          (75_000, 100_000, 125_000, 125_000)),
    Space("salle_classe", "Salle de classe du Collège", "salle_classe", False,
          (10_000, 15_000, 20_000, 20_000),
          (10_000, 15_000, 20_000, 20_000)),
    Space("terrain_multisport", "Terrain multisport du Collège", "terrain_multisport", False,
          (10_000, 20_000, 25_000, 25_000),
          # À CONFIRMER auprès de l'économat : valeurs recopiées telles qu'écrites sur la grille
          # « moins de 5 heures » (20 000 pour l'extérieur alors que le partenaire public paie 12 500).
          (10_000, 20_000, 12_500, 12_500)),
    Space("tatami", "Tatami du Collège", "tatami", False,
          (15_000, 25_000, 40_000, 50_000),
          (10_000, 15_000, 25_000, 25_000)),
    Space("cours_college", "Cours du Collège", "cours_college", False,
          (300_000, 400_000, 500_000, 500_000),
          (150_000, 200_000, 250_000, 250_000)),
]}
# Non proposés dans l'application (décision du père économe) : appartement meublé, chambre meublée, cuisine.


@dataclass(frozen=True)
class Extra:
    key: str
    label: str
    group: str  # « chaises », « tables » ou « sonorisation »
    unit_price: int


EXTRAS: dict[str, Extra] = {e.key: e for e in [
    Extra("chaise_simple_rouge", "Chaise simple rouge", "chaises", 1_500),
    Extra("chaise_vip_napoleon", "Chaise VIP Napoléon", "chaises", 2_000),
    Extra("chaise_vip_prestige", "Chaise VIP Prestige", "chaises", 5_000),
    Extra("chaise_des_maries", "Chaises des mariés", "chaises", 50_000),
    Extra("table_simple", "Table simple", "tables", 2_000),
    Extra("table_vip", "Table VIP", "tables", 50_000),
    Extra("sonorisation_complete", "Sonorisation complète", "sonorisation", 350_000),
]}

MONTHLY_NOTE = "Pour toute location mensuelle ou annuelle, un taux forfaitaire est appliqué : contactez l'administration."


class TariffError(ValueError):
    """Demande de tarif invalide (espace, catégorie ou prestation inconnus...)."""


@dataclass
class QuoteLine:
    key: str
    label: str
    quantity: int
    unit_price: int
    total: int


@dataclass
class Quote:
    room: str
    category: str
    duration_type: str
    rental: int
    extras: list[QuoteLine] = field(default_factory=list)

    @property
    def extras_total(self) -> int:
        return sum(line.total for line in self.extras)

    @property
    def total(self) -> int:
        """Location + prestations (c'est le chiffre d'affaires de la réservation)."""
        return self.rental + self.extras_total

    @property
    def deposit(self) -> int:
        return DEPOSIT_FCFA

    @property
    def total_due(self) -> int:
        """Ce que le client verse : location + prestations + caution remboursable."""
        return self.total + self.deposit


def room_label(room_key: str) -> str:
    space = SPACES.get(room_key)
    return space.label if space else room_key


def category_label(category: str | None) -> str:
    return CATEGORY_LABELS.get(category or "", "Réservation interne du Collège")


def venue_rooms(room_key: str) -> list[str]:
    """Toutes les offres qui occupent le même lieu physique (y compris celle demandée)."""
    space = SPACES.get(room_key)
    if not space:
        return [room_key]
    return [s.key for s in SPACES.values() if s.venue == space.venue]


def duration_minutes(start: time, end: time) -> int:
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def duration_type(start: time, end: time) -> str:
    minutes = duration_minutes(start, end)
    if minutes <= 0:
        raise TariffError("L'heure de fin doit être après l'heure de début.")
    return "short" if minutes <= SHORT_MAX_MINUTES else "day"


def compute_quote(room_key: str, category: str, start: time, end: time, extras: dict[str, int] | None = None) -> Quote:
    space = SPACES.get(room_key)
    if not space:
        raise TariffError(f"Espace inconnu : {room_key}.")
    if category not in CATEGORY_LABELS:
        raise TariffError(f"Catégorie de client inconnue : {category}.")

    kind = duration_type(start, end)
    prices = space.short if kind == "short" else space.day
    rental = prices[CATEGORY_KEYS.index(category)]

    lines: list[QuoteLine] = []
    for key, quantity in (extras or {}).items():
        extra = EXTRAS.get(key)
        if not extra:
            raise TariffError(f"Prestation inconnue : {key}.")
        if not space.extras_allowed:
            raise TariffError(f"Les prestations (chaises, tables, sonorisation) ne sont pas proposées pour : {space.label}.")
        if quantity < 1 or quantity > MAX_EXTRA_QUANTITY:
            raise TariffError(f"Quantité invalide pour {extra.label}.")
        lines.append(QuoteLine(key, extra.label, quantity, extra.unit_price, extra.unit_price * quantity))
    return Quote(room_key, category, kind, rental, lines)


def catalog() -> dict:
    """Catalogue complet, lu par l'application mobile (aucun prix n'est écrit en dur dans l'application)."""
    return {
        "categories": [{"key": k, "label": v} for k, v in CATEGORY_LABELS.items()],
        "durations": [{"key": k, "label": v} for k, v in DURATION_LABELS.items()],
        "short_max_hours": SHORT_MAX_MINUTES // 60,
        "deposit": DEPOSIT_FCFA,
        "spaces": [
            {
                "key": s.key,
                "label": s.label,
                "extras_allowed": s.extras_allowed,
                "prices": {
                    "day": dict(zip(CATEGORY_KEYS, s.day)),
                    "short": dict(zip(CATEGORY_KEYS, s.short)),
                },
            }
            for s in SPACES.values()
        ],
        "extras": [
            {"key": e.key, "label": e.label, "group": e.group, "unit_price": e.unit_price} for e in EXTRAS.values()
        ],
        "note": MONTHLY_NOTE,
    }
