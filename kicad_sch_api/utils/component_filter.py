"""
Shared component filtering for ComponentCollection.filter() and bulk_update().
"""

import re
from typing import Any, Iterable, List

SUPPORTED_CRITERIA = (
    "lib_id",
    "value",
    "value_pattern",
    "reference",
    "reference_pattern",
    "footprint",
    "in_area",
    "has_property",
)


def filter_components(components: Iterable[Any], **criteria: Any) -> List[Any]:
    """
    Filter components by criteria.

    Supported criteria:
        lib_id: library ID (exact match)
        value: value (exact match)
        value_pattern: value contains (case-insensitive)
        reference: reference designator (exact match)
        reference_pattern: reference designator (regex match)
        footprint: footprint (exact match)
        in_area: (x1, y1, x2, y2) bounding box
        has_property: name of a property the component must have

    Raises:
        ValueError: on an unsupported criteria key, so a typo cannot silently match everything.
    """
    unsupported = sorted(set(criteria) - set(SUPPORTED_CRITERIA))
    if unsupported:
        raise ValueError(
            f"Unsupported filter criteria: {', '.join(unsupported)}. "
            f"Supported: {', '.join(SUPPORTED_CRITERIA)}"
        )

    results = list(components)

    if "lib_id" in criteria:
        results = [c for c in results if c.lib_id == criteria["lib_id"]]

    if "value" in criteria:
        results = [c for c in results if c.value == criteria["value"]]

    if "value_pattern" in criteria:
        pattern = criteria["value_pattern"].lower()
        results = [c for c in results if pattern in c.value.lower()]

    if "reference" in criteria:
        results = [c for c in results if c.reference == criteria["reference"]]

    if "reference_pattern" in criteria:
        pattern = re.compile(criteria["reference_pattern"])
        results = [c for c in results if pattern.match(c.reference)]

    if "footprint" in criteria:
        results = [c for c in results if c.footprint == criteria["footprint"]]

    if "in_area" in criteria:
        x1, y1, x2, y2 = criteria["in_area"]
        results = [c for c in results if x1 <= c.position.x <= x2 and y1 <= c.position.y <= y2]

    if "has_property" in criteria:
        results = [c for c in results if criteria["has_property"] in c.properties]

    return results
