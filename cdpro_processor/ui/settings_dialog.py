from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.settings import AppSettings


class SettingsDialog(QDialog):
    """Dialog for configuring Wine and CD Pro paths."""

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Wine path row
        self._wine_edit = QLineEdit(self._settings.wine_path)
        wine_browse = QPushButton("Browse…")
        wine_browse.clicked.connect(self._browse_wine)
        wine_row = self._make_row(self._wine_edit, wine_browse)
        form.addRow("Wine executable:", wine_row)
        form.addRow("", QLabel("<small>e.g. /usr/local/bin/wine  (brew install --cask wine-stable)</small>"))

        # CD Pro exe path row
        self._cdpro_edit = QLineEdit(self._settings.cdpro_exe_path)
        cdpro_browse = QPushButton("Browse…")
        cdpro_browse.clicked.connect(self._browse_cdpro)
        cdpro_row = self._make_row(self._cdpro_edit, cdpro_browse)
        form.addRow("CDPro.exe path:", cdpro_row)
        form.addRow("", QLabel("<small>Absolute path to the CD Pro Windows executable</small>"))

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _make_row(edit: QLineEdit, btn: QPushButton) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(edit, stretch=1)
        row.addWidget(btn)
        return w

    def _browse_wine(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Wine Executable", "/usr/local/bin")
        if path:
            self._wine_edit.setText(path)

    def _browse_cdpro(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CDPro.exe", "", "Executables (*.exe);;All files (*)"
        )
        if path:
            self._cdpro_edit.setText(path)

    def accept(self) -> None:
        self._settings.wine_path = self._wine_edit.text().strip()
        self._settings.cdpro_exe_path = self._cdpro_edit.text().strip()
        super().accept()
