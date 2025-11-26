import 'package:flutter/material.dart';
import 'admin_events_tab.dart';
import 'admin_projects_tab.dart';

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
