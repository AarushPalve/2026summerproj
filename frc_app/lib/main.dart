// Main Application Entry Point
// FRC Strategy and Forecasting Application
// Spec: 01_system_architecture.md

import 'package:flutter/material.dart';
import 'core/database.dart';
import 'data/data_repository.dart';
import 'workers/worker_manager.dart';
import 'ml/onnx_inference.dart';
import 'data/sync_manager.dart';
import 'utils/app_dependencies.dart';

void main() async {
  // Initialize Flutter
  WidgetsFlutterBinding.ensureInitialized();

  // Set up dependency injection
  final dependencies = AppDependencies();
  await dependencies.initialize();

  // Run the app
  runApp(FRCStrategyApp(dependencies: dependencies));
}

class FRCStrategyApp extends StatelessWidget {
  final AppDependencies dependencies;

  const FRCStrategyApp({Key? key, required this.dependencies}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FRC Strategy App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MainScreen(dependencies: dependencies),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainScreen extends StatefulWidget {
  final AppDependencies dependencies;

  const MainScreen({Key? key, required this.dependencies}) : super(key: key);

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  bool _isSyncing = false;
  String _syncStatus = 'Ready to sync';
  double _syncProgress = 0.0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FRC Strategy App'),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: _isSyncing ? null : _performSync,
            tooltip: 'Sync Data',
          ),
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: _navigateToAnalytics,
            tooltip: 'Analytics',
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'FRC Strategy & Forecasting',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Text(_syncStatus, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 10),
            if (_isSyncing) ...[
              LinearProgressIndicator(value: _syncProgress),
              const SizedBox(height: 10),
              Text('${(_syncProgress * 100).toStringAsFixed(1)}%'),
            ],
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _testDatabase,
              child: const Text('Test Database'),
            ),
            ElevatedButton(
              onPressed: _testMLInference,
              child: const Text('Test ML Inference'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _performSync() async {
    setState(() {
      _isSyncing = true;
      _syncStatus = 'Starting sync...';
      _syncProgress = 0.0;
    });

    try {
      // Perform synchronization
      final syncResult = await widget.dependencies.syncManager.performSync();

      setState(() {
        _syncStatus = syncResult.message;
        _syncProgress = 1.0;
      });

      // Calculate metrics after sync
      await widget.dependencies.syncManager.calculateMetricsAfterSync();

      // Run predictions
      await widget.dependencies.syncManager.runPredictionsAfterSync();

      setState(() {
        _syncStatus = 'Sync and analysis complete!';
      });
    } catch (e) {
      setState(() {
        _syncStatus = 'Sync failed: ${e.toString()}';
        _syncProgress = 0.0;
      });
    } finally {
      setState(() {
        _isSyncing = false;
      });
    }
  }

  Future<void> _testDatabase() async {
    try {
      // Test database operations
      final event = Event(
        eventId: '2026test',
        name: 'Test Event',
        startDate: '2026-01-01',
        endDate: '2026-01-03',
        year: 2026,
      );

      await widget.dependencies.repository.insertEvent(event);

      final events = await widget.dependencies.repository.getEvents();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Database test successful! Found ${events.length} events')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Database test failed: ${e.toString()}')),
      );
    }
  }

  Future<void> _testMLInference() async {
    try {
      // Test ML inference
      final result = await widget.dependencies.onnxEngine.runInference(
        'test_model',
        List.filled(10, 0.5), // Test input vector
      );

      if (result['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('ML Inference successful! Output: ${result['output']}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('ML Inference failed: ${result['error']}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('ML test failed: ${e.toString()}')),
      );
    }
  }

  void _navigateToAnalytics() {
    // Navigate to analytics screen
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AnalyticsScreen(dependencies: widget.dependencies),
      ),
    );
  }
}

class AnalyticsScreen extends StatelessWidget {
  final AppDependencies dependencies;

  const AnalyticsScreen({Key? key, required this.dependencies}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics'),
      ),
      body: FutureBuilder<List<Event>>(
        future: dependencies.repository.getEvents(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final events = snapshot.data ?? [];

          return ListView.builder(
            itemCount: events.length,
            itemBuilder: (context, index) {
              final event = events[index];
              return ListTile(
                title: Text(event.name),
                subtitle: Text('${event.startDate} to ${event.endDate}'),
                onTap: () => _showEventDetails(context, event),
              );
            },
          );
        },
      ),
    );
  }

  void _showEventDetails(BuildContext context, Event event) {
    // Show event details
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(event.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Event ID: ${event.eventId}'),
            Text('Year: ${event.year}'),
            Text('Location: ${event.location ?? 'N/A'}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}