from dataclasses import dataclass, field


@dataclass
class FileTypeConfig:
    name: str
    extensions: list[str]
    description: str
    cdpro_args: list[str] = field(default_factory=list)


# Registry of supported file types.
# To add a new type: add an entry here — nothing else in the app needs to change.
FILE_TYPES: dict[str, FileTypeConfig] = {
    "spectral": FileTypeConfig(
        name="Spectral Data",
        extensions=[".csv", ".txt"],
        description="Raw spectral output files (.csv, .txt)",
    ),
    "audio": FileTypeConfig(
        name="Audio",
        extensions=[".wav", ".aif", ".aiff"],
        description="Uncompressed audio files (.wav, .aif, .aiff)",
        cdpro_args=["--audio-mode"],
    ),
    # Add more types here as needed
}
