// interactive_mask_image.dart
import 'package:flutter/material.dart';

/// Widget (1):
/// Displays the original image with a transparent interactive mask over it.
/// - User draws a mask by dragging.
/// - Has a clear button to reset the mask.
/// - Taps anywhere toggle between normal and expanded (fullscreen-ish) view.
/// - Notifies parent whenever mask changes.
class InteractiveMaskImage extends StatefulWidget {
  final ImageProvider image;
  final ValueChanged<List<Offset>> onMaskChanged;

  const InteractiveMaskImage({
    super.key,
    required this.image,
    required this.onMaskChanged,
  });

  @override
  State<InteractiveMaskImage> createState() => _InteractiveMaskImageState();
}

class _InteractiveMaskImageState extends State<InteractiveMaskImage> {
  final List<Offset> _maskPoints = [];
  bool _isExpanded = false;

  void _addPoint(Offset point) {
    setState(() {
      _maskPoints.add(point);
    });
    widget.onMaskChanged(List.unmodifiable(_maskPoints));
  }

  void _clearMask() {
    setState(() {
      _maskPoints.clear();
    });
    widget.onMaskChanged(List.unmodifiable(_maskPoints));
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });
  }

  @override
  Widget build(BuildContext context) {
    final content = AspectRatio(
      aspectRatio: 1.0, // adjust if you want non-square
      child: LayoutBuilder(
        builder: (context, constraints) {
          return GestureDetector(
            onPanStart: (details) => _addPoint(details.localPosition),
            onPanUpdate: (details) => _addPoint(details.localPosition),
            onTap: _toggleExpanded,
            child: Stack(
              fit: StackFit.expand,
              children: [
                // Base image
                Image(
                  image: widget.image,
                  fit: BoxFit.cover,
                ),
                // Mask overlay
                CustomPaint(
                  painter: _MaskPainter(
                    points: _maskPoints,
                    color: Colors.red.withOpacity(0.35),
                  ),
                ),
                // Clear button
                Positioned(
                  top: 8,
                  right: 8,
                  child: Material(
                    color: Colors.black26,
                    shape: const CircleBorder(),
                    child: IconButton(
                      icon: const Icon(
                        Icons.clear,
                        color: Colors.white,
                        size: 20,
                      ),
                      tooltip: 'Clear mask',
                      onPressed: _clearMask,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );

    if (!_isExpanded) {
      // Normal inline version
      return ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: content,
      );
    }

    // Expanded version in a popup-style overlay
    return Stack(
      children: [
        // Dim background
        Positioned.fill(
          child: GestureDetector(
            onTap: _toggleExpanded,
            child: Container(
              color: Colors.black54,
            ),
          ),
        ),
        // Centered enlarged content
        Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: 800,
              maxHeight: 800,
            ),
            child: Material(
              borderRadius: BorderRadius.circular(16),
              clipBehavior: Clip.antiAlias,
              child: content,
            ),
          ),
        ),
      ],
    );
  }
}

class _MaskPainter extends CustomPainter {
  final List<Offset> points;
  final Color color;

  _MaskPainter({required this.points, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    if (points.isEmpty) return;

    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    // Very simple: treat all points as a single blob/path.
    // You can replace this with something more sophisticated if needed.
    final path = Path();
    if (points.length > 2) {
      path.moveTo(points.first.dx, points.first.dy);
      for (final p in points.skip(1)) {
        path.lineTo(p.dx, p.dy);
      }
      path.close();
      canvas.drawPath(path, paint);
    } else {
      for (final p in points) {
        canvas.drawCircle(p, 4.0, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _MaskPainter oldDelegate) =>
      oldDelegate.points != points || oldDelegate.color != color;
}
