import 'package:flutter/material.dart';

// Placeholder for the existing ShotGridPage.
// This should be replaced with your actual implementation.
class ShotGridPage extends StatelessWidget {
  const ShotGridPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.view_quilt, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'Shot Grid Page',
            style: TextStyle(fontSize: 24, color: Colors.grey),
          ),
          Text(
            'This is where the existing shot grid UI will be displayed.',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

// lib/ui/admin/admin_page.dart
import 'package:flutter/material.dart';
import 'admin_projects_tab.dart';
import 'admin_events_tab.dart';

class AdminPage extends StatelessWidget {
  const AdminPage({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: false,
          toolbarHeight: 0, // Hide the app bar, tabs are the primary content
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.folder_copy), text: "Projects"),
              Tab(icon: Icon(Icons.history), text: "Events"),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            AdminProjectsTab(),
            AdminEventsTab(),
          ],
        ),
      ),
    );
  }
}
