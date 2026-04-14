"""
Stage 2 of the processing pipeline: run CD Pro via Wine.

CDProRunner wraps subprocess calls to:
    wine CDPro.exe <input_file> [extra_args] --output <output_dir>

This module has no Qt imports — it can be used and tested standalone.
"""

import os
import subprocess
from dataclasses import dataclass, field


@dataclass
class CDProResult:
    success: bool
    returncode: int
    stdout: str
    stderr: str
    error_message: str = ""  # human-readable summary if success is False


class CDProRunner:
    """Subprocess wrapper for running CDPro.exe through Wine on macOS."""

    # Default timeout in seconds for a single CDPro invocation
    DEFAULT_TIMEOUT = 300

    def __init__(self, wine_path: str, cdpro_exe_path: str) -> None:
        self.wine_path = wine_path
        self.cdpro_exe_path = cdpro_exe_path

    def is_available(self) -> bool:
        """Return True if both the Wine binary and CDPro.exe exist on disk."""
        return (
            bool(self.wine_path)
            and os.path.isfile(self.wine_path)
            and bool(self.cdpro_exe_path)
            and os.path.isfile(self.cdpro_exe_path)
        )

    def run(
        self,
        input_path: str,
        output_dir: str,
        extra_args: list[str] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> CDProResult:
        """
        Invoke CDPro.exe via Wine for a single file.

        Args:
            input_path:  Absolute path to the (possibly pre-converted) input file.
            output_dir:  Where CD Pro should write its output.
            extra_args:  Additional CLI flags from FileTypeConfig.cdpro_args.
            timeout:     Seconds before the subprocess is killed.

        Returns:
            CDProResult with success flag, return code, and captured output.
        """
        if not self.is_available():
            return CDProResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="",
                error_message=(
                    "CD Pro is not available. Configure Wine and CDPro.exe paths in Settings."
                ),
            )

        cmd = [
            self.wine_path,
            self.cdpro_exe_path,
            input_path,
            # ----------------------------------------------------------------
            # TODO: Adjust these arguments to match CDPro's actual CLI interface.
            #
            # Common patterns:
            #   "--output", output_dir
            #   "-o", output_dir
            #   "/output", output_dir
            # ----------------------------------------------------------------
            "--output", output_dir,
        ]
        if extra_args:
            cmd.extend(extra_args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            success = result.returncode == 0
            return CDProResult(
                success=success,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message="" if success else f"CDPro exited with code {result.returncode}",
            )
        except subprocess.TimeoutExpired:
            return CDProResult(
                success=False,
                returncode=-2,
                stdout="",
                stderr="",
                error_message=f"CDPro timed out after {timeout}s",
            )
        except OSError as exc:
            return CDProResult(
                success=False,
                returncode=-3,
                stdout="",
                stderr="",
                error_message=f"Failed to launch CDPro: {exc}",
            )
