import 'package:flutter_test/flutter_test.dart';
import 'package:retraite_mobile/core/validators.dart';

void main() {
  group('validateFullName', () {
    test('accepte des noms normaux', () {
      for (final n in ['Jean Dupont', "Marie-Claire N'Guessan", 'Éloïse Ndzié', 'Aïssatou', 'Jean-Pierre N’Dri']) {
        expect(validateFullName(n), isNull, reason: n);
      }
    });
    test('refuse les chiffres, symboles et noms vides', () {
      for (final n in ['', '  ', 'Jean2', '123', 'Jean_Dupont', 'J', 'Jean @Dupont']) {
        expect(validateFullName(n), isNotNull, reason: n);
      }
    });
    test('ignore les espaces autour du nom', () {
      expect(validateFullName('  Jean Dupont  '), isNull);
    });
  });

  group('validateEmailAddress', () {
    test('accepte gmail, icloud et autres fournisseurs connus', () {
      for (final e in ['nom@gmail.com', 'Nom.Prenom@iCloud.com', 'a_b@outlook.fr', 'x@yahoo.com']) {
        expect(validateEmailAddress(e), isNull, reason: e);
      }
    });
    test('refuse les fautes et les adresses inventées', () {
      for (final e in ['', 'nom', 'nom@', 'nom@gmail', 'nom@gmail.con', 'nom@gmai.com', 'nom@exemple.com', 'nom @gmail.com']) {
        expect(validateEmailAddress(e), isNotNull, reason: e);
      }
    });
  });
}
