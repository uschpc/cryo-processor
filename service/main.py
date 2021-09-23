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

import asyncio
import concurrent.futures
import contextlib
import json
import logging
import os
import pprint
import threading
import time
from logging.config import dictConfig

from Config import Config
from Session import Session


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
    },
}

dictConfig(log_config)

log = logging.getLogger('cryoem')

config = Config()

API_KEY_NAME = "access_token"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

app.state.keep_running = True
app.state.sessions = {}


def main_loop():

    log.info("In main(), id is {}".format(id(app.state.sessions)))
    
    load_state()

    # this is the main event loop for general use
    while app.state.keep_running:
        log.info("Waking up main thread")

        # check on all the tracked sessions
        # fix for
        # future: <Future finished exception=RuntimeError('dictionary changed size during iteration',)>
        
        #log.info("Checking on SESSIONS {}".format(app.state.sessions))
        to_del = []
        for sid, session in app.state.sessions.items():
            log.info("Checking on session {}".format(sid))
            session.update()
            log.info(pprint.pformat(session.get_status()))

            if not session.is_valid():
                to_del.append(sid)
        
        # clean up expired sessions
        for sid in to_del: del app.state.sessions[sid]

        # save periodically?   
        save_state()

        time.sleep(60)

    save_state()


def load_state():
    sfilename = os.path.join(os.environ['HOME'], '.cryoem.state')
    if os.path.exists(sfilename):
        with open(sfilename) as f:
            j = json.load(open(sfilename))
            for sid, session in j.items():
                app.state.sessions[sid] = Session(config, session["user"], session["session_id"])


def save_state():
    j = {}
    for sid, session in app.state.sessions.items():
        j[sid] = session.get_state()
    with open(os.path.join(os.environ['HOME'], '.cryoem.state'), 'w') as f:
        json.dump(j, f)


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


@app.on_event("startup")
async def startup():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, main_loop)
    #with concurrent.futures.ThreadPoolExecutor() as pool:
    #    loop.run_in_executor(pool, main_loop)


@app.on_event("shutdown")
async def shutdown():
    app.state.keep_running = False


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
    
    log.info("In sessions(), id is {}".format(id(app.state.sessions)))

    response = {"sessions": []}

    for d in os.listdir(os.path.join(config.get('general', 'session_dir'), user)):
        response["sessions"].append({"session_id": d})

    return response


@app.get("/{user}/session/{session_id}")
async def session_status(user: str, session_id: str, api_key: APIKey = Depends(get_api_key)):
    
    key = "{}/{}".format(user, session_id)
    if key in app.state.sessions:
        s = app.state.sessions[key]
    else:
        s = Session(config, user, session_id)
        if not s.is_valid():
            # should this be a 404?
            return {"state": "no_such_session"}
        app.state.sessions[key] = s

    return s.get_status()


@app.post("/{user}/session/{session_id}/start-processing")
async def start_processing(user: str,
                           session_id: str, 
                           apix: float,
                           fmdose: float,
                           kev: int,
                           #rawgainref: str,
                           #rawdefectsmap: str,
                           #basename_prefix: str,
                           #basename_suffix: str,
                           #basename_extension: str,
                           #throw: int,
                           #trunc: int,
                           #particle_size: int,
                           superresolution: bool,
                           api_key: APIKey = Depends(get_api_key)
                           ):
# async def start_processing(user: str,
                           # session_id: str, 
                           # api_key: APIKey = Depends(get_api_key)
                           # **kwargs ):
    key = "{}/{}".format(user, session_id)
    if key in app.state.sessions:
        s = app.state.sessions[key]
    else:
        s = Session(config, user, session_id)
        if not s.is_valid():
            # should this be a 404?
            return {"results": "no_such_session"}
        app.state.sessions[key] = s

    if not s.is_processing():
        s.start_processing(
            apix = apix,
            fmdose = fmdose,
            kev = kev,
            #rawgainref = rawgainref,
            #rawdefectsmap = rawdefectsmap,
            #basename_prefix = basename_prefix,
            #basename_suffix = basename_suffix,
            #basename_extension = basename_extension,
            #throw = throw,
            #trunc = trunc,
            #particle_size = particle_size,
            superresolution = superresolution,
             )

    return {"result": "ok"}


@app.post("/{user}/session/{session_id}/stop-processing")
async def stop_processing(user: str,
                          session_id: str,
                          api_key: APIKey = Depends(get_api_key)):
    key = "{}/{}".format(user, session_id)
    if key in app.state.sessions:
        s = app.state.sessions[key]
    else:
        s = Session(config, user, session_id)
        if not s.is_valid():
            # should this be a 404?
            return {"results": "no_such_session"}
        app.state.sessions[key] = s

    s.stop_processing()

    return {"result": "ok"}


if __name__ == '__main__':
    uvicorn.run(
            "main:app",
            host = '0.0.0.0',
            port = config.getint('api', 'port', fallback=8112),
            reload = False,
            log_level = "info",
            loop = "asyncio",
            workers = 1
    )


