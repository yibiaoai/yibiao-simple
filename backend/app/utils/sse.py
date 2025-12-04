"""SSE (Server-Sent Events) 相关工具"""
from typing import AsyncGenerator, Any, Dict, Optional

from fastapi.responses import StreamingResponse


DEFAULT_SSE_HEADERS: Dict[str, str] = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "text/event-stream",
}


def sse_response(
    generator: AsyncGenerator[str, Any],
    media_type: str = "text/event-stream",
    extra_headers: Optional[Dict[str, str]] = None,
) -> StreamingResponse:
    """
    包装 SSE 异步生成器为 StreamingResponse，统一 headers 和 media_type。

    Args:
        generator: 异步生成器，yield 已经带好 "data: ..." 和 "\n\n" 的字符串
        media_type: 响应的 media_type，默认使用 text/event-stream
        extra_headers: 额外需要添加或覆盖的响应头
    """
    headers = DEFAULT_SSE_HEADERS.copy()
    if extra_headers:
        headers.update(extra_headers)

    return StreamingResponse(
        generator,
        media_type=media_type,
        headers=headers,
    )



