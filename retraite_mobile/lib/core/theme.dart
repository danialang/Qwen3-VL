import 'package:flutter/material.dart';

/// Couleurs du Collège Catholique Bilingue de la Retraite : vert / blanc.
class CollegeColors {
  static const Color green = Color(0xFF0B6E4F);
  static const Color greenDark = Color(0xFF084C37);
  static const Color greenLight = Color(0xFFE3F3EC);
  static const Color gold = Color(0xFFD4AF37);

  static const Color statusValidated = Color(0xFF2E7D32);
  static const Color statusPending = Color(0xFFF9A825);
  static const Color statusCancelled = Color(0xFFC62828);
}

/// Échelle d'arrondis partagée par tous les composants (boutons, champs, cartes...).
class AppRadius {
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double pill = 999;
}

/// Échelle d'espacements partagée par les écrans.
class AppSpacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
}

const String _fontFamily = 'Poppins';

class AppTheme {
  static ThemeData light() => _build(
        scheme: ColorScheme.fromSeed(seedColor: CollegeColors.green, brightness: Brightness.light),
        appBarColor: CollegeColors.green,
        scaffoldBackgroundColor: Colors.white,
      );

  static ThemeData dark() => _build(
        scheme: ColorScheme.fromSeed(seedColor: CollegeColors.green, brightness: Brightness.dark),
        appBarColor: CollegeColors.greenDark,
        scaffoldBackgroundColor: const Color(0xFF121712),
      );

  static ThemeData _build({
    required ColorScheme scheme,
    required Color appBarColor,
    required Color scaffoldBackgroundColor,
  }) {
    final radius = BorderRadius.circular(AppRadius.md);
    final textTheme = _textTheme(scheme.brightness);

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      brightness: scheme.brightness,
      fontFamily: _fontFamily,
      textTheme: textTheme,
      scaffoldBackgroundColor: scaffoldBackgroundColor,
      appBarTheme: AppBarTheme(
        backgroundColor: appBarColor,
        foregroundColor: Colors.white,
        centerTitle: true,
        elevation: 0,
        titleTextStyle: textTheme.titleLarge?.copyWith(color: Colors.white, fontSize: 20),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: CollegeColors.green,
          foregroundColor: Colors.white,
          disabledBackgroundColor: CollegeColors.green.withOpacity(0.4),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.sm)),
          textStyle: textTheme.labelLarge,
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.sm)),
          textStyle: textTheme.labelLarge,
          side: BorderSide(color: scheme.outline),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          textStyle: textTheme.labelLarge,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.sm)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: radius, borderSide: BorderSide.none),
        enabledBorder: OutlineInputBorder(borderRadius: radius, borderSide: BorderSide.none),
        focusedBorder: OutlineInputBorder(
          borderRadius: radius,
          borderSide: const BorderSide(color: CollegeColors.green, width: 1.6),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: radius,
          borderSide: const BorderSide(color: CollegeColors.statusCancelled, width: 1.2),
        ),
        filled: true,
        fillColor: scheme.brightness == Brightness.dark
            ? Colors.white.withOpacity(0.06)
            : CollegeColors.greenLight,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        labelStyle: textTheme.bodyMedium,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: scheme.brightness == Brightness.dark ? const Color(0xFF1B221B) : Colors.white,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          side: BorderSide(color: scheme.outlineVariant.withOpacity(0.4)),
        ),
        margin: EdgeInsets.zero,
      ),
      chipTheme: ChipThemeData(
        backgroundColor: CollegeColors.greenLight,
        labelStyle: textTheme.labelMedium,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.pill)),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      ),
      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
        titleTextStyle: textTheme.titleMedium,
        contentTextStyle: textTheme.bodyMedium,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: scheme.brightness == Brightness.dark ? Colors.white : CollegeColors.greenDark,
        contentTextStyle: textTheme.bodyMedium?.copyWith(
          color: scheme.brightness == Brightness.dark ? Colors.black87 : Colors.white,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.sm)),
      ),
      dividerTheme: DividerThemeData(color: scheme.outlineVariant.withOpacity(0.5), space: 1),
      listTileTheme: ListTileThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
      ),
    );
  }

  static TextTheme _textTheme(Brightness brightness) {
    final base = brightness == Brightness.dark ? ThemeData.dark() : ThemeData.light();
    return base.textTheme
        .apply(fontFamily: _fontFamily)
        .copyWith(
          titleLarge: base.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700, fontFamily: _fontFamily),
          titleMedium: base.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600, fontFamily: _fontFamily),
          titleSmall: base.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600, fontFamily: _fontFamily),
          labelLarge: base.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600, fontFamily: _fontFamily),
          bodyLarge: base.textTheme.bodyLarge?.copyWith(fontFamily: _fontFamily),
          bodyMedium: base.textTheme.bodyMedium?.copyWith(fontFamily: _fontFamily),
        );
  }
}
