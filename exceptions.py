
import sys
from typing import Union
from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
    HTTPException,
    WebSocketRequestValidationError,
)
from fastapi.exception_handlers import (
    http_exception_handler as _http_exception_handler,
    request_validation_exception_handler as _request_validation_exception_handler,
    websocket_request_validation_exception_handler as _websocket_request_validation_exception_handler,
)
from fastapi.responses import JSONResponse, Response
from api_logger import setup_logger, log_api_response

logger = setup_logger("api_exceptions.log", "api_exceptions")


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of FastAPI.
    This function will be called when client input is not valid.
    """
    response_body = await _request_validation_exception_handler(request, exc)
    logger.debug("Our custom request_validation_exception_handler was called")
    await log_api_response(
        request, req_body=exc.body, res_body=response_body.body,status_code=422, function_name=str(request.url)
    )
    return response_body

async def http_exception_handler(
    request: Request, exc: HTTPException
) -> Union[JSONResponse, Response]:
    """
    This is a wrapper to the default HTTPException handler of FastAPI.
    This function will be called when a HTTPException is explicitly raised.
    """
    pydantic_basemodel = dict(getattr(request.state, "pydantic_basemodel", {}))
    logger.debug("Our custom http_exception_handler was called")
    response_body = await _http_exception_handler(request, exc)
    await log_api_response(
        request,
        req_body=pydantic_basemodel,
        res_body=response_body.body,
        status_code=exc.status_code,
        function_name=str(request.url),
    )
    return response_body

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.debug("Our custom unhandled_exception_handler was called")
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)
    error_details = f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
    logger.error(error_details)
    pydantic_basemodel = dict(getattr(request.state, "pydantic_basemodel", {}))

    # Ensure the following line is awaited in an asynchronous context
    response_body = JSONResponse({"detail": str(exc)}, status_code=500)
    await log_api_response(
        request, req_body=pydantic_basemodel, res_body=response_body.body, status_code=500, function_name=str(url)
    )
    return response_body
