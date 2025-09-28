import httpx
from typing import Any


class HttpxException(Exception):
    def __init__(
        self, 
        msg: str, 
        error: Any, 
        status_code: int | None = None,
    ):
        self.msg = msg
        self.error = error
        self.status_code = status_code

    def __str__(self):
        try:
            return f"{self.msg!s} -> {self.error['error']!s}"
        except TypeError as e:
            return f"{self.msg!s} -> {self.error!s}"

class HttpClients:

    @staticmethod
    async def httpx_request_async(
        method: str, 
        url: str, 
        headers: dict | None = None, 
        data: dict | None = None,
        json: Any | None = None
    ):
        '''Common httpx interface for all async HTTP requests

        url: URL | str,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        stream: SyncByteStream | AsyncByteStream | None = None,
        extensions: RequestExtensions | None = Non
        '''
        try:
            async with httpx.AsyncClient() as client:
                request = httpx.Request(
                    method, url, headers=headers, json=json, data=data
                )
                response = await client.send(request)
                response.raise_for_status()
                return response
        except httpx.TimeoutException as e:
            raise HttpxException(f'Request Timeout: {url}', e)
        except httpx.RequestError as e:
            raise HttpxException(f'Request Failed: {url}', e)
        except httpx.HTTPStatusError as e:
            raise HttpxException(f'Status not 2xx: {url}', e)

    @staticmethod
    def httpx_request(
        method: str, 
        url: str, 
        headers: dict | None = None, 
        data: dict | None = None,
        json: Any | None = None
    ):
        '''Common httpx interface for all non-async HTTP requests

        url: URL | str,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        stream: SyncByteStream | AsyncByteStream | None = None,
        extensions: RequestExtensions | None = Non
        '''
        try:
            with httpx.Client() as client:
                request = httpx.Request(
                    method, url, headers=headers, json=json, data=data
                )
                response = client.send(request)
                response.raise_for_status()
                return response
        except httpx.TimeoutException as e:
            raise HttpxException(f'Request Timeout: {url}', e)
        except httpx.RequestError as e:
            raise HttpxException(f'Request Failed: {url}', e)
        except httpx.HTTPStatusError as e:
            raise HttpxException(f'Status not 2xx: {url}', e)