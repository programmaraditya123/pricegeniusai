from abc import ABC, abstractmethod
from pathlib import Path

from app.expense_tracker.config import get_settings


class StorageProvider(ABC):
    @abstractmethod
    async def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    async def delete(self, key: str) -> None:
        path = self.base_path / key
        if path.exists():
            path.unlink()


class S3StorageProvider(StorageProvider):
    def __init__(self):
        import boto3

        settings = get_settings()
        self.bucket = settings.s3_bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )

    async def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        extra_args = {"ContentType": content_type} if content_type else {}
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra_args)
        return key

    async def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


class StorageService:
    def __init__(self, provider: StorageProvider | None = None):
        self.provider = provider or self._provider_from_settings()

    async def save(self, key: str, data: bytes, content_type: str | None = None) -> str:
        return await self.provider.save(key, data, content_type)

    async def delete(self, key: str) -> None:
        await self.provider.delete(key)

    def _provider_from_settings(self) -> StorageProvider:
        settings = get_settings()
        if settings.storage_backend.lower() == "s3":
            return S3StorageProvider()
        return LocalStorageProvider(settings.local_storage_path)

