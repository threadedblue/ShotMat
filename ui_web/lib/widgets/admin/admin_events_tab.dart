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
