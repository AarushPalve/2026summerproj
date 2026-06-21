import 'package:flutter/material.dart';

class AppColorThemes {
  // Theme 1: Midnight Ocean
  static final ThemeData midnightOcean = ThemeData(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF00BCD4),      // Cyan accent
      secondary: Color(0xFF0097A7),     // Darker cyan
      surface: Color(0xFF0D1B2A),       // Dark blue surface
      background: Color(0xFF011627),     // Deep navy background
      error: Color(0xFFE71D36),         // Red error
      onPrimary: Color(0xFF011627),     // Dark text on primary
      onSecondary: Color(0xFFFFFFFF),   // White text on secondary
      onSurface: Color(0xFFE1F5FE),     // Light text on surface
      onBackground: Color(0xFFE1F5FE),  // Light text on background
      onError: Color(0xFFFFFFFF),        // White text on error
    ),
    scaffoldBackgroundColor: const Color(0xFF011627),
    cardColor: const Color(0xFF0D1B2A),
    dialogBackgroundColor: const Color(0xFF0D1B2A),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF00BCD4),
      foregroundColor: Color(0xFF011627),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF00838F),
      selectedItemColor: Color(0xFF00E5FF),
      unselectedItemColor: Color(0xFFB2EBF2),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF00BCD4),
      foregroundColor: Color(0xFF011627),
    ),
  );

  // Theme 2: Deep Forest
  static final ThemeData deepForest = ThemeData(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF4CAF50),      // Green accent
      secondary: Color(0xFF388E3C),     // Darker green
      surface: Color(0xFF1B3A26),       // Dark green surface
      background: Color(0xFF0E2012),     // Deep forest background
      error: Color(0xFFD32F2F),         // Red error
      onPrimary: Color(0xFF0E2012),     // Dark text on primary
      onSecondary: Color(0xFFFFFFFF),   // White text on secondary
      onSurface: Color(0xFFC8E6C9),     // Light text on surface
      onBackground: Color(0xFFC8E6C9),  // Light text on background
      onError: Color(0xFFFFFFFF),        // White text on error
    ),
    scaffoldBackgroundColor: const Color(0xFF0E2012),
    cardColor: const Color(0xFF1B3A26),
    dialogBackgroundColor: const Color(0xFF1B3A26),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF4CAF50),
      foregroundColor: Color(0xFF0E2012),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF388E3C),
      selectedItemColor: Color(0xFF81C784),
      unselectedItemColor: Color(0xFFA5D6A7),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF4CAF50),
      foregroundColor: Color(0xFF0E2012),
    ),
  );

  // Theme 3: Royal Velvet
  static final ThemeData royalVelvet = ThemeData(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF9C27B0),      // Purple accent
      secondary: Color(0xFF7B1FA2),     // Darker purple
      surface: Color(0xFF311B4F),       // Dark purple surface
      background: Color(0xFF1A0F2A),     // Deep purple background
      error: Color(0xFFC2185B),         // Pink error
      onPrimary: Color(0xFFFFFFFF),     // White text on primary
      onSecondary: Color(0xFFFFFFFF),   // White text on secondary
      onSurface: Color(0xFFF3E5F5),     // Light text on surface
      onBackground: Color(0xFFF3E5F5),  // Light text on background
      onError: Color(0xFFFFFFFF),        // White text on error
    ),
    scaffoldBackgroundColor: const Color(0xFF1A0F2A),
    cardColor: const Color(0xFF311B4F),
    dialogBackgroundColor: const Color(0xFF311B4F),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF9C27B0),
      foregroundColor: Color(0xFFFFFFFF),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF7B1FA2),
      selectedItemColor: Color(0xFFBA68C8),
      unselectedItemColor: Color(0xFFE1BEE7),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF9C27B0),
      foregroundColor: Color(0xFFFFFFFF),
    ),
  );

  // Theme 4: Mystic Purple
  static final ThemeData mysticPurple = ThemeData(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF673AB7),      // Deep purple accent
      secondary: Color(0xFF512DA8),     // Darker purple
      surface: Color(0xFF261C32),       // Dark purple surface
      background: Color(0xFF0D051C),     // Very deep purple background
      error: Color(0xFFD50000),         // Red error
      onPrimary: Color(0xFFFFFFFF),     // White text on primary
      onSecondary: Color(0xFFFFFFFF),   // White text on secondary
      onSurface: Color(0xFFEDE7F6),     // Light text on surface
      onBackground: Color(0xFFEDE7F6),  // Light text on background
      onError: Color(0xFFFFFFFF),        // White text on error
    ),
    scaffoldBackgroundColor: const Color(0xFF0D051C),
    cardColor: const Color(0xFF261C32),
    dialogBackgroundColor: const Color(0xFF261C32),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF673AB7),
      foregroundColor: Color(0xFFFFFFFF),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF512DA8),
      selectedItemColor: Color(0xFF9575CD),
      unselectedItemColor: Color(0xFFD1C4E9),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF673AB7),
      foregroundColor: Color(0xFFFFFFFF),
    ),
  );

  // Theme 5: Carbon Fiber
  static final ThemeData carbonFiber = ThemeData(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFF212121),       // Dark gray accent
      secondary: Color(0xFF424242),      // Lighter gray
      surface: Color(0xFF121212),        // Black surface
      background: Color(0xFF000000),      // Pure black background
      error: Color(0xFFCF6679),         // Soft red error
      onPrimary: Color(0xFFFFFFFF),      // White text on primary
      onSecondary: Color(0xFFFFFFFF),    // White text on secondary
      onSurface: Color(0xFFE0E0E0),      // Light gray text on surface
      onBackground: Color(0xFFE0E0E0),   // Light gray text on background
      onError: Color(0xFF000000),         // Black text on error
    ),
    scaffoldBackgroundColor: const Color(0xFF000000),
    cardColor: const Color(0xFF121212),
    dialogBackgroundColor: const Color(0xFF121212),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF212121),
      foregroundColor: Color(0xFFFFFFFF),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF121212),
      selectedItemColor: Color(0xFF757575),
      unselectedItemColor: Color(0xFFBDBDBD),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: Color(0xFF212121),
      foregroundColor: Color(0xFFFFFFFF),
    ),
  );

  // Get theme by ID
  static ThemeData getThemeById(int themeId) {
    switch (themeId) {
      case 1:
        return midnightOcean;
      case 2:
        return deepForest;
      case 3:
        return royalVelvet;
      case 4:
        return mysticPurple;
      case 5:
        return carbonFiber;
      default:
        return midnightOcean;
    }
  }

  // Get all themes
  static List<ThemeData> get allThemes => [
    midnightOcean,
    deepForest,
    royalVelvet,
    mysticPurple,
    carbonFiber,
  ];
}