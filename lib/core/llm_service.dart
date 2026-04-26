/// LLM service result
class LlmResult {
  final int code;
  final String message;
  final String text;
  final List<Map<String, dynamic>> tasks;

  LlmResult({
    required this.code,
    required this.message,
    required this.text,
    this.tasks = const [],
  });
}

/// LLM service for text optimization and task extraction
class LlmService {
  static LlmService? _instance;
  String _provider = 'mock';

  LlmService._();

  static LlmService get instance {
    _instance ??= LlmService._();
    return _instance!;
  }

  /// Optimize text using mock implementation
  Future<LlmResult> optimizeText(String text) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return LlmResult(code: 0, message: '优化成功', text: text);
  }

  /// Generate title from content
  Future<LlmResult> generateTitle(String content) async {
    await Future.delayed(const Duration(milliseconds: 200));

    // Simple mock title extraction
    String title = '新任务';
    final lines = content.split('\n');
    if (lines.isNotEmpty) {
      final firstLine = lines.first.trim();
      if (firstLine.isNotEmpty) {
        title = firstLine.length > 20
            ? '${firstLine.substring(0, 20)}...'
            : firstLine;
      }
    }

    return LlmResult(code: 0, message: '标题生成成功', text: title);
  }

  /// Extract tasks from content
  Future<LlmResult> extractTasks(String content) async {
    await Future.delayed(const Duration(milliseconds: 300));

    final lines = content.split('\n');
    final tasks = <Map<String, dynamic>>[];

    for (final line in lines) {
      final trimmed = line.trim();
      if (trimmed.isNotEmpty && trimmed.startsWith(RegExp(r'^\d+[\.\:]'))) {
        tasks.add({'content': trimmed, 'completed': false});
      }
    }

    if (tasks.isEmpty) {
      tasks.add({'content': content, 'completed': false});
    }

    return LlmResult(code: 0, message: '任务提取成功', text: content, tasks: tasks);
  }

  String get provider => _provider;
}
