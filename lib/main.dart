import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const TapItApp());
}

class TapItApp extends StatelessWidget {
  const TapItApp({super.key});

  @override
  Widget build(BuildContext context) {
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
      home: const HomeScreen(),
    );
  }
}
