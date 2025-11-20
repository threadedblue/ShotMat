import 'package:flutter/material.dart';
import 'package:ui_web/widgets/shot_grid.dart'; // Import the ShotGrid widget

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ShotMat Workflow'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Theme.of(context).colorScheme.onPrimary,
      ),
      body: const ShotGrid(), // Display the ShotGrid widget here
    );
  }
}