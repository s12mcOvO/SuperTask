/// OCR service result
class OcrResult {
  final int code;
  final String message;
  final String text;
  final List<String> words;

  OcrResult({
    required this.code,
    required this.message,
    required this.text,
    required this.words,
  });
}

/// OCR service for text recognition
class OcrService {
  static OcrService? _instance;
  String _provider = 'mock';

  OcrService._();

  static OcrService get instance {
    _instance ??= OcrService._();
    return _instance!;
  }

  /// Recognize text from image path
  /// Currently returns mock results for demonstration
  Future<OcrResult> recognizeText(String imagePath) async {
    // Simulate processing delay
    await Future.delayed(const Duration(milliseconds: 500));

    // Mock OCR results
    final samples = [
      '数学作业\n1. 解方程: x²-5x+6=0\n2. 计算三角形面积\n3. 证明勾股定理',
      '英语作业\n1. 背诵课文 Unit 3\n2. 翻译练习 p56-58',
      '物理作业\n1. 完成练习册P45-48\n2. 实验报告：摩擦力实验',
      '化学作业\n1. 配平方程式\n2. 计算摩尔质量',
    ];

    final text = samples[DateTime.now().millisecond % samples.length];
    final words = text.split('\n');

    return OcrResult(code: 0, message: '模拟识别成功', text: text, words: words);
  }

  String get provider => _provider;
}
