import 'package:flutter/material.dart';
import '../models/shot_row.dart';

class ShotGrid extends StatefulWidget {
  const ShotGrid({super.key});

  @override
  State<ShotGrid> createState() => _ShotGridState();
}

class _ShotGridState extends State<ShotGrid> {
  final List<ShotRow> _rows = [
    ShotRow(shotNo: 1),
  ];

  void _addRowBelow(int index) {
    setState(() {
      final newShotNo = _rows.length + 1;
      _rows.insert(index + 1, ShotRow(shotNo: newShotNo));
    });
  }

  void _removeRow(int index) {
    if (_rows.length == 1) return; // keep at least one row
    setState(() {
      _rows.removeAt(index);
    });
  }

  void _runRow(int index) {
    final row = _rows[index];
    debugPrint('Running row ${row.shotNo}: input="${row.input}" mlx="${row.mlxArgs}"');
    // TODO: call your backend here
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header row (fixed)
        Container(
          color: Theme.of(context).colorScheme.onSurfaceVariant,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: const [
              SizedBox(width: 40, child: Text('#', style: TextStyle(fontWeight: FontWeight.bold))),
              Expanded(flex: 3, child: Text('Input', style: TextStyle(fontWeight: FontWeight.bold))),
              Expanded(flex: 2, child: Text('MLX Args', style: TextStyle(fontWeight: FontWeight.bold))),
              Expanded(flex: 3, child: Text('Output', style: TextStyle(fontWeight: FontWeight.bold))),
              SizedBox(width: 96, child: Text('Actions', style: TextStyle(fontWeight: FontWeight.bold))),
            ],
          ),
        ),
        const Divider(height: 0),

        // Scrollable rows
        Expanded(
          child: ListView.builder(
            itemCount: _rows.length,
            itemBuilder: (context, index) {
              final row = _rows[index];
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 40,
                      child: Text(row.shotNo.toString()),
                    ),
                    Expanded(
                      flex: 3,
                      child: TextField(
                        decoration: const InputDecoration(
                          isDense: true,
                          hintText: 'Script / prompt / instruction',
                        ),
                        onChanged: (v) => row.input = v,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      flex: 2,
                      child: TextField(
                        decoration: const InputDecoration(
                          isDense: true,
                          hintText: 'MLX args',
                        ),
                        onChanged: (v) => row.mlxArgs = v,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      flex: 3,
                      child: TextField(
                        decoration: const InputDecoration(
                          isDense: true,
                          hintText: 'Output (description / id)',
                        ),
                        onChanged: (v) => row.output = v,
                      ),
                    ),
                    const SizedBox(width: 4),
                    SizedBox(
                      width: 96,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.add),
                            tooltip: 'Add row below',
                            onPressed: () => _addRowBelow(index),
                          ),
                          IconButton(
                            icon: const Icon(Icons.remove),
                            tooltip: 'Remove row',
                            onPressed: () => _removeRow(index),
                          ),
                          IconButton(
                            icon: const Icon(Icons.play_arrow),
                            tooltip: 'Run row',
                            onPressed: () => _runRow(index),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
