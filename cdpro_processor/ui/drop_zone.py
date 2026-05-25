from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QPaintEvent, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class DropZoneWidget(QWidget):
    """Large drag-and-drop target. Emits files_dropped(list[str]) on a successful drop."""

    files_dropped = pyqtSignal(list)  # list[str] — absolute file paths

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._accepted_extensions: list[str] = []
        self._hovering = False
        self.setAcceptDrops(True)
        self.setMinimumHeight(140)

    def set_accepted_extensions(self, extensions: list[str]) -> None:
        """Call this when the active file type changes."""
        self._accepted_extensions = [e.lower() for e in extensions]

    # ------------------------------------------------------------------ drag
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if self._any_accepted(paths):
                event.acceptProposedAction()
                self._hovering = True
                self.update()
                return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._hovering = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        self._hovering = False
        self.update()
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        accepted = self._filter_accepted(paths)
        if accepted:
            event.acceptProposedAction()
            self.files_dropped.emit(accepted)

    # ----------------------------------------------------------------- paint
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        text_color = QColor("#666666")
        bg_color = text_color if not self.isEnabled() else (QColor("#e8f4fd") if self._hovering else QColor("#f5f5f5"))
        border_color = QColor("#2196F3") if self._hovering else QColor("#aaaaaa")

        painter.fillRect(self.rect(), bg_color)

        pen = QPen(border_color, 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(4, 4, -4, -4), 8, 8)

        painter.setPen(text_color)
        if self._title:
            title_rect = self.rect().adjusted(0, 8, 0, 0)
            title_font = painter.font()
            title_font.setBold(True)
            title_font.setPointSize(title_font.pointSize() + 1)
            painter.setFont(title_font)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._title)
            title_font.setBold(False)
            title_font.setPointSize(title_font.pointSize() - 1)
            painter.setFont(title_font)

        if self._accepted_extensions:
            exts = ", ".join(self._accepted_extensions)
            label = f"Drop files here\n({exts})"
        else:
            label = "Drop files here"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, label)

    # ---------------------------------------------------------------- helpers
    def _any_accepted(self, paths: list[str]) -> bool:
        if not self._accepted_extensions:
            return True
        return any(self._is_accepted(p) for p in paths)

    def _filter_accepted(self, paths: list[str]) -> list[str]:
        if not self._accepted_extensions:
            return paths
        return [p for p in paths if self._is_accepted(p)]

    def _is_accepted(self, path: str) -> bool:
        from pathlib import Path
        return Path(path).suffix.lower() in self._accepted_extensions
