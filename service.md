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

    [api]
    
    port = 8112
    token = somesecret
    
    [data]
    
    session_dir = /project/cryoem/sessions


Then simply start the service on discovery1 by running

    cd service/
    ./runme.sh


## Interacting with the Service

The endpoints available are:

 * `/list-sessions`
 * `/start-processing`
 * `/stop-processing`
 * `/status`

For example, to start a new workflow:

    curl 'localhost:8112/start-processing?user=rynge&session=K3_2-20210322121212&access_token=somesecret'


