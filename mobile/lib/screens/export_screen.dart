import 'package:flutter/material.dart';

class ExportScreen extends StatelessWidget {
  const ExportScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Export')),
      body: Center(
        child: Text('Export Screen'),
      ),
    );
  }
}
