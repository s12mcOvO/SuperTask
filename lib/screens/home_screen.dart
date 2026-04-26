import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/database_service.dart';
import '../core/ocr_service.dart';
import '../core/llm_service.dart';

/// Home screen with tab navigation
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SuperTask - 智能任务管理系统'),
        centerTitle: true,
        elevation: 0,
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: const [TeacherTab(), StudentTab(), StatsTab()],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt),
            label: '教师端',
          ),
          NavigationDestination(
            icon: Icon(Icons.checklist_outlined),
            selectedIcon: Icon(Icons.checklist),
            label: '学生端',
          ),
          NavigationDestination(
            icon: Icon(Icons.bar_chart_outlined),
            selectedIcon: Icon(Icons.bar_chart),
            label: '统计',
          ),
        ],
      ),
    );
  }
}

/// Teacher tab for adding assignments
class TeacherTab extends StatelessWidget {
  const TeacherTab({super.key});

  @override
  Widget build(BuildContext context) {
    final ocrService = context.read<OcrService>();
    final dbService = context.read<DatabaseService>();
    final llmService = context.read<LlmService>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Icon(Icons.school, size: 48),
                  const SizedBox(height: 8),
                  Text('教师端', style: Theme.of(context).textTheme.headlineSmall),
                  const Text('拍照识别白板内容并发送任务'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // OCR Capture Button
          FilledButton.icon(
            onPressed: () async {
              // Show loading
              ScaffoldMessenger.of(
                context,
              ).showSnackBar(const SnackBar(content: Text('正在识别...')));

              // Perform OCR
              final result = await ocrService.recognizeText('mock_path');

              if (result.code == 0) {
                // Generate title and optimize
                final titleResult = await llmService.generateTitle(result.text);
                final optimizeResult = await llmService.optimizeText(
                  result.text,
                );

                // Add to database
                dbService.addAssignment(
                  titleResult.text,
                  optimizeResult.text,
                  '教师',
                );

                if (context.mounted) {
                  ScaffoldMessenger.of(
                    context,
                  ).showSnackBar(const SnackBar(content: Text('任务已发送！')));
                }
              }
            },
            icon: const Icon(Icons.camera_alt),
            label: const Text('📷 拍照识别白板'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 16),

          // Manual input
          OutlinedButton.icon(
            onPressed: () => _showManualInputDialog(context, dbService),
            icon: const Icon(Icons.edit),
            label: const Text('手动输入任务'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 24),

          // Sent tasks header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('已发送任务', style: Theme.of(context).textTheme.titleMedium),
              TextButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('刷新'),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Task list
          Consumer<DatabaseService>(
            builder: (context, db, _) {
              final assignments = db.getAll();

              if (assignments.isEmpty) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(
                          Icons.inbox_outlined,
                          size: 48,
                          color: Colors.grey,
                        ),
                        SizedBox(height: 8),
                        Text('暂无已发送任务', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                );
              }

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: assignments.length,
                itemBuilder: (context, index) {
                  final assignment =
                      assignments[assignments.length - 1 - index];
                  return Card(
                    child: ListTile(
                      leading: Icon(
                        assignment.completed
                            ? Icons.check_circle
                            : Icons.radio_button_unchecked,
                        color: assignment.completed
                            ? Colors.green
                            : Colors.orange,
                      ),
                      title: Text(assignment.title),
                      subtitle: Text(
                        '${assignment.date} | ${assignment.sender}',
                      ),
                      trailing: assignment.completed
                          ? const Chip(label: Text('已完成'))
                          : const Chip(
                              label: Text('待完成'),
                              backgroundColor: Colors.orange,
                            ),
                    ),
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }

  Future<void> _showManualInputDialog(
    BuildContext context,
    DatabaseService db,
  ) async {
    final titleController = TextEditingController();
    final contentController = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('手动输入任务'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(
                labelText: '标题',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: contentController,
              decoration: const InputDecoration(
                labelText: '内容',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('发送'),
          ),
        ],
      ),
    );

    if (result == true && titleController.text.isNotEmpty) {
      db.addAssignment(titleController.text, contentController.text, '教师');

      if (context.mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('任务已发送！')));
      }
    }
  }
}

/// Student tab for viewing tasks
class StudentTab extends StatelessWidget {
  const StudentTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<DatabaseService>(
      builder: (context, db, _) {
        final assignments = db.getAll();
        final pending = assignments.where((a) => !a.completed).toList();
        final completed = assignments.where((a) => a.completed).toList();

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Stats cards
            Row(
              children: [
                Expanded(
                  child: Card(
                    color: Colors.orange.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Text(
                            '${pending.length}',
                            style: Theme.of(context).textTheme.headlineMedium
                                ?.copyWith(color: Colors.orange),
                          ),
                          const Text(
                            '待完成',
                            style: TextStyle(color: Colors.orange),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Card(
                    color: Colors.green.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Text(
                            '${completed.length}',
                            style: Theme.of(context).textTheme.headlineMedium
                                ?.copyWith(color: Colors.green),
                          ),
                          const Text(
                            '已完成',
                            style: TextStyle(color: Colors.green),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Task list
            Text('任务列表', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),

            if (assignments.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Icon(Icons.inbox_outlined, size: 48, color: Colors.grey),
                      SizedBox(height: 8),
                      Text('暂无任务', style: TextStyle(color: Colors.grey)),
                    ],
                  ),
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: assignments.length,
                itemBuilder: (context, index) {
                  final assignment =
                      assignments[assignments.length - 1 - index];
                  return Card(
                    child: CheckboxListTile(
                      value: assignment.completed,
                      onChanged: (value) {
                        db.toggleComplete(assignment.id);
                      },
                      title: Text(
                        assignment.title,
                        style: TextStyle(
                          decoration: assignment.completed
                              ? TextDecoration.lineThrough
                              : null,
                        ),
                      ),
                      subtitle: Text(
                        '${assignment.date} | ${assignment.content.length > 30 ? '${assignment.content.substring(0, 30)}...' : assignment.content}',
                      ),
                      secondary: IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () {
                          db.deleteAssignment(assignment.id);
                        },
                      ),
                    ),
                  );
                },
              ),
          ],
        );
      },
    );
  }
}

/// Statistics tab
class StatsTab extends StatelessWidget {
  const StatsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<DatabaseService>(
      builder: (context, db, _) {
        final stats = db.getStats();
        final total = stats['total'] ?? 0;
        final pending = stats['pending'] ?? 0;
        final completed = stats['completed'] ?? 0;
        final rate = total > 0 ? (completed / total * 100).round() : 0;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Main stat card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Text(
                        '$rate%',
                        style: Theme.of(context).textTheme.displayLarge
                            ?.copyWith(
                              color: Theme.of(context).primaryColor,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const Text('完成率'),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _StatItem(
                            label: '总数',
                            value: '$total',
                            color: Colors.blue,
                          ),
                          _StatItem(
                            label: '待完成',
                            value: '$pending',
                            color: Colors.orange,
                          ),
                          _StatItem(
                            label: '已完成',
                            value: '$completed',
                            color: Colors.green,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Progress indicator
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('进度'),
                      const SizedBox(height: 16),
                      LinearProgressIndicator(
                        value: total > 0 ? completed / total : 0,
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '$completed / $total 任务已完成',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(label, style: TextStyle(color: color)),
      ],
    );
  }
}
