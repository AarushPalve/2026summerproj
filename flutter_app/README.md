# Flutter Dark Theme Showcase

A Flutter application demonstrating 5 beautiful dark UI themes with theme switching capabilities.

## Features

- 5 distinct dark themes with complete color specifications
- Theme switching with persistence using SharedPreferences
- Custom theme extensions for additional colors
- Themed widgets (buttons, cards, text)
- Responsive UI with theme showcase

## Themes

1. **Midnight Ocean** - Deep navy and cyan theme
2. **Deep Forest** - Rich green forest theme  
3. **Royal Velvet** - Luxurious purple theme
4. **Mystic Purple** - Deep purple with blue undertones
5. **Carbon Fiber** - Modern dark gray/black theme

## Directory Structure

```
flutter_app/
├── lib/
│   ├── main.dart                  # Application entry point
│   ├── app.dart                    # Main app widget with providers
│   ├── theme/
│   │   ├── color_themes.dart       # 5 dark theme definitions
│   │   ├── theme_manager.dart       # Theme switching logic
│   │   └── theme_data.dart          # Custom theme extensions
│   ├── screens/
│   │   ├── home_screen.dart        # Main screen with theme showcase
│   │   └── settings_screen.dart     # Theme selection screen
│   ├── widgets/
│   │   ├── themed_button.dart      # Custom button widgets
│   │   ├── themed_card.dart        # Custom card widgets
│   │   └── themed_text.dart        # Typography components
│   └── utils/
│       └── constants.dart          # App constants
├── test/
│   └── theme_test.dart             # Theme tests
├── pubspec.yaml
└── README.md
```

## Getting Started

1. **Prerequisites**
   - Flutter SDK (>=3.0.0)
   - Dart SDK
   - Android Studio / VS Code (recommended)

2. **Installation**

   ```bash
   # Clone the repository
   git clone <repository-url>
   cd flutter_app

   # Get dependencies
   flutter pub get

   # Run the app
   flutter run
   ```

3. **Running Tests**

   ```bash
   flutter test
   ```

## Usage

### Theme Switching

The app provides two ways to switch themes:

1. **Cycle through themes**: Press the floating action button or the "Cycle Theme" button
2. **Select specific theme**: Go to Settings screen and tap on any theme card

### Theme Persistence

The selected theme is persisted using SharedPreferences and will be remembered across app restarts.

## Customization

### Adding New Themes

1. Add a new theme in `lib/theme/color_themes.dart`
2. Update the `getThemeById` method
3. Add theme name to `lib/utils/constants.dart`
4. Add custom colors in `CustomThemeColors.forTheme()` method

### Using Themed Widgets

```dart
// Themed Button
ThemedButton(
  text: 'Click Me',
  onPressed: () {},
  isPrimary: true,
)

// Gradient Button
GradientButton(
  text: 'Gradient',
  onPressed: () {},
)

// Themed Card
ThemedCard(
  title: 'Card Title',
  subtitle: 'Card subtitle',
  icon: Icon(Icons.star),
  onTap: () {},
)

// Themed Text
ThemedText(
  'Hello World',
  type: TextType.headline2,
)
```

## Dependencies

- `flutter`: SDK
- `provider`: State management
- `shared_preferences`: Theme persistence
- `cupertino_icons`: Cupertino icons

## Screenshots

![Home Screen](screenshots/home.png)
![Settings Screen](screenshots/settings.png)

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
