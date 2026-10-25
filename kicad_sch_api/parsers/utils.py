"""
Utility functions for S-expression parsing.

Common helper functions used across multiple element parsers,
extracted from monolithic parser.py for reusability.
"""

from typing import Any, Dict, List, Tuple, Union

import sexpdata


def _number(value: Any) -> Union[int, float]:
    """Parse an S-expression number, keeping integers as int so they round-trip unchanged."""
    number = float(value)
    return int(number) if number.is_integer() else number


def _parse_color(elem: List[Any]) -> Tuple[Union[int, float], ...]:
    """Parse (color r g b a) into an (r, g, b, a) tuple."""
    return tuple(_number(v) for v in elem[1:5])


def parse_stroke(stroke: List[Any], data: Dict[str, Any]) -> None:
    """Read (stroke (width w) (type t) (color r g b a)) into stroke_width/stroke_type/stroke_color."""
    for elem in stroke[1:]:
        if not isinstance(elem, list) or len(elem) < 2:
            continue
        key = str(elem[0])
        if key == "width":
            data["stroke_width"] = float(elem[1])
        elif key == "type":
            data["stroke_type"] = str(elem[1])
        elif key == "color" and len(elem) >= 5:
            data["stroke_color"] = _parse_color(elem)


def parse_fill(fill: List[Any], data: Dict[str, Any]) -> None:
    """Read (fill (type t) (color r g b a)) into fill_type/fill_color."""
    for elem in fill[1:]:
        if not isinstance(elem, list):
            continue
        key = str(elem[0])
        if key == "type":
            data["fill_type"] = str(elem[1]) if len(elem) >= 2 else "none"
        elif key == "color" and len(elem) >= 5:
            data["fill_color"] = _parse_color(elem)


def stroke_to_sexp(data: Dict[str, Any], default_width: float, default_type: str) -> List[Any]:
    """Build (stroke ...) from stroke_width/stroke_type/stroke_color."""
    stroke = [
        sexpdata.Symbol("stroke"),
        [sexpdata.Symbol("width"), data.get("stroke_width", default_width)],
        [sexpdata.Symbol("type"), sexpdata.Symbol(data.get("stroke_type", default_type))],
    ]
    if data.get("stroke_color") is not None:
        stroke.append([sexpdata.Symbol("color"), *data["stroke_color"]])
    return stroke


def fill_to_sexp(data: Dict[str, Any], default_type: str) -> List[Any]:
    """Build (fill ...) from fill_type/fill_color."""
    fill = [
        sexpdata.Symbol("fill"),
        [sexpdata.Symbol("type"), sexpdata.Symbol(data.get("fill_type", default_type))],
    ]
    if data.get("fill_color") is not None:
        fill.append([sexpdata.Symbol("color"), *data["fill_color"]])
    return fill


def color_to_rgba(color_name: str) -> List[float]:
    """
    Convert color name to RGBA values (0.0-1.0) for KiCAD compatibility.

    Args:
        color_name: Color name (e.g., "red", "blue", "green")

    Returns:
        List of 4 floats [R, G, B, A] in range 0.0-1.0

    Example:
        >>> color_to_rgba("red")
        [1.0, 0.0, 0.0, 1.0]
        >>> color_to_rgba("unknown")
        [0.0, 0.0, 0.0, 1.0]  # defaults to black
    """
    # Basic color mapping for common colors (0.0-1.0 range)
    color_map = {
        "red": [1.0, 0.0, 0.0, 1.0],
        "blue": [0.0, 0.0, 1.0, 1.0],
        "green": [0.0, 1.0, 0.0, 1.0],
        "yellow": [1.0, 1.0, 0.0, 1.0],
        "magenta": [1.0, 0.0, 1.0, 1.0],
        "cyan": [0.0, 1.0, 1.0, 1.0],
        "black": [0.0, 0.0, 0.0, 1.0],
        "white": [1.0, 1.0, 1.0, 1.0],
        "gray": [0.5, 0.5, 0.5, 1.0],
        "grey": [0.5, 0.5, 0.5, 1.0],
        "orange": [1.0, 0.5, 0.0, 1.0],
        "purple": [0.5, 0.0, 0.5, 1.0],
    }

    # Return RGBA values, default to black if color not found
    return color_map.get(color_name.lower(), [0.0, 0.0, 0.0, 1.0])


def color_to_rgb255(color_name: str) -> List[int]:
    """
    Convert color name to RGB values (0-255) for KiCAD rectangle graphics.

    Args:
        color_name: Color name (e.g., "red", "blue", "green")

    Returns:
        List of 3 integers [R, G, B] in range 0-255

    Example:
        >>> color_to_rgb255("red")
        [255, 0, 0]
        >>> color_to_rgb255("unknown")
        [0, 0, 0]  # defaults to black
    """
    # Basic color mapping for common colors (0-255 range)
    color_map = {
        "red": [255, 0, 0],
        "blue": [0, 0, 255],
        "green": [0, 255, 0],
        "yellow": [255, 255, 0],
        "magenta": [255, 0, 255],
        "cyan": [0, 255, 255],
        "black": [0, 0, 0],
        "white": [255, 255, 255],
        "gray": [128, 128, 128],
        "grey": [128, 128, 128],
        "orange": [255, 128, 0],
        "purple": [128, 0, 128],
    }

    # Return RGB values, default to black if color not found
    return color_map.get(color_name.lower(), [0, 0, 0])
