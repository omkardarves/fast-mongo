from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from api_logger import log_api_response
import io

class LogAPIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Read and store the request body
        req_body_bytes = await request.body()
        req_body = req_body_bytes.decode('utf-8')
        
        # Recreate the request object with the original body so it can be consumed by the route handler
        request = Request(
            scope=request.scope,
            receive=lambda: io.BytesIO(req_body_bytes).read(),
            send=request._send
        )

        # Process the request and get the response
        response = await call_next(request)

        if response.status_code == 200:
            if isinstance(response, StreamingResponse):
                # Capture the response body from a StreamingResponse
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                # Reconstruct the StreamingResponse with the captured body
                response = StreamingResponse(
                    content=iter([response_body]),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                    background=response.background,
                )
            else:
                # Capture the response body for non-streaming responses
                response_body = b"".join([chunk async for chunk in response.__dict__["body_iterator"]])

                # Reconstruct the Response with the captured body
                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                    background=response.background,
                )

            # Log the successful response
            await log_api_response(
                request=request,
                req_body=req_body,
                status_code=response.status_code,
                res_body={"response": response_body.decode('utf-8')},
                function_name=str(request.url),
            )

        return response
