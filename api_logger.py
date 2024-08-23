import inspect
import logging
from logging.handlers import RotatingFileHandler
import traceback
import json
from datetime import datetime, timezone, timedelta
import uuid
from fastapi import Request, HTTPException
from models import ApiLog

logs_directory = "logs"

def setup_logger(log_file, name, max_log_size=100 * 1024 * 1024, backup_count=3):
    log_file = f"{logs_directory}/" + log_file
    handler = RotatingFileHandler(
        log_file, maxBytes=max_log_size, backupCount=backup_count
    )
    formatter = logging.Formatter(
        "'log_timestamp':%(asctime)s%(msecs)d - %(name)s - %(levelname)s - %(message)s - %(exc_text)s"
    )

    console_formatter = logging.Formatter(
        "%(asctime)s%(msecs)d - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger("logger.log", "logger")

async def log_api_response(
    request: Request,
    status_code=200,
    req_body={},
    res_body={},
    function_name="",
    personalized_message="",
):
    try:
        function_name = (
            function_name
            if function_name
            else inspect.currentframe().f_back.f_code.co_name
        )
        api_title = function_name.split("?")[0].replace("_", " ").title() + " API Log"
        api_title = "/".join(api_title.split("/")[-2:])
        req_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))

        data = {
            "req_body": str(req_body),
            "res_body": str(res_body),
            "path_params": str(request.path_params),
            "query_params": str(request.query_params),
            "headers": dict(request.headers),
            "api_url": str(function_name),
            "api_title": api_title,
            "personalized_message": personalized_message,
            "client_ip": str(request.client),
            "status_code": status_code,
            "req_time": str(req_time),
            "status": "Success" if status_code == 200 else "Failure",
        }

        if data["status"] == "Failure":
            data["traceback"] = traceback.format_exc()

        data["headers"] = json.dumps(data["headers"])

        api_log = ApiLog(**data)
        await api_log.insert()

    except (Exception, HTTPException) as e:
        logger.error("An error occurred while logging API response: {}".format(str(e)))
