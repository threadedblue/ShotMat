// lib/models/shot_project.dart
class ShotProject {
  final String name;
  final Map<String, dynamic> details;

  ShotProject({required this.name, required this.details});

  factory ShotProject.fromJson(Map<String, dynamic> json) {
    return ShotProject(
      name: json['name'] ?? 'Untitled Project',
      details: json,
    );
  }
}
