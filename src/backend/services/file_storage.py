from pathlib import Path
from uuid import uuid4

MAX_UPLOAD_BYTES = 512 * 1024 * 1024
ALLOWED_SUFFIXES = {".pcap": "PCAP", ".pcapng": "PCAPNG"}


class FileStorage:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, upload):
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise ValueError("Unsupported file type. Upload a PCAP or PCAPNG file.")
        upload.seek(0, 2)
        size = upload.tell()
        upload.seek(0)
        if size > MAX_UPLOAD_BYTES:
            raise ValueError("Upload failed. File size must be 512 MB or less.")
        stored = self.directory / f"{uuid4().hex}{suffix}"
        upload.save(stored)
        return {
            "original_name": upload.filename,
            "stored_path": str(stored),
            "file_size": size,
            "file_type": ALLOWED_SUFFIXES[suffix],
        }
