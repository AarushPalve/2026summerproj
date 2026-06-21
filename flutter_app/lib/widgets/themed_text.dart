import 'package:flutter/material.dart';

class ThemedText extends StatelessWidget {
  final String text;
  final TextType type;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;

  const ThemedText(
    this.text, {
    super.key,
    this.type = TextType.body,
    this.textAlign,
    this.maxLines,
    this.overflow,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    TextStyle style;

    switch (type) {
      case TextType.headline1:
        style = TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: colorScheme.onBackground,
        );
        break;
      case TextType.headline2:
        style = TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: colorScheme.onBackground,
        );
        break;
      case TextType.headline3:
        style = TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: colorScheme.onBackground,
        );
        break;
      case TextType.subtitle:
        style = TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: colorScheme.onBackground.withOpacity(0.8),
        );
        break;
      case TextType.body:
        style = TextStyle(
          fontSize: 16,
          color: colorScheme.onBackground,
        );
        break;
      case TextType.caption:
        style = TextStyle(
          fontSize: 12,
          color: colorScheme.onBackground.withOpacity(0.6),
        );
        break;
      case TextType.button:
        style = TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: colorScheme.onPrimary,
          letterSpacing: 1.2,
        );
        break;
    }

    return Text(
      text,
      style: style,
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}

enum TextType {
  headline1,
  headline2,
  headline3,
  subtitle,
  body,
  caption,
  button,
}