import 'package:flutter/material.dart';
import 'board/shot_grid_page.dart';
import 'admin/admin_page.dart';
import '../models/shot_project.dart';

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;
  ShotProject? _currentProject; // Placeholder for global project state

  final List<Widget> _pages = [
    const ShotGridPage(), // Existing page for the "Board"
    const AdminPage(),
  ];

  @override
  void initState() {
    super.initState();
    // TODO: Replace with actual project loading and selection logic
    _currentProject = ShotProject(name: "Default Project", details: {});
  }

  void _onDestinationSelected(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final bool useRail = constraints.maxWidth >= 640;
        return Scaffold(
          appBar: AppBar(
            title: Text(_currentProject?.name ?? "ShotMat"),
            actions: [
              // TODO: Replace with a proper project selector dropdown/dialog
              Padding(
                padding: const EdgeInsets.only(right: 16.0),
                child: Center(child: Text('Project: ${_currentProject?.name ?? 'None'}')),
              ),
            ],
          ),
          body: Row(
            children: [
              if (useRail)
                NavigationRail(
                  selectedIndex: _selectedIndex,
                  onDestinationSelected: _onDestinationSelected,
                  labelType: NavigationRailLabelType.all,
                  destinations: const [
                    NavigationRailDestination(
                      icon: Icon(Icons.grid_on_outlined),
                      selectedIcon: Icon(Icons.grid_on),
                      label: Text('Board'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.admin_panel_settings_outlined),
                      selectedIcon: Icon(Icons.admin_panel_settings),
                      label: Text('Admin'),
                    ),
                  ],
                ),
              Expanded(
                child: IndexedStack(
                  index: _selectedIndex,
                  children: _pages,
                ),
              ),
            ],
          ),
          bottomNavigationBar: useRail
              ? null
              : BottomNavigationBar(
                  currentIndex: _selectedIndex,
                  onTap: _onDestinationSelected,
                  items: const [
                    BottomNavigationBarItem(
                      icon: Icon(Icons.grid_on_outlined),
                      activeIcon: Icon(Icons.grid_on),
                      label: 'Board',
                    ),
                    BottomNavigationBarItem(
                      icon: Icon(Icons.admin_panel_settings_outlined),
                      activeIcon: Icon(Icons.admin_panel_settings),
                      label: 'Admin',
                    ),
                  ],
                ),
        );
      },
    );
  }
}
