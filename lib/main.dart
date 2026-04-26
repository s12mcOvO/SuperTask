import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/database_service.dart';
import 'core/ocr_service.dart';
import 'core/llm_service.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize database
  await DatabaseService.instance.initialize();

  runApp(const SuperTaskApp());
}

/// Main application widget
class SuperTaskApp extends StatelessWidget {
  const SuperTaskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<DatabaseService>.value(value: DatabaseService.instance),
        Provider<OcrService>(create: (_) => OcrService.instance),
        Provider<LlmService>(create: (_) => LlmService.instance),
      ],
      child: MaterialApp(
        title: 'SuperTask - 智能任务管理系统',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF4A90E2),
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          fontFamily: 'Roboto',
        ),
        darkTheme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF4A90E2),
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
          fontFamily: 'Roboto',
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
