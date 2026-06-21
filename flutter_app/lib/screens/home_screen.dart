import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_theme_app/theme/theme_manager.dart';
import 'package:flutter_theme_app/widgets/themed_button.dart';
import 'package:flutter_theme_app/widgets/themed_card.dart';
import 'package:flutter_theme_app/widgets/themed_text.dart';
import 'package:flutter_theme_app/utils/constants.dart';
import 'package:flutter_theme_app/theme/theme_data.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final customColors = theme.extension<CustomThemeColors>()!;
    final themeManager = Provider.of<ThemeManager>(context);

    return Scaffold(
      appBar: AppBar(
        title: const ThemedText(
          AppConstants.appName,
          type: TextType.headline3,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Current Theme Info
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            ThemedText(
                              'Current Theme',
                              type: TextType.subtitle,
                            ),
                            const SizedBox(height: 4),
                            ThemedText(
                              _getCurrentThemeName(themeManager.currentTheme),
                              type: TextType.headline3,
                            ),
                          ],
                        ),
                      ),
                      ThemedButton(
                        text: 'Cycle Theme',
                        onPressed: () {
                          themeManager.cycleTheme();
                        },
                        isPrimary: true,
                        icon: Icons.cached,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Theme Showcase Section
              ThemedText(
                'Theme Showcase',
                type: TextType.headline2,
              ),
              const SizedBox(height: 12),

              // Color Palette Cards
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildColorCard(context, 'Primary', theme.colorScheme.primary),
                  _buildColorCard(context, 'Secondary', theme.colorScheme.secondary),
                  _buildColorCard(context, 'Surface', theme.colorScheme.surface),
                  _buildColorCard(context, 'Background', theme.colorScheme.background),
                  _buildColorCard(context, 'Success', customColors.successColor!),
                  _buildColorCard(context, 'Warning', customColors.warningColor!),
                ],
              ),
              const SizedBox(height: 24),

              // UI Components Demo
              ThemedText(
                'UI Components',
                type: TextType.headline2,
              ),
              const SizedBox(height: 12),

              // Buttons Demo
              const ThemedText(
                'Buttons',
                type: TextType.subtitle,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ThemedButton(
                    text: 'Primary',
                    onPressed: () {},
                    isPrimary: true,
                  ),
                  ThemedButton(
                    text: 'Secondary',
                    onPressed: () {},
                    isPrimary: false,
                  ),
                  GradientButton(
                    text: 'Gradient',
                    onPressed: () {},
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Cards Demo
              const ThemedText(
                'Cards',
                type: TextType.subtitle,
              ),
              const SizedBox(height: 8),
              Column(
                children: [
                  ThemedCard(
                    title: 'Sample Card',
                    subtitle: 'This is a themed card component',
                    icon: const Icon(Icons.card_giftcard, color: Colors.white),
                    onTap: () {},
                  ),
                  StatusCard(
                    title: 'Status',
                    value: 'Active',
                    statusColor: customColors.successColor!,
                    statusIcon: Icons.check_circle,
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Typography Demo
              const ThemedText(
                'Typography',
                type: TextType.subtitle,
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const ThemedText('Headline 1', type: TextType.caption),
                      ThemedText('Dark Theme Showcase', type: TextType.headline1),
                      const SizedBox(height: 8),
                      const ThemedText('Headline 2', type: TextType.caption),
                      ThemedText('Beautiful UI Components', type: TextType.headline2),
                      const SizedBox(height: 8),
                      const ThemedText('Headline 3', type: TextType.caption),
                      ThemedText('Customizable Themes', type: TextType.headline3),
                      const SizedBox(height: 8),
                      const ThemedText('Subtitle', type: TextType.caption),
                      ThemedText('Explore different dark themes', type: TextType.subtitle),
                      const SizedBox(height: 8),
                      const ThemedText('Body', type: TextType.caption),
                      ThemedText('This is the main body text style used throughout the app.', type: TextType.body),
                      const SizedBox(height: 8),
                      const ThemedText('Caption', type: TextType.caption),
                      ThemedText('Small text for captions and secondary information.', type: TextType.caption),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          themeManager.cycleTheme();
        },
        tooltip: 'Cycle Theme',
        child: const Icon(Icons.palette),
      ),
    );
  }

  Widget _buildColorCard(BuildContext context, String label, Color color) {
    return SizedBox(
      width: 100,
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 5,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          ThemedText(
            label,
            type: TextType.caption,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  String _getCurrentThemeName(ThemeData theme) {
    if (theme == AppColorThemes.midnightOcean) {
      return AppConstants.theme1;
    } else if (theme == AppColorThemes.deepForest) {
      return AppConstants.theme2;
    } else if (theme == AppColorThemes.royalVelvet) {
      return AppConstants.theme3;
    } else if (theme == AppColorThemes.mysticPurple) {
      return AppConstants.theme4;
    } else if (theme == AppColorThemes.carbonFiber) {
      return AppConstants.theme5;
    }
    return 'Unknown Theme';
  }
}

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const ThemedText('Settings', type: TextType.headline3),
      ),
      body: const Padding(
        padding: EdgeInsets.all(16),
        child: ThemeSelectionSection(),
      ),
    );
  }
}