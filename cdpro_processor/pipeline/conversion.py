"""
Stage 1 of the processing pipeline: user-supplied file conversion.

Override ConversionStage.process() with your own logic.
The method receives the original input file path and should return
the path of the file that CD Pro (Stage 2) will receive — this may be
the same path, or a new/temp file written to output_dir.

This module deliberately has no Qt imports so it can be tested standalone.
"""

import csv
import io
import re
from pathlib import Path

from config.file_types import FileTypeConfig

from dataclasses import dataclass


@dataclass
class InputFormat:
    name: str
    description: str


# Registry of supported input formats.
# Each key maps to a method named process_<key> on ConversionStage.
# Add an entry here and a matching method below to support a new format.
INPUT_FORMATS: dict[str, InputFormat] = {
    "type1": InputFormat(name="Type 1", description="Placeholder format type 1"),
    "type2": InputFormat(name="Type 2", description="Placeholder format type 2"),
    "type3": InputFormat(name="Type 3", description="Placeholder format type 3"),
}

# Maps file extensions to a format label.
# Add or modify entries here as you support more formats.
EXTENSION_TYPE_MAP: dict[str, str] = {
    ".csv":  "csv",
    ".txt":  "text",
    ".wav":  "audio_wav",
    ".aif":  "audio_aif",
    ".aiff": "audio_aif",
}

# Regex that captures the extension from a filename or full path,
# including dotfiles and multi-part names (e.g. ".hidden", "file.tar.gz").
_EXT_PATTERN = re.compile(r"\.([^./\\]+)$", re.IGNORECASE)


class ConversionStage:
    """
    Pre-processing hook for Stage 1.

    Reads the input text file into self.content, then hands the
    (unmodified) file path on to CD Pro. Replace process() with your
    own logic to transform self.content and write a new output file.
    """

    def __init__(self) -> None:
        self.content: str = ""
        self.detected_type: str = ""   # value from EXTENSION_TYPE_MAP, or raw extension
        self.name: str = ""            # sample name passed to CD Pro as output file header

    def read_text(self, input_path: str, encoding: str = "utf-8") -> str:
        """Read a text file into self.content, detect its type, and return the content.

        Also sets self.name from the input filename stem if not already assigned.
        Override self.name after calling read_text() to use a custom sample name.
        """
        self.content = Path(input_path).read_text(encoding=encoding)

        match = _EXT_PATTERN.search(input_path)
        if match:
            ext = f".{match.group(1).lower()}"
            self.detected_type = EXTENSION_TYPE_MAP.get(ext, ext.lstrip("."))
        else:
            self.detected_type = "unknown"

        # Default sample name to the filename stem (e.g. "mysample" from "mysample.csv").
        # Only set if not already assigned so a manual override is preserved.
        if not self.name:
            self.name = Path(input_path).stem

        return self.content

    def process(
        self,
        input_path: str,
        file_type: FileTypeConfig,
        output_dir: str,
        input_format: str = "",
    ) -> str:
        """
        Convert / transform input_path before it is handed to CD Pro.

        Dispatches to process_<input_format>() to produce a CSV, then
        passes the result to process_csv().

        Args:
            input_path:    Absolute path to the source file.
            file_type:     The FileTypeConfig for the currently selected type.
            output_dir:    The user-chosen output directory.
            input_format:  Key from INPUT_FORMATS (e.g. "type1").
        """
        self.read_text(input_path)

        dispatch = {
            "type1": self.process_type1,
            "type2": self.process_type2,
            "type3": self.process_type3,
        }

        if input_format in dispatch:
            csv_path = dispatch[input_format](input_path, output_dir)
            return self.process_csv(csv_path)

        # Fallback: treat input as CSV directly
        return self.process_csv(input_path)

    # ------------------------------------------------------------------
    # Input format converters — each receives the raw input file and
    # must return an absolute path to a CSV file for process_csv().
    # ------------------------------------------------------------------

    def process_type1(self, input_path: str, output_dir: str) -> str:
        # TODO: convert input_path to CSV and return the new path
        return input_path

    def process_type2(self, input_path: str, output_dir: str) -> str:
        # TODO: convert input_path to CSV and return the new path
        return input_path

    def process_type3(self, input_path: str, output_dir: str) -> str:
        # TODO: convert input_path to CSV and return the new path
        return input_path

    def process_csv(self, input_path: str) -> str:
        """Parse self.content as a two-column CSV into self.col1 and self.col2."""
        rows = []
        for line in self.content.splitlines():
            if line.strip():
                rows.append([cell.strip() for cell in line.split(",")])



        with open(f"{self.name}_CD.txt","w") as plain:
            plain.write(f"\n#\n# PRINT    IBasis   \n      0         1       \n#\n# 1 Title Line\n SAMPLE INPUT:  Lactate Dehydrogenase CD DATA (178-260 nm)\n#\n#    WL_Begin     WL_End       Factor\n     {max(self.col1)}    {min(self.col1)}    {abs(self.col1[0]-self.col1[1])}\n#")

        return input_path