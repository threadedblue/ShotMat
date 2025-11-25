class ShotEvent {
  final String shotId;
  final String generator;
  final String prompt;
  final String nPrompt;
  final String input;
  final String output;

  ShotEvent({
    required this.shotId,
    required this.generator,
    required this.prompt,
    required this.nPrompt,
    required this.input,
    required this.output,
  });

  factory ShotEvent.fromJson(Map<String, dynamic> json) {
    return ShotEvent(
      shotId: json['shot_id'] ?? '',
      generator: json['generator'] ?? '',
      prompt: json['prompt'] ?? '',
      nPrompt: json['n_prompt'] ?? '',
      input: json['input'] ?? '',
      output: json['output'] ?? '',
    );
  }
}
