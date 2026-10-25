"""
Round-trip of stroke/fill colors and text justification on schematic graphics.

Loading and saving an untouched schematic must not drop (color ...) from
stroke/fill or (justify ...) from text effects.
"""

from kicad_sch_api import load_schematic

SCHEMATIC = """(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "00000000-0000-0000-0000-000000000001")
	(paper "A4")
	(lib_symbols)
	(polyline (pts (xy 10 10) (xy 20 10)) (stroke (width 0.6) (type solid) (color 255 140 0 1)) (uuid "00000000-0000-0000-0000-000000000010"))
	(arc (start 30 10) (mid 35 5) (end 40 10) (stroke (width 0.2) (type dash) (color 10 20 30 1)) (fill (type color) (color 40 50 60 1)) (uuid "00000000-0000-0000-0000-000000000011"))
	(circle (center 50 10) (radius 2) (stroke (width 0.3) (type solid)) (fill (type color) (color 220 30 30 1)) (uuid "00000000-0000-0000-0000-000000000012"))
	(bezier (pts (xy 60 10) (xy 62 5) (xy 64 15) (xy 66 10)) (stroke (width 0.2) (type solid) (color 1 2 3 1)) (fill (type none)) (uuid "00000000-0000-0000-0000-000000000013"))
	(rectangle (start 70 10) (end 80 20) (stroke (width 0.4) (type solid) (color 0 0 255 1)) (fill (type color) (color 255 236 150 1)) (uuid "00000000-0000-0000-0000-000000000014"))
	(text "left bottom" (exclude_from_sim no) (at 10 40 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "00000000-0000-0000-0000-000000000015"))
	(text "centered" (exclude_from_sim no) (at 10 50 0) (effects (font (size 2 2))) (uuid "00000000-0000-0000-0000-000000000016"))
	(text_box "box" (exclude_from_sim no) (at 10 60 0) (size 20 10) (margins 1 1 1 1) (stroke (width 0.2) (type solid) (color 9 8 7 1)) (fill (type color) (color 200 200 200 1)) (effects (font (size 1.27 1.27)) (justify left top)) (uuid "00000000-0000-0000-0000-000000000017"))
	(sheet_instances (path "/" (page "1")))
)
"""


def _roundtrip(tmp_path):
    src = tmp_path / "in.kicad_sch"
    src.write_text(SCHEMATIC)
    dst = tmp_path / "out.kicad_sch"
    load_schematic(str(src)).save(str(dst))
    return load_schematic(str(dst))._data


def _by_uuid(items, uuid_suffix):
    return next(i for i in items if i["uuid"].endswith(uuid_suffix))


def test_stroke_and_fill_colors_survive_save(tmp_path):
    data = _roundtrip(tmp_path)

    polyline = _by_uuid(data["polylines"], "010")
    assert polyline["stroke_color"] == (255, 140, 0, 1)

    arc = _by_uuid(data["arcs"], "011")
    assert arc["stroke_color"] == (10, 20, 30, 1)
    assert arc["fill_color"] == (40, 50, 60, 1)

    circle = _by_uuid(data["circles"], "012")
    assert "stroke_color" not in circle
    assert circle["fill_type"] == "color"
    assert circle["fill_color"] == (220, 30, 30, 1)

    bezier = _by_uuid(data["beziers"], "013")
    assert bezier["stroke_color"] == (1, 2, 3, 1)
    assert "fill_color" not in bezier

    rectangle = _by_uuid(data["rectangles"], "014")
    assert rectangle["stroke_color"] == (0, 0, 255, 1)
    assert rectangle["fill_color"] == (255, 236, 150, 1)

    text_box = _by_uuid(data["text_boxes"], "017")
    assert text_box["stroke_color"] == (9, 8, 7, 1)
    assert text_box["fill_color"] == (200, 200, 200, 1)


def test_text_justify_survives_save(tmp_path):
    data = _roundtrip(tmp_path)

    assert _by_uuid(data["texts"], "015")["justify"] == ["left", "bottom"]
    assert "justify" not in _by_uuid(data["texts"], "016")


def test_saved_file_keeps_color_and_justify_tokens(tmp_path):
    src = tmp_path / "in.kicad_sch"
    src.write_text(SCHEMATIC)
    dst = tmp_path / "out.kicad_sch"
    load_schematic(str(src)).save(str(dst))
    saved = " ".join(dst.read_text().split())

    for token in [
        "(color 255 140 0 1)",
        "(color 40 50 60 1)",
        "(color 220 30 30 1)",
        "(color 255 236 150 1)",
        "(color 9 8 7 1)",
        "(justify left bottom)",
    ]:
        assert token in saved, token
