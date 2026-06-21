import 'package:flutter/material.dart';

// Custom theme extension for additional colors
class CustomThemeColors extends ThemeExtension<CustomThemeColors> {
  final Color? successColor;
  final Color? warningColor;
  final Color? infoColor;
  final Color? gradientStart;
  final Color? gradientEnd;

  const CustomThemeColors({
    this.successColor,
    this.warningColor,
    this.infoColor,
    this.gradientStart,
    this.gradientEnd,
  });

  @override
  CustomThemeColors copyWith({
    Color? successColor,
    Color? warningColor,
    Color? infoColor,
    Color? gradientStart,
    Color? gradientEnd,
  }) {
    return CustomThemeColors(
      successColor: successColor ?? this.successColor,
      warningColor: warningColor ?? this.warningColor,
      infoColor: infoColor ?? this.infoColor,
      gradientStart: gradientStart ?? this.gradientStart,
      gradientEnd: gradientEnd ?? this.gradientEnd,
    );
  }

  @override
  CustomThemeColors lerp(ThemeExtension<CustomThemeColors>? other, double t) {
    if (other is! CustomThemeColors) {
      return this;
    }

    return CustomThemeColors(
      successColor: Color.lerp(successColor, other.successColor, t),
      warningColor: Color.lerp(warningColor, other.warningColor, t),
      infoColor: Color.lerp(infoColor, other.infoColor, t),
      gradientStart: Color.lerp(gradientStart, other.gradientStart, t),
      gradientEnd: Color.lerp(gradientEnd, other.gradientEnd, t),
    );
  }

  // Helper method to get custom colors for each theme
  static CustomThemeColors forTheme(ThemeData theme) {
    if (theme == AppColorThemes.midnightOcean) {
      return const CustomThemeColors(
        successColor: Color(0xFF4CAF50),
        warningColor: Color(0xFFFFC107),
        infoColor: Color(0xFF2196F3),
        gradientStart: Color(0xFF006064),
        gradientEnd: Color(0xFF0097A7),
      );
    } else if (theme == AppColorThemes.deepForest) {
      return const CustomThemeColors(
        successColor: Color(0xFF8BC34A),
        warningColor: Color(0xFFFFEB3B),
        infoColor: Color(0xFF00BCD4),
        gradientStart: Color(0xFF1B5E20),
        gradientEnd: Color(0xFF2E7D32),
      );
    } else if (theme == AppColorThemes.royalVelvet) {
      return const CustomThemeColors(
        successColor: Color(0xFFE91E63),
        warningColor: Color(0xFFFF9800),
        infoColor: Color(0xFF3F51B5),
        gradientStart: Color(0xFF6A1B9A),
        gradientEnd: Color(0xFF8E24AA),
      );
    } else if (theme == AppColorThemes.mysticPurple) {
      return const CustomThemeColors(
        successColor: Color(0xFF9C27B0),
        warningColor: Color(0xFFFFC107),
        infoColor: Color(0xFF03A9F4),
        gradientStart: Color(0xFF4527A0),
        gradientEnd: Color(0xFF5E35B1),
      );
    } else { // Carbon Fiber
      return const CustomThemeColors(
        successColor: Color(0xFF4CAF50),
        warningColor: Color(0xFFFF9800),
        infoColor: Color(0xFF2196F3),
        gradientStart: Color(0xFF333333),
        gradientEnd: Color(0xFF424242),
      );
    }
  }
}