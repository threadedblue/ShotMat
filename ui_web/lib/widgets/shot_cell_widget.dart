import 'package:flutter/material.dart';
import '../models/shot.dart';

enum ShotColumn {
  number,
  input,
  mlxArgs,
  output,
  run,
}

class ShotCellWidget extends StatelessWidget {
  final bool isHeader;
  final ShotColumn column;
  final Shot? shot;
  final VoidCallback? onRun;

  const ShotCellWidget.header({
    super.key,
    required this.column,
  })  : isHeader = true,
        shot = null,
        onRun = null;

  const ShotCellWidget.data({
    super.key,
    required this.column,
    required this.shot,
    this.onRun,
  }) : isHeader = false;

  String _headerLabel() {
    switch (column) {
      case ShotColumn.number:
        return 'Shot No.';
      case ShotColumn.input:
        return 'Input';
      case ShotColumn.mlxArgs:
        return 'MLX Args';
      case ShotColumn.output:
        return 'Output';
      case ShotColumn.run:
        return 'Run';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isHeader) {
      return Card(
        color: Colors.blueGrey.shade800,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
        ),
        child: Center(
          child: Text(
            _headerLabel(),
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final currentShot = shot!;
    Widget child;

    switch (column) {
      case ShotColumn.number:
        child = Text(
          currentShot.number.toString(),
          style: const TextStyle(fontWeight: FontWeight.w600),
          textAlign: TextAlign.center,
        );
        break;
      case ShotColumn.input:
        child = Text(
          currentShot.input,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        );
        break;
      case ShotColumn.mlxArgs:
        child = Text(
          currentShot.mlxArgs,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        );
        break;
      case ShotColumn.output:
        child = Text(
          currentShot.output,
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        );
        break;
      case ShotColumn.run:
        child = Center(
          child: ElevatedButton(
            onPressed: onRun,
            child: const Text('Run'),
          ),
        );
        break;
    }

    return Card(
      color: Colors.blueGrey.shade900,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(6),
      ),
      child: Padding(
        padding: const EdgeInsets.all(6.0),
        child: child,
      ),
    );
  }
}
