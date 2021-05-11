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

import contextlib
import logging
import os
import pprint
import threading
import time
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

#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()


class Server(uvicorn.Server):
    '''
    see https://github.com/encode/uvicorn/issues/742
    '''

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


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


@app.get("/{user}/sessions",
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "sessions": [{"session_id": "K3_2-20210322121212"}]
                    }
                }
            }
        }
    }
)
async def sessions(user: str, api_key: APIKey = Depends(get_api_key)):
    response = {"sessions": []}

    for d in os.listdir(os.path.join(config.get('data', 'session_dir'), user)):
        response["sessions"].append({"session_id", d})

    return response


@app.get("/{user}/session/{session_id}")
async def session_status(user: str, session_id: str, api_key: APIKey = Depends(get_api_key)):
    # we should have some kind of state map here
    response = {}
    session_dir = os.path.join(config.get('data', 'session_dir'), user, session_id)
    wf_dir = os.path.join(session_dir, 'workflow', 'motioncor2')

    if not os.path.exists(wf_dir):
        return {"state": "not_submitted"}

    logger.info("Checking {} ...".format(wf_dir))

    # this needs some work....
    wf = Workflow("motioncor2")
    wf._submit_dir = wf_dir
    state = wf.get_status()
    #logger.info(pprint.pformat(response))
    
    if state is None or "totals" not in state:
        return {"state": "unknown"}

    response = state['dags']['root']

    return response


@app.get("/{user}/session/{session_id}/start-processing")
async def start_processing(user: str, session_id: str, api_key: APIKey = Depends(get_api_key)):
    response = {}
    session_dir = os.path.join(config.get('data', 'session_dir'), user, session_id)
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


@app.get("/{user}/session/{session_id}/stop-processing")
async def stop_processing(user: str, session_id: str, api_key: APIKey = Depends(get_api_key)):
    response = {}
    return response


def main():

    server_config = uvicorn.Config(
                "main:app",
                host = '0.0.0.0',
                port = config.getint('api', 'port', fallback=8112),
                reload = True,
                log_level = "info",
                loop = "asyncio")
    server = Server(config=server_config)

    with server.run_in_thread():
        # this is the main event loop for general use
        while True:
            time.sleep(10)



if __name__ == '__main__':
    main()

