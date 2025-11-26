import 'package:ui_web/models/shot.dart';

class ShotRow {
  ShotRow({
    this.shotNo = 1,
    this.input = '',
    this.mlxArgs = '',
    this.output = '',
  });

  int shotNo;
  String input;
  String mlxArgs;
  String output;

  /// Creates a mutable [ShotRow] from an immutable [Shot].
  /// This is useful for populating a form for editing.
  factory ShotRow.fromShot(Shot shot) {
    return ShotRow(
      shotNo: shot.number,
      input: shot.input,
      mlxArgs: shot.mlxArgs,
      output: shot.output,
    );
  }

  /// Converts this mutable [ShotRow] into an immutable [Shot].
  /// This is useful when saving the data from a form.
  Shot toShot() => Shot(number: shotNo, input: input, mlxArgs: mlxArgs, output: output);
}