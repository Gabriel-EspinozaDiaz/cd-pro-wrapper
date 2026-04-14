from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QComboBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config.file_types import FILE_TYPES
from core.settings import AppSettings
from pipeline.cdpro_runner import CDProRunner
from pipeline.conversion import ConversionStage
from pipeline.worker import PipelineWorker
from ui.drop_zone import DropZoneWidget
from ui.file_list import FileListWidget
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._settings = settings
        self._worker: PipelineWorker | None = None

        self.setWindowTitle("CD Pro Processor")
        self.setMinimumSize(600, 700)
        self._build_ui()
        self._connect_signals()
        self._restore_state()

    # ------------------------------------------------------------------ build
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # File type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("File type:"))
        self._type_combo = QComboBox()
        for key, cfg in FILE_TYPES.items():
            self._type_combo.addItem(cfg.name, userData=key)
            self._type_combo.setItemData(
                self._type_combo.count() - 1, cfg.description, Qt.ItemDataRole.ToolTipRole
            )
        type_row.addWidget(self._type_combo, stretch=1)
        root.addLayout(type_row)

        # Drop zone
        self._drop_zone = DropZoneWidget()
        root.addWidget(self._drop_zone)

        # File list
        file_list_box = QGroupBox("Queued files")
        fl_layout = QVBoxLayout(file_list_box)
        self._file_list = FileListWidget()
        fl_layout.addWidget(self._file_list)
        root.addWidget(file_list_box)

        # Output folder
        output_box = QGroupBox("Output folder")
        out_layout = QHBoxLayout(output_box)
        self._output_edit = QLineEdit()
        self._output_edit.setReadOnly(True)
        self._output_edit.setPlaceholderText("Choose an output folder…")
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_output_folder)
        out_layout.addWidget(self._output_edit, stretch=1)
        out_layout.addWidget(browse_btn)
        root.addWidget(output_box)

        # Run / cancel
        action_row = QHBoxLayout()
        self._run_btn = QPushButton("Run")
        self._run_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._run_btn.setEnabled(False)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        action_row.addWidget(self._run_btn, stretch=3)
        action_row.addWidget(self._cancel_btn, stretch=1)
        root.addLayout(action_row)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        root.addWidget(self._progress)

        # Log pane
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(500)
        self._log.setPlaceholderText("Processing log will appear here…")
        font = self._log.font()
        font.setFamily("Menlo")
        font.setPointSize(11)
        self._log.setFont(font)
        root.addWidget(self._log)

        # Settings action in menu bar
        menu = self.menuBar()
        app_menu = menu.addMenu("App")
        settings_action = app_menu.addAction("Settings…")
        settings_action.triggered.connect(self._open_settings)

    # --------------------------------------------------------- connect signals
    def _connect_signals(self) -> None:
        self._drop_zone.files_dropped.connect(self._file_list.add_files)
        self._type_combo.currentIndexChanged.connect(self._on_file_type_changed)
        self._file_list.list_changed.connect(self._on_list_changed)
        self._run_btn.clicked.connect(self._on_run_clicked)
        self._cancel_btn.clicked.connect(self._on_cancel_clicked)

    # ---------------------------------------------------------- restore state
    def _restore_state(self) -> None:
        self._output_edit.setText(self._settings.last_output_dir)

        last_type = self._settings.last_file_type
        if last_type:
            for i in range(self._type_combo.count()):
                if self._type_combo.itemData(i) == last_type:
                    self._type_combo.setCurrentIndex(i)
                    break

        self._on_file_type_changed(self._type_combo.currentIndex())

    # ----------------------------------------------------------------- slots
    def _on_file_type_changed(self, index: int) -> None:
        key = self._type_combo.itemData(index)
        cfg = FILE_TYPES.get(key)
        if cfg:
            self._drop_zone.set_accepted_extensions(cfg.extensions)
            self._settings.last_file_type = key

    def _on_list_changed(self, paths: list) -> None:
        has_files = bool(paths)
        has_output = bool(self._output_edit.text().strip())
        self._run_btn.setEnabled(has_files and has_output)

    def _browse_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self._settings.last_output_dir
        )
        if folder:
            self._output_edit.setText(folder)
            self._settings.last_output_dir = folder
            self._on_list_changed(self._file_list.get_files())

    def _on_run_clicked(self) -> None:
        files = self._file_list.get_files()
        if not files:
            return

        output_dir = self._output_edit.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "No output folder", "Please choose an output folder first.")
            return

        key = self._type_combo.currentData()
        file_type = FILE_TYPES.get(key)
        if file_type is None:
            return

        cdpro = CDProRunner(
            wine_path=self._settings.wine_path,
            cdpro_exe_path=self._settings.cdpro_exe_path,
        )
        if not cdpro.is_available():
            QMessageBox.warning(
                self,
                "CD Pro not configured",
                "Wine or CDPro.exe path is not set or not found.\n\nConfigure them in App → Settings.",
            )
            # Still allow running — stage 1 (conversion) will execute; stage 2 will be skipped with a warning
        conversion = ConversionStage()

        self._worker = PipelineWorker(
            files=files,
            file_type=file_type,
            output_dir=output_dir,
            conversion=conversion,
            cdpro=cdpro,
        )
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.finished.connect(self._on_worker_finished)

        self._log.clear()
        self._progress.setValue(0)
        self._run_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._worker.start()

    def _on_cancel_clicked(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._log.appendPlainText("Cancelling…")

    def _on_worker_progress(self, message: str, percent: int) -> None:
        self._log.appendPlainText(message)
        self._progress.setValue(percent)

    def _on_file_done(self, path: str, success: bool) -> None:
        status = "✓" if success else "✗ error"
        self._file_list.set_file_status(path, status)

    def _on_worker_finished(self, success: bool, errors: list) -> None:
        self._run_btn.setEnabled(bool(self._file_list.get_files()))
        self._cancel_btn.setEnabled(False)
        self._progress.setValue(100 if success else self._progress.value())

        if errors:
            QMessageBox.warning(
                self,
                "Completed with errors",
                f"{len(errors)} file(s) had errors:\n\n" + "\n".join(errors[:10]),
            )
        else:
            self._log.appendPlainText("\nAll files processed successfully.")

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._settings, parent=self)
        dlg.exec()
