import 'package:flutter/material.dart';

import '../core/theme.dart';

/// Emplacement pour le logo/les photos du Collège.
///
/// Aucune image officielle n'a encore été fournie : ce widget affiche un
/// repli (icône + initiales) et charge `assets/images/logo.png` s'il existe.
/// Une fois les visuels du Collège reçus, les déposer dans
/// `assets/images/` (logo.png, accueil.jpg, ...) sans autre changement de code.
class CollegeLogo extends StatelessWidget {
  final double size;
  const CollegeLogo({super.key, this.size = 72});

  @override
  Widget build(BuildContext context) {
    return ClipOval(
      child: Image.asset(
        'assets/images/logo.png',
        width: size,
        height: size,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => Container(
          width: size,
          height: size,
          decoration: const BoxDecoration(color: CollegeColors.green, shape: BoxShape.circle),
          alignment: Alignment.center,
          child: Text(
            'CCR',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: size * 0.24,
            ),
          ),
        ),
      ),
    );
  }
}

/// Bannière d'accueil : image du Collège si disponible, sinon dégradé vert.
class CollegeHeroBanner extends StatelessWidget {
  final double height;
  const CollegeHeroBanner({super.key, this.height = 160});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      width: double.infinity,
      child: Image.asset(
        'assets/images/accueil.jpg',
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [CollegeColors.green, CollegeColors.greenDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          alignment: Alignment.center,
          child: const Icon(Icons.school, color: Colors.white, size: 56),
        ),
      ),
    );
  }
}
