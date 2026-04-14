#!/usr/bin/env python3
"""
Usage:
    python convert.py <input.csv>

Reads a CSV file into a 2D list and writes a formatted plaintext output
next to the input file (same directory, .txt extension).
"""

import sys
from pathlib import Path


def read_csv(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append([cell.strip() for cell in line.split(",")])
    return rows


def write_output(data: list[list[str]], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        # TODO: replace the block below with your desired output format
        for i, row in enumerate(data):
            value = float(row[1])
            formatted = f"{value:.2f}"
            spacing = "   " if value >= 0 else "  "
            f.write(formatted + spacing)
            if (i + 1) % 15 == 0:
                f.write("\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python convert.py <input.csv>")
        sys.exit(1)

    in_path = Path(sys.argv[1]).resolve()
    if not in_path.exists():
        print(f"File not found: {in_path}")
        sys.exit(1)

    data = read_csv(in_path)
    out_path = in_path.with_suffix(".txt")
    write_output(data, out_path)
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
