"""Create a focused PNG crop from an approved portfolio visual."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--box", nargs=4, type=int, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), required=True)
    args = parser.parse_args()

    with Image.open(args.source) as image:
        width, height = image.size
        left, top, right, bottom = args.box
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise SystemExit(f"Crop {args.box} is outside source dimensions {(width, height)}")
        crop = image.crop((left, top, right, bottom))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        crop.save(args.output, "PNG", optimize=True)
        print(f"Saved {args.output.name}: {crop.size[0]} x {crop.size[1]}")


if __name__ == "__main__":
    main()
