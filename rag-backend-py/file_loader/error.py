class FileLoadError(Exception):
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Load file failed: {self.value}"
