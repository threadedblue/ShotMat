import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/shot_project.dart';
import '../models/shot_event.dart';

// NOTE: This is a placeholder API client. The base URL and error handling
// should be configured for your specific environment.
class ApiClient {
  final String _baseUrl = "http://127.0.0.1:8000"; // Adjust to your API address

  Future<List<ShotProject>> getProjects() async {
    // TODO: Implement actual API call to fetch projects
    // For now, returning mock data.
    // final response = await http.get(Uri.parse('$_baseUrl/admin/projects'));
    // if (response.statusCode == 200) {
    //   final List<dynamic> data = json.decode(response.body);
    //   return data.map((json) => ShotProject.fromJson(json)).toList();
    // } else {
    //   throw Exception('Failed to load projects');
    // }
    await Future.delayed(const Duration(seconds: 1));
    return [
      ShotProject(name: "Project Alpha", details: {}),
      ShotProject(name: "Project Beta", details: {}),
    ];
  }

  Future<List<ShotEvent>> getShotEvents() async {
    final response = await http.get(Uri.parse('$_baseUrl/admin/events'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      final List<dynamic> eventsData = data['events'] ?? [];
      return eventsData.map((json) => ShotEvent.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load shot events');
    }
  }

  Future<ShotProject> createProject(String name) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/admin/projects'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'project_name': name}),
    );

    if (response.statusCode == 201) {
      return ShotProject.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create project');
    }
  }
}