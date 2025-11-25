import 'package:flutter/material.dart';
import '../../api/api_client.dart';
import '../../models/shot_project.dart';

class AdminProjectsTab extends StatefulWidget {
  const AdminProjectsTab({super.key});

  @override
  State<AdminProjectsTab> createState() => _AdminProjectsTabState();
}

class _AdminProjectsTabState extends State<AdminProjectsTab> {
  final ApiClient _apiClient = ApiClient();
  late Future<List<ShotProject>> _projectsFuture;
  final TextEditingController _newProjectController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadProjects();
  }

  void _loadProjects() {
    setState(() {
      _projectsFuture = _apiClient.getProjects();
    });
  }

  Future<void> _showCreateProjectDialog() async {
    return showDialog<void>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Create New Project'),
          content: TextField(
            controller: _newProjectController,
            decoration: const InputDecoration(hintText: "Project Name"),
            autofocus: true,
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancel'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text('Create'),
              onPressed: () {
                _createProject();
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  void _createProject() async {
    if (_newProjectController.text.isEmpty) return;
    try {
      await _apiClient.createProject(_newProjectController.text);
      _newProjectController.clear();
      _loadProjects(); // Refresh the list
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Project created successfully')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to create project: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<List<ShotProject>>(
        future: _projectsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No projects found.'));
          }
          final projects = snapshot.data!;
          return ListView.builder(
            itemCount: projects.length,
            itemBuilder: (context, index) {
              final project = projects[index];
              return ListTile(
                leading: const Icon(Icons.folder),
                title: Text(project.name),
                // TODO: Add trailing buttons for update/delete actions
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showCreateProjectDialog,
        tooltip: 'Create Project',
        child: const Icon(Icons.add),
      ),
    );
  }

  @override
  void dispose() {
    _newProjectController.dispose();
    super.dispose();
  }
}

// lib/ui/admin/admin_events_tab.dart
import 'package:flutter/material.dart';
import '../../api/api_client.dart';
import '../../models/shot_event.dart';

class AdminEventsTab extends StatefulWidget {
  const AdminEventsTab({super.key});

  @override
  State<AdminEventsTab> createState() => _AdminEventsTabState();
}

class _AdminEventsTabState extends State<AdminEventsTab> {
  final ApiClient _apiClient = ApiClient();
  late Future<List<ShotEvent>> _eventsFuture;

  @override
  void initState() {
    super.initState();
    _loadEvents();
  }

  void _loadEvents() {
    setState(() {
      _eventsFuture = _apiClient.getShotEvents();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () async => _loadEvents(),
        child: FutureBuilder<List<ShotEvent>>(
          future: _eventsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Error: ${snapshot.error}'),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: _loadEvents,
                      child: const Text('Retry'),
                    )
                  ],
                ),
              );
            }
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return const Center(child: Text('No shot events found.'));
            }
            final events = snapshot.data!;
            return ListView.builder(
              itemCount: events.length,
              itemBuilder: (context, index) {
                final event = events[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: ListTile(
                    leading: const Icon(Icons.history_toggle_off),
                    title: Text(event.prompt, maxLines: 1, overflow: TextOverflow.ellipsis),
                    subtitle: Text('ID: ${event.shotId} | Gen: ${event.generator}'),
                    // TODO: Add onTap to show event details
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
