from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class _FileRow(QWidget):
    remove_requested = pyqtSignal(str)  # emits the file path

    def __init__(self, path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.path = path

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._label = QLabel(Path(path).name)
        self._label.setToolTip(path)

        self._remove_btn = QPushButton("✕")
        self._remove_btn.setFixedSize(20, 20)
        self._remove_btn.setFlat(True)
        self._remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.path))

        layout.addWidget(self._label, stretch=1)
        layout.addWidget(self._remove_btn)

    def set_status(self, status: str) -> None:
        """Update the label suffix to show processing status."""
        name = Path(self.path).name
        self._label.setText(f"{name}  {status}" if status else name)


class FileListWidget(QWidget):
    """Displays the queue of files to be processed, with per-row remove buttons."""

    list_changed = pyqtSignal(list)  # list[str] — current file paths

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._paths: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._list = QListWidget()
        self._list.setSpacing(1)

        clear_btn = QPushButton("Clear all")
        clear_btn.clicked.connect(self.clear)

        layout.addWidget(self._list)
        layout.addWidget(clear_btn)

    def add_files(self, paths: list[str]) -> None:
        for path in paths:
            if path not in self._paths:
                self._paths.append(path)
                self._add_row(path)
        self.list_changed.emit(list(self._paths))

    def remove_file(self, path: str) -> None:
        if path not in self._paths:
            return
        self._paths.remove(path)
        for i in range(self._list.count()):
            item = self._list.item(i)
            widget = self._list.itemWidget(item)
            if isinstance(widget, _FileRow) and widget.path == path:
                self._list.takeItem(i)
                break
        self.list_changed.emit(list(self._paths))

    def clear(self) -> None:
        self._paths.clear()
        self._list.clear()
        self.list_changed.emit([])

    def get_files(self) -> list[str]:
        return list(self._paths)

    def set_file_status(self, path: str, status: str) -> None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            widget = self._list.itemWidget(item)
            if isinstance(widget, _FileRow) and widget.path == path:
                widget.set_status(status)
                break

    def _add_row(self, path: str) -> None:
        row = _FileRow(path)
        row.remove_requested.connect(self.remove_file)
        item = QListWidgetItem(self._list)
        item.setSizeHint(row.sizeHint())
        self._list.addItem(item)
        self._list.setItemWidget(item, row)
