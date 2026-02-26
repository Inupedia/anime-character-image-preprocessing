"""Extract face bounding boxes from detection results."""

from typing import List, Tuple


def extract_face_boundaries(
    image_path: str,
    detection: List[Tuple[Tuple[float, float, float, float], str, float]],
    labels: List[str],
) -> List[Tuple[int, int, int, int]]:
    """Extract bounding box coordinates from detection results.

    Args:
        image_path: Path to the source image (unused, kept for API compatibility).
        detection: Detection results with (bbox, label, score) tuples.
        labels: List of known labels.

    Returns:
        List of (xmin, ymin, xmax, ymax) bounding boxes.
    """
    return [(int(xmin), int(ymin), int(xmax), int(ymax)) for (xmin, ymin, xmax, ymax), _, _ in detection]
