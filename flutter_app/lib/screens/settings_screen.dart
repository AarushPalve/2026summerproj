import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_theme_app/theme/theme_manager.dart';
import 'package:flutter_theme_app/widgets/themed_card.dart';
import 'package:flutter_theme_app/widgets/themed_text.dart';
import 'package:flutter_theme_app/utils/constants.dart';
import 'package:flutter_theme_app/theme/color_themes.dart';

class ThemeSelectionSection extends StatelessWidget {
  const ThemeSelectionSection({super.key});

  @override
  Widget build(BuildContext context) {
    final themeManager = Provider.of<ThemeManager>(context);
    final currentTheme = themeManager.currentTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const ThemedText(
          'Theme Selection',
          type: TextType.headline2,
        ),
        const SizedBox(height: 12),
        const ThemedText(
          'Choose from 5 beautiful dark themes:',
          type: TextType.body,
        ),
        const SizedBox(height: 24),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: AppColorThemes.allThemes.length,
          separatorBuilder: (context, index) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final themeId = index + 1;
            final themeData = AppColorThemes.getThemeById(themeId);
            final isSelected = currentTheme == themeData;

            return _buildThemeOption(
              context,
              themeId,
              _getThemeName(themeId),
              themeData,
              isSelected,
              themeManager,
            );
          },
        ),
      ],
    );
  }

  Widget _buildThemeOption(
    BuildContext context,
    int themeId,
    String themeName,
    ThemeData themeData,
    bool isSelected,
    ThemeManager themeManager,
  ) {
    return ThemedCard(
      title: themeName,
      subtitle: 'Tap to apply this theme',
      customColor: themeData.colorScheme.surface,
      onTap: () {
        themeManager.setTheme(themeId);
      },
      icon: Stack(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: themeData.colorScheme.primary,
              shape: BoxShape.circle,
            ),
          ),
          if (isSelected)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.check,
                  size: 16,
                  color: themeData.colorScheme.primary,
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _getThemeName(int themeId) {
    switch (themeId) {
      case 1:
        return AppConstants.theme1;
      case 2:
        return AppConstants.theme2;
      case 3:
        return AppConstants.theme3;
      case 4:
        return AppConstants.theme4;
      case 5:
        return AppConstants.theme5;
      default:
        return 'Unknown Theme';
    }
  }
}