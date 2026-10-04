"""Losslessly package the supplied artwork as HOI4-compatible RGBA DDS.

No cropping, resizing, colour changes, generated content, or compression.
The original RGB24 DDS and PNG references remain under art/focus_icons.
"""
from pathlib import Path
import hashlib
import json
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art/focus_icons/MSGA_TFR_focus_icons"
OUTPUT = ROOT / "make_serbia_great_again/gfx/interface/goals"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for source in sorted((SOURCE / "dds_95").glob("*.dds")):
        reference = Image.open(source).convert("RGBA")
        png = Image.open(SOURCE / "png_95" / (source.stem + ".png")).convert("RGBA")
        assert reference.size == (95, 95)
        assert reference.tobytes() == png.tobytes(), source.name
        destination = OUTPUT / source.name
        reference.save(destination, format="DDS")
        header = destination.read_bytes()[:128]
        assert header[:4] == b"DDS "
        assert struct.unpack_from("<I", header, 88)[0] == 32
        assert Image.open(destination).convert("RGBA").tobytes() == reference.tobytes()
        results.append({
            "sprite": source.stem,
            "dimensions": [95, 95],
            "format": "uncompressed RGBA8, explicit opaque alpha",
            "pixels_preserved": True,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "runtime_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        })
    assert len(results) == 18
    (SOURCE / "conversion_manifest.json").write_text(json.dumps(results, indent=2) + "\n")
    print("18 DDS files: RGBA8, 95x95, every decoded pixel matches supplied DDS and PNG.")


if __name__ == "__main__":
    main()
