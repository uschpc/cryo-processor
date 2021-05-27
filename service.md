# CryoEM Service


## Goals

The goal is to create a service which is can be used from the web user
interface to get status, and start/stop CryoEM processing.

This is currently a mockup, and will be used to drive discussion and
future development decisions.


## Directory Layout

The assumption here is that there is one directory for the data,
organzied then by user and session. In this example, the top level
data directory is `/project/cryoem/sessions/` and under there the
following directories exist:

    ├── csul
    │   └── K3_2-20210427113000
    │       └── raw
    └── rynge
        ├── K3_2-20210202000000
        │   └── raw
        └── K3_2-20210322121212
            ├── raw
            └── workflow
                └── motioncor2

The session names, such as `K3_2-20210427113000` are just made up. The
`raw` directory is the data as it comes from the instrument, and the
`workflow` directory is created when processing is requested.


## Runnning the Service

Create a config file under `~/.cryoem.conf` with the contents like:

    [general]
    
    debug = False
    session_dir = /project/cryoem/sessions
    
    [api]
    
    port = 8112
    token = somesecret


Then simply start the service on discovery1 by running

    cd service/
    ./runme.sh


## Interacting with the Service

The endpoints available are:

 * `/{user}/sessions` (gives a list of sessions)
 * `/{user}/session/{session_id}` (gives status of a session)
 * `/{user}/session/{session_id}/start-processing`
 * `/{user}/session/{session_id}/stop-processing`

For example, to start a new workflow:

    $ curl 'localhost:8112/rynge/session/K3_2-2021032212121/start-processing?access_token=somesecret'

To get status:

    $ curl 'localhost:8112/rynge/session/K3_2-20210322121212?access_token=somesecret' | python -m json.tool
    {
        "dagname": "motioncor2-0.dag",
        "failed": 1,
        "percent_done": 11.1,
        "post": 0,
        "pre": 0,
        "queued": 0,
        "ready": 0,
        "state": "Failure",
        "succeeded": 2,
        "unready": 15
    }


