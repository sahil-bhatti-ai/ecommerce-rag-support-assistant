import csv
import json
from io import BytesIO, StringIO
from pathlib import Path

from pypdf import PdfReader


class DocumentLoadError(RuntimeError):
    pass


def load_document_text(path: str | Path) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if not file_path.exists():
        raise DocumentLoadError(f"File does not exist: {file_path}")

    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".csv":
        raw = file_path.read_text(encoding="utf-8", errors="ignore")
        rows = csv.reader(StringIO(raw))
        return "\n".join(" | ".join(cell.strip() for cell in row) for row in rows)

    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
        return json.dumps(payload, ensure_ascii=False, indent=2)

    if suffix == ".pdf":
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(BytesIO(pdf_file.read()))
        text_parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text_parts)

    raise DocumentLoadError(f"Unsupported extension: {suffix}")
