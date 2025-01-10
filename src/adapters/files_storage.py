import io
from datetime import timedelta
from typing import Union, Optional

import miniopy_async

from config import Config


class FilesStorage:
    def __init__(self, config: Config, minio_client: miniopy_async.Minio):
        self._config = config
        self._minio_client = minio_client

    async def put_object(
            self,
            bucket_name: str,
            object_name: str,
            data: Union[io.BytesIO, io.StringIO],
            length: int,
            content_type: str,
    ) -> str:
        if not await self._minio_client.bucket_exists(bucket_name):
            await self._minio_client.make_bucket(bucket_name)
        await self._minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=length,
            content_type=content_type,
        )
        return await self.get_object_link(bucket_name, object_name, content_type=content_type)

    async def get_object_link(
            self,
            bucket_name: str,
            object_name: str,
            expires: timedelta = timedelta(hours=1),
            content_type: Optional[str] = None,
    ) -> str:
        response_headers = {}
        if content_type:
            response_headers["Content-Type"] = content_type
        return await self._minio_client.presigned_get_object(
            bucket_name,
            object_name,
            change_host=self._config.MINIO_PUBLIC_HOST,
            response_headers=response_headers,
            expires=expires,
        )

    async def check_object_exists(self, bucket_name: str, object_name: str) -> bool:
        try:
            await self._minio_client.stat_object(bucket_name, object_name)
            return True
        except Exception:
            return False
