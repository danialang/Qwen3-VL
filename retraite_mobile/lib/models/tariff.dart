// Grille tarifaire du Collège : toutes les données viennent de l'API (GET /tariffs), aucun prix n'est écrit ici.

int _asInt(dynamic value) => value is num ? value.toInt() : int.tryParse(value?.toString() ?? '') ?? 0;

class TariffCategory {
  final String key;
  final String label;
  const TariffCategory({required this.key, required this.label});

  factory TariffCategory.fromJson(Map<String, dynamic> json) =>
      TariffCategory(key: json['key'] as String, label: json['label'] as String);
}

class TariffExtra {
  final String key;
  final String label;
  final String group;
  final int unitPrice;
  const TariffExtra({required this.key, required this.label, required this.group, required this.unitPrice});

  factory TariffExtra.fromJson(Map<String, dynamic> json) => TariffExtra(
        key: json['key'] as String,
        label: json['label'] as String,
        group: json['group'] as String,
        unitPrice: _asInt(json['unit_price']),
      );
}

class TariffCatalog {
  final List<TariffCategory> categories;
  final List<TariffExtra> extras;
  final Set<String> spacesWithExtras;
  final int deposit;
  final String note;

  const TariffCatalog({
    required this.categories,
    required this.extras,
    required this.spacesWithExtras,
    required this.deposit,
    required this.note,
  });

  bool allowsExtras(String roomApiValue) => spacesWithExtras.contains(roomApiValue);

  factory TariffCatalog.fromJson(Map<String, dynamic> json) => TariffCatalog(
        categories: (json['categories'] as List)
            .map((e) => TariffCategory.fromJson(e as Map<String, dynamic>))
            .toList(),
        extras: (json['extras'] as List).map((e) => TariffExtra.fromJson(e as Map<String, dynamic>)).toList(),
        spacesWithExtras: (json['spaces'] as List)
            .map((e) => e as Map<String, dynamic>)
            .where((s) => s['extras_allowed'] == true)
            .map((s) => s['key'] as String)
            .toSet(),
        deposit: _asInt(json['deposit']),
        note: json['note'] as String? ?? '',
      );
}

/// Une ligne de prestation (chaises, tables, sonorisation) avec son prix figé.
class QuoteLine {
  final String key;
  final String label;
  final int quantity;
  final int unitPrice;
  final int total;
  const QuoteLine({
    required this.key,
    required this.label,
    required this.quantity,
    required this.unitPrice,
    required this.total,
  });

  factory QuoteLine.fromJson(Map<String, dynamic> json) => QuoteLine(
        key: json['key'] as String,
        label: json['label'] as String,
        quantity: _asInt(json['quantity']),
        unitPrice: _asInt(json['unit_price']),
        total: _asInt(json['total']),
      );
}

/// Prix détaillé d'une location : location + prestations = total, puis caution remboursable.
class Quote {
  final String categoryLabel;
  final String durationLabel;
  final int rental;
  final List<QuoteLine> extras;
  final int extrasTotal;
  final int total;
  final int deposit;
  final int totalDue;

  const Quote({
    required this.categoryLabel,
    required this.durationLabel,
    required this.rental,
    required this.extras,
    required this.extrasTotal,
    required this.total,
    required this.deposit,
    required this.totalDue,
  });

  factory Quote.fromJson(Map<String, dynamic> json) => Quote(
        categoryLabel: json['client_category_label'] as String,
        durationLabel: json['duration_label'] as String,
        rental: _asInt(json['rental']),
        extras: (json['extras'] as List).map((e) => QuoteLine.fromJson(e as Map<String, dynamic>)).toList(),
        extrasTotal: _asInt(json['extras_total']),
        total: _asInt(json['total']),
        deposit: _asInt(json['deposit']),
        totalDue: _asInt(json['total_due']),
      );
}
