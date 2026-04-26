import 'dart:io';
import 'dart:convert';

/// Assignment data model
class Assignment {
  final int id;
  final String title;
  final String content;
  final String sender;
  final String date;
  final bool completed;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  Assignment({
    required this.id,
    required this.title,
    required this.content,
    required this.sender,
    required this.date,
    this.completed = false,
    this.status = 'pending',
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  Assignment copyWith({
    int? id,
    String? title,
    String? content,
    String? sender,
    String? date,
    bool? completed,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Assignment(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      sender: sender ?? this.sender,
      date: date ?? this.date,
      completed: completed ?? this.completed,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'sender': sender,
      'date': date,
      'completed': completed,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  factory Assignment.fromJson(Map<String, dynamic> json) {
    return Assignment(
      id: json['id'] as int,
      title: json['title'] as String,
      content: json['content'] as String,
      sender: json['sender'] as String,
      date: json['date'] as String,
      completed: json['completed'] as bool? ?? false,
      status: json['status'] as String? ?? 'pending',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now(),
    );
  }
}

/// Database service for local persistence
class DatabaseService {
  static DatabaseService? _instance;
  late String _dbPath;
  late File _dbFile;
  late File _backupFile;
  List<Assignment> _assignments = [];
  int _nextId = 1;
  bool _initialized = false;

  DatabaseService._();

  static DatabaseService get instance {
    _instance ??= DatabaseService._();
    return _instance!;
  }

  /// Initialize database with custom path
  Future<void> initialize({String? dbPath}) async {
    if (_initialized) return;

    _dbPath = dbPath ?? 'data/assignments.db';
    _dbFile = File(_dbPath);
    _backupFile = File(_dbPath.replaceAll('.db', '_backup.json'));

    // Ensure directory exists
    final dir = Directory.fromUri(_dbFile.uri);
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }

    // Load existing data or create new
    if (await _dbFile.exists()) {
      await _loadFromDb();
    } else {
      await _createNewDb();
    }

    _initialized = true;
    print('[Database] Initialized at: $_dbPath');
  }

  Future<void> _loadFromDb() async {
    try {
      final content = await _dbFile.readAsString();
      final data = jsonDecode(content) as List;
      _assignments = data.map((e) => Assignment.fromJson(e)).toList();
      if (_assignments.isNotEmpty) {
        _nextId =
            _assignments.map((e) => e.id).reduce((a, b) => a > b ? a : b) + 1;
      }
    } catch (e) {
      print('[Database] Error loading: $e');
      await _createNewDb();
    }
  }

  Future<void> _createNewDb() async {
    _assignments = [];
    _nextId = 1;
    await _save();
  }

  Future<void> _save() async {
    try {
      final data = _assignments.map((e) => e.toJson()).toList();
      await _dbFile.writeAsString(jsonEncode(data));

      // Also save JSON backup
      await _backupFile.writeAsString(jsonEncode(data));
    } catch (e) {
      print('[Database] Error saving: $e');
    }
  }

  /// Get all assignments
  List<Assignment> getAll() {
    return List.unmodifiable(_assignments);
  }

  /// Get pending assignments
  List<Assignment> getPending() {
    return _assignments.where((e) => !e.completed).toList();
  }

  /// Get completed assignments
  List<Assignment> getCompleted() {
    return _assignments.where((e) => e.completed).toList();
  }

  /// Add new assignment
  Assignment addAssignment(String title, String content, String sender) {
    final assignment = Assignment(
      id: _nextId++,
      title: title,
      content: content,
      sender: sender,
      date: DateTime.now().toIso8601String().split('T')[0],
    );
    _assignments.add(assignment);
    _save();
    return assignment;
  }

  /// Toggle assignment completion status
  Assignment toggleComplete(int id) {
    final index = _assignments.indexWhere((e) => e.id == id);
    if (index == -1) throw Exception('Assignment not found: $id');

    final assignment = _assignments[index];
    final updated = assignment.copyWith(
      completed: !assignment.completed,
      status: !assignment.completed ? 'completed' : 'pending',
      updatedAt: DateTime.now(),
    );
    _assignments[index] = updated;
    _save();
    return updated;
  }

  /// Delete assignment
  void deleteAssignment(int id) {
    _assignments.removeWhere((e) => e.id == id);
    _save();
  }

  /// Get statistics
  Map<String, int> getStats() {
    final total = _assignments.length;
    final pending = _assignments.where((e) => !e.completed).length;
    final completed = _assignments.where((e) => e.completed).length;
    return {'total': total, 'pending': pending, 'completed': completed};
  }

  /// Close database connection
  Future<void> close() async {
    await _save();
    _initialized = false;
  }
}
