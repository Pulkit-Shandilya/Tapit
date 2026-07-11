import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'theme_controller.dart';

void main() {
  runApp(const TapItApp());
}

class TapItApp extends StatelessWidget {
  const TapItApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: appThemeMode,
      builder: (context, themeMode, _) {
        return MaterialApp(
          title: 'TapIt',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF6C63FF),
              brightness: Brightness.light,
            ),
            useMaterial3: true,
            fontFamily: 'Roboto',
          ),
          darkTheme: ThemeData(
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF6C63FF),
              brightness: Brightness.dark,
            ),
            scaffoldBackgroundColor: const Color(0xFF0F1115),
            useMaterial3: true,
            fontFamily: 'Roboto',
          ),
          themeMode: themeMode,
          home: const HomeScreen(),
        );
      },
    );
  }
}
