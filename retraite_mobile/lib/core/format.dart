/// Formate un montant avec des espaces entre les milliers : 5000000 -> "5 000 000 FCFA".
String formatFcfa(double amount) {
  final s = amount.toStringAsFixed(0);
  final buffer = StringBuffer();
  for (int i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 == 0) buffer.write(' ');
    buffer.write(s[i]);
  }
  return '$buffer FCFA';
}
