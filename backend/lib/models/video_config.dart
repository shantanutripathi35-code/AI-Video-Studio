class VideoConfig {
  final int targetDuration;
  final String aspectRatio;
  final bool captions;
  final bool removeSilence;
  final bool voiceEnhancement;

  VideoConfig({
    required this.targetDuration,
    required this.aspectRatio,
    required this.captions,
    required this.removeSilence,
    required this.voiceEnhancement,
  });

  factory VideoConfig.fromJson(Map<String, dynamic> json) {
    return VideoConfig(
      targetDuration: json['target_duration'] ?? 30,
      aspectRatio: json['aspect_ratio'] ?? '16:9',
      captions: json['captions'] ?? true,
      removeSilence: json['remove_silence'] ?? false,
      voiceEnhancement: json['voice_enhancement'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'target_duration': targetDuration,
      'aspect_ratio': aspectRatio,
      'captions': captions,
      'remove_silence': removeSilence,
      'voice_enhancement': voiceEnhancement,
    };
  }
}
