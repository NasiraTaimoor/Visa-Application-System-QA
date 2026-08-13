"""Protected document object storage adapter (T012).

Scaffold implementation stores bytes on local disk under a namespaced
directory and returns an opaque file_reference; production deployments swap
this for an encrypted object store (S3/GCS/Azure Blob) behind the same
interface. No raw file bytes are ever logged or included in audit metadata.
"""

import uuid
from pathlib import Path

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / ".data" / "documents"


class ObjectStorageAdapter:
    def __init__(self, root: Path | None = None):
        self.root = root or STORAGE_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, application_id: str, filename: str, content: bytes) -> str:
        file_reference = f"{application_id}/{uuid.uuid4()}-{filename}"
        target = self.root / file_reference
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return file_reference

    def retrieve(self, file_reference: str) -> bytes:
        return (self.root / file_reference).read_bytes()

    def delete(self, file_reference: str) -> None:
        path = self.root / file_reference
        if path.exists():
            path.unlink()


_default_adapter = ObjectStorageAdapter()


def get_object_storage_adapter() -> ObjectStorageAdapter:
    return _default_adapter
