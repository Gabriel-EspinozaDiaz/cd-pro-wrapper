import sys

from PyQt6.QtWidgets import QApplication

from core.settings import AppSettings
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("CDProProcessor")
    app.setOrganizationName(AppSettings.ORGANIZATION)

    settings = AppSettings()
    window = MainWindow(settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
