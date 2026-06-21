import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_theme_app/theme/color_themes.dart';
import 'package:flutter_theme_app/theme/theme_data.dart';

void main() {
  group('Theme Tests', () {
    test('All themes should be dark', () {
      for (final theme in AppColorThemes.allThemes) {
        expect(theme.brightness, equals(Brightness.dark));
      }
    });

    test('getThemeById should return correct theme', () {
      expect(AppColorThemes.getThemeById(1), equals(AppColorThemes.midnightOcean));
      expect(AppColorThemes.getThemeById(2), equals(AppColorThemes.deepForest));
      expect(AppColorThemes.getThemeById(3), equals(AppColorThemes.royalVelvet));
      expect(AppColorThemes.getThemeById(4), equals(AppColorThemes.mysticPurple));
      expect(AppColorThemes.getThemeById(5), equals(AppColorThemes.carbonFiber));
    });

    test('getThemeById should return default theme for invalid ID', () {
      expect(AppColorThemes.getThemeById(0), equals(AppColorThemes.midnightOcean));
      expect(AppColorThemes.getThemeById(6), equals(AppColorThemes.midnightOcean));
      expect(AppColorThemes.getThemeById(100), equals(AppColorThemes.midnightOcean));
    });

    test('CustomThemeColors should have correct values for each theme', () {
      final midnightCustom = CustomThemeColors.forTheme(AppColorThemes.midnightOcean);
      expect(midnightCustom.successColor, equals(const Color(0xFF4CAF50)));
      expect(midnightCustom.gradientStart, equals(const Color(0xFF006064)));

      final forestCustom = CustomThemeColors.forTheme(AppColorThemes.deepForest);
      expect(forestCustom.successColor, equals(const Color(0xFF8BC34A)));
      expect(forestCustom.gradientStart, equals(const Color(0xFF1B5E20)));

      final royalCustom = CustomThemeColors.forTheme(AppColorThemes.royalVelvet);
      expect(royalCustom.successColor, equals(const Color(0xFFE91E63)));
      expect(royalCustom.gradientStart, equals(const Color(0xFF6A1B9A)));

      final mysticCustom = CustomThemeColors.forTheme(AppColorThemes.mysticPurple);
      expect(mysticCustom.successColor, equals(const Color(0xFF9C27B0)));
      expect(mysticCustom.gradientStart, equals(const Color(0xFF4527A0)));

      final carbonCustom = CustomThemeColors.forTheme(AppColorThemes.carbonFiber);
      expect(carbonCustom.successColor, equals(const Color(0xFF4CAF50)));
      expect(carbonCustom.gradientStart, equals(const Color(0xFF333333)));
    });

    test('Theme color schemes should have all required colors', () {
      for (final theme in AppColorThemes.allThemes) {
        final colorScheme = theme.colorScheme;
        expect(colorScheme.primary, isNotNull);
        expect(colorScheme.secondary, isNotNull);
        expect(colorScheme.surface, isNotNull);
        expect(colorScheme.background, isNotNull);
        expect(colorScheme.error, isNotNull);
        expect(colorScheme.onPrimary, isNotNull);
        expect(colorScheme.onSecondary, isNotNull);
        expect(colorScheme.onSurface, isNotNull);
        expect(colorScheme.onBackground, isNotNull);
        expect(colorScheme.onError, isNotNull);
      }
    });

    test('CustomThemeColors lerp should work correctly', () {
      final custom1 = const CustomThemeColors(
        successColor: Color(0xFF4CAF50),
        warningColor: Color(0xFFFFC107),
      );

      final custom2 = const CustomThemeColors(
        successColor: Color(0xFFE91E63),
        warningColor: Color(0xFFFF9800),
      );

      final lerped = custom1.lerp(custom2, 0.5);
      expect(lerped, isA<CustomThemeColors>());
    });

    test('CustomThemeColors copyWith should create new instance', () {
      final original = const CustomThemeColors(
        successColor: Color(0xFF4CAF50),
      );

      final copied = original.copyWith(warningColor: Color(0xFFFFC107));
      expect(copied.successColor, equals(original.successColor));
      expect(copied.warningColor, equals(const Color(0xFFFFC107)));
    });
  });
}