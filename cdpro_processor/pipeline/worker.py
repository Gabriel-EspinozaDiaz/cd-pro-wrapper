"""
PipelineWorker — QThread subclass that runs the two-stage processing pipeline.

Stage 1: ConversionStage.process()   (user's Python script)
Stage 2: CDProRunner.run()           (Wine + CDPro.exe)

Signals are emitted from the worker thread; Qt's AutoConnection queues them
to the main thread automatically, so UI updates are safe.
"""

import threading
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from config.file_types import FileTypeConfig
from pipeline.cdpro_runner import CDProRunner
from pipeline.conversion import ConversionStage


class PipelineWorker(QThread):
    # (human-readable message, 0-100 percent)
    progress = pyqtSignal(str, int)

    # Path of the file that just started processing
    file_started = pyqtSignal(str)

    # (path, success)
    file_done = pyqtSignal(str, bool)

    # (overall_success, list_of_error_strings)
    finished = pyqtSignal(bool, list)

    def __init__(
        self,
        files: list[str],
        file_type: FileTypeConfig,
        output_dir: str,
        conversion: ConversionStage,
        cdpro: CDProRunner,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._files = files
        self._file_type = file_type
        self._output_dir = output_dir
        self._conversion = conversion
        self._cdpro = cdpro
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        """Request cancellation. The thread checks between files."""
        self._cancel_event.set()

    def run(self) -> None:
        errors: list[str] = []
        total = len(self._files)

        for idx, path in enumerate(self._files):
            if self._cancel_event.is_set():
                self.progress.emit("Cancelled.", int(idx / total * 100))
                break

            name = Path(path).name
            self.file_started.emit(path)
            self.progress.emit(f"[{idx + 1}/{total}] {name}", int(idx / total * 100))

            # ---- Stage 1: Conversion ----
            try:
                converted_path = self._conversion.process(
                    input_path=path,
                    file_type=self._file_type,
                    output_dir=self._output_dir,
                )
                self.progress.emit(f"  Stage 1 done → {converted_path}", int((idx + 0.5) / total * 100))
            except Exception as exc:
                msg = f"  Stage 1 error for {name}: {exc}"
                self.progress.emit(msg, int((idx + 0.5) / total * 100))
                errors.append(f"{name}: conversion error — {exc}")
                self.file_done.emit(path, False)
                continue

            # ---- Stage 2: CD Pro via Wine ----
            result = self._cdpro.run(
                input_path=converted_path,
                output_dir=self._output_dir,
                extra_args=self._file_type.cdpro_args or None,
            )
            if result.success:
                self.progress.emit(f"  Stage 2 done ✓", int((idx + 1) / total * 100))
                self.file_done.emit(path, True)
            else:
                msg = f"  Stage 2 error for {name}: {result.error_message}"
                if result.stderr:
                    msg += f"\n    stderr: {result.stderr[:200]}"
                self.progress.emit(msg, int((idx + 1) / total * 100))
                errors.append(f"{name}: {result.error_message}")
                self.file_done.emit(path, False)

        self.finished.emit(len(errors) == 0, errors)
