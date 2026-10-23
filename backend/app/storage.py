import os, secrets
from pathlib import Path
from abc import ABC, abstractmethod
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
class StorageBackend(ABC):
    @abstractmethod
    def write(self, data: bytes, filename: str) -> str: ...
    @abstractmethod
    def read(self, path: str) -> bytes: ...

class LocalStorage(StorageBackend):
    def __init__(self, root=None):
        self.root = Path(root or os.getenv('PROOFGRAPH_STORAGE',str(ROOT/'storage'))).resolve()
        self.root.mkdir(parents=True,exist_ok=True)
    def write(self, data, filename):
        ext = Path(filename).suffix.lower()
        if ext not in {'.pdf','.png','.jpg','.jpeg','.webp'}:
            raise HTTPException(400,'Only PDF/PNG/JPG/WebP uploads supported')
        identifier = secrets.token_hex(14) + ext
        (self.root/identifier).write_bytes(data)
        return identifier
    def read(self, path):
        file = (self.root / path).resolve()
        if file.parent != self.root: raise HTTPException(403,'Unsafe path')
        if not file.is_file(): raise HTTPException(404,'Document file unavailable')
        return file.read_bytes()

storage = LocalStorage()
