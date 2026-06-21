import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_theme_app/theme/theme_manager.dart';
import 'package:flutter_theme_app/screens/home_screen.dart';
import 'package:flutter_theme_app/utils/constants.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeManager()),
      ],
      child: Consumer<ThemeManager>(
        builder: (context, themeManager, child) {
          return MaterialApp(
            title: AppConstants.appName,
            theme: themeManager.currentTheme.copyWith(
              extensions: [
                CustomThemeColors.forTheme(themeManager.currentTheme),
              ],
            ),
            home: const HomeScreen(),
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}