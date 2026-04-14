from PyQt6.QtCore import QSettings


class AppSettings:
    ORGANIZATION = "MyOrg"
    APPLICATION = "CDProProcessor"

    def __init__(self) -> None:
        self._qs = QSettings(self.ORGANIZATION, self.APPLICATION)

    # Wine executable path (e.g. /usr/local/bin/wine or /opt/homebrew/bin/wine)
    @property
    def wine_path(self) -> str:
        return self._qs.value("wine_path", "/usr/local/bin/wine")

    @wine_path.setter
    def wine_path(self, value: str) -> None:
        self._qs.setValue("wine_path", value)

    # Absolute path to CDPro.exe
    @property
    def cdpro_exe_path(self) -> str:
        return self._qs.value("cdpro_exe_path", "")

    @cdpro_exe_path.setter
    def cdpro_exe_path(self, value: str) -> None:
        self._qs.setValue("cdpro_exe_path", value)

    # Last output directory chosen by the user
    @property
    def last_output_dir(self) -> str:
        import os
        return self._qs.value("last_output_dir", os.path.expanduser("~/Desktop"))

    @last_output_dir.setter
    def last_output_dir(self, value: str) -> None:
        self._qs.setValue("last_output_dir", value)

    # Key into FILE_TYPES dict for the last selected file type
    @property
    def last_file_type(self) -> str:
        return self._qs.value("last_file_type", "")

    @last_file_type.setter
    def last_file_type(self, value: str) -> None:
        self._qs.setValue("last_file_type", value)
