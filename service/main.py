#!/usr/bin/python3

from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.logger import logger

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

import uvicorn

from Pegasus.api import *

import os
import logging
import pprint
from logging.config import dictConfig

from Config import Config
from PipelineWorkflow import PipelineWorkflow


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "cryoem": {"handlers": ["default"], "level": "DEBUG"},
        "pegasus.client": {"handlers": ["default"], "level": "INFO"},
    },
}

dictConfig(log_config)

logger = logging.getLogger('cryoem')

config = Config()

API_KEY_NAME = "access_token"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header)
):

    if api_key_query == config.get('api', 'token'):
        return api_key_query
    elif api_key_header == config.get('api', 'token'):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


@app.get("/list-sessions")
async def list_sessions(user: str, api_key: APIKey = Depends(get_api_key)):
    response = {}

    for d in os.listdir(os.path.join(config.get('data', 'session_dir'), user)):
        response[d] = {'placeholder': 'details in here'}

    if len(response) == 0:
        response = {"error": "No sessions found"}
    return response


@app.get("/status")
async def start_processing(user: str, session: str, api_key: APIKey = Depends(get_api_key)):
    # we should have some kind of state map here
    response = {}
    session_dir = os.path.join(config.get('data', 'session_dir'), user, session)
    wf_dir = os.path.join(session_dir, 'workflow', 'motioncor2')

    if not os.path.exists(wf_dir):
        return {"status": "not_submitted"}

    # this needs some work....
    wf = Workflow("CryoEM")
    wf._submit_dir = wf_dir
    response = wf.status()
    logger.info(pprint.pformat(response))

    return response


@app.get("/start-processing")
async def start_processing(user: str, session: str, api_key: APIKey = Depends(get_api_key)):
    response = {}
    session_dir = os.path.join(config.get('data', 'session_dir'), user, session)
    wf_dir = os.path.join(session_dir, 'workflow')

    if os.path.exists(wf_dir):
        # do we want the API do this, or should it be a human only step?
        for root, dirs, files in os.walk(wf_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(wf_dir)

    wf = PipelineWorkflow(wf_dir)
    try:
        wf.submit_workflow()
    except Exception as e:
        logger.error(e)
        return {"error": "Unable to submit workfork"}

    return {"result": "ok"}


def main():
    uvicorn.run("main:app",
                host = '0.0.0.0',
                port = config.getint('api', 'port', fallback=8112),
                reload = True,
                debug = True, 
                workers = 3)


if __name__ == '__main__':
    main()

