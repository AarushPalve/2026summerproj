import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeManager with ChangeNotifier {
  static const String _themeKey = 'current_theme_id';
  late ThemeData _currentTheme;
  late SharedPreferences _prefs;

  ThemeManager() {
    _currentTheme = AppColorThemes.midnightOcean; // Default theme
    _loadThemeFromPrefs();
  }

  ThemeData get currentTheme => _currentTheme;

  Future<void> _loadThemeFromPrefs() async {
    _prefs = await SharedPreferences.getInstance();
    final themeId = _prefs.getInt(_themeKey) ?? 1; // Default to theme 1
    _currentTheme = AppColorThemes.getThemeById(themeId);
    notifyListeners();
  }

  Future<void> setTheme(int themeId) async {
    if (themeId < 1 || themeId > 5) {
      throw ArgumentError('Theme ID must be between 1 and 5');
    }

    _currentTheme = AppColorThemes.getThemeById(themeId);
    await _prefs.setInt(_themeKey, themeId);
    notifyListeners();
  }

  Future<void> cycleTheme() async {
    final currentId = AppColorThemes.allThemes.indexOf(_currentTheme) + 1;
    final nextId = currentId % 5 + 1; // Cycle through 1-5
    await setTheme(nextId);
  }
}