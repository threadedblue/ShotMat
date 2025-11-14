import 'package:flutter/material.dart';
import 'pages/home_page.dart';

void main() {
  runApp(const ShotMatWebApp());
}

class ShotMatWebApp extends StatelessWidget {
  const ShotMatWebApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ShotMat Web',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF020617), // near-slate
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF38BDF8), // cyan-ish accent
          brightness: Brightness.dark,
        ),
        textTheme: ThemeData.dark().textTheme.apply(
              fontFamily: 'Roboto',
            ),
      ),
      home: const HomePage(),
    );
  }
}
