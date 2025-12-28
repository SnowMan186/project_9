from pathlib import Path
import json


class FileManager:
    """Управляет чтением и записью данных в файлы."""

    def read_file(self, filepath: Path) -> str:
        """Читает данные из файла."""
        with open(filepath, mode="r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, filepath: Path, content: str) -> None:
        """Записывает данные в файл."""
        with open(filepath, mode="w", encoding="utf-8") as f:
            f.write(content)

    def load_json(self, filepath: Path) -> dict:
        """Загружает JSON-файл."""
        with open(filepath, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def dump_json(self, filepath: Path, obj: dict) -> None:
        """Сохраняет словарь в JSON-файл."""
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
