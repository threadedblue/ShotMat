// segmentation_carousel.dart
import 'package:flutter/material.dart';

/// Simple model representing one segmentation result image.
/// You can add an ID or metadata as needed.
class SegmentationResult {
  final String id;
  final ImageProvider image;

  SegmentationResult({
    required this.id,
    required this.image,
  });
}

/// Widget (2):
/// Displays a carousel of segmentation results as thumbnails.
/// - Supports removing unwanted images.
/// - Clicking a thumbnail toggles an expanded view for that item.
/// - Parent owns the list; this widget calls onRemove(id) when user deletes.
class SegmentationCarousel extends StatefulWidget {
  final List<SegmentationResult> results;
  final ValueChanged<String> onRemove;

  const SegmentationCarousel({
    super.key,
    required this.results,
    required this.onRemove,
  });

  @override
  State<SegmentationCarousel> createState() => _SegmentationCarouselState();
}

class _SegmentationCarouselState extends State<SegmentationCarousel> {
  String? _expandedId;

  void _toggleExpanded(SegmentationResult result) {
    setState(() {
      if (_expandedId == result.id) {
        _expandedId = null;
      } else {
        _expandedId = result.id;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (widget.results.isEmpty) {
      return const SizedBox.shrink();
    }

    if (_expandedId != null) {
      final expandedResult = widget.results
          .firstWhere((r) => r.id == _expandedId, orElse: () => widget.results.first);

      return Stack(
        children: [
          // Dim background
          Positioned.fill(
            child: GestureDetector(
              onTap: () => _toggleExpanded(expandedResult),
              child: Container(color: Colors.black54),
            ),
          ),
          Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(
                maxWidth: 800,
                maxHeight: 800,
              ),
              child: Material(
                borderRadius: BorderRadius.circular(16),
                clipBehavior: Clip.antiAlias,
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: Image(
                        image: expandedResult.image,
                        fit: BoxFit.contain,
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Material(
                            color: Colors.black45,
                            shape: const CircleBorder(),
                            child: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.white),
                              tooltip: 'Delete image',
                              onPressed: () {
                                widget.onRemove(expandedResult.id);
                                setState(() {
                                  _expandedId = null;
                                });
                              },
                            ),
                          ),
                          const SizedBox(width: 8),
                          Material(
                            color: Colors.black45,
                            shape: const CircleBorder(),
                            child: IconButton(
                              icon: const Icon(Icons.close, color: Colors.white),
                              tooltip: 'Close',
                              onPressed: () => _toggleExpanded(expandedResult),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      );
    }

    // Normal thumbnail carousel
    return SizedBox(
      height: 120,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        itemCount: widget.results.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final result = widget.results[index];
          return GestureDetector(
            onTap: () => _toggleExpanded(result),
            child: Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: AspectRatio(
                    aspectRatio: 1.0,
                    child: Image(
                      image: result.image,
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                Positioned(
                  top: 4,
                  right: 4,
                  child: Material(
                    color: Colors.black54,
                    shape: const CircleBorder(),
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      onTap: () => widget.onRemove(result.id),
                      child: const Padding(
                        padding: EdgeInsets.all(4.0),
                        child: Icon(
                          Icons.delete,
                          color: Colors.white,
                          size: 18,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
