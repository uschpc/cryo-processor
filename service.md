# CryoEM Service


## Goals

The goal is to create a service which is can be used from the web user
interface to get status, and start/stop CryoEM processing.

This is currently a mockup, and will be used to drive discussion and
future development decisions.


## Directory Layout

The assumption here is that there is one directory for the data,
organzied then by user and session. In this example, the top level
data directory is `/cryoem1/project_id/sessions/` and under there the
following directories exist:

    ├── ttrojan1
    │   └── 20210427113_usc_ttrojan_k3_mysample1
    │       └── raw
    └── ttrojan2
        ├── 20210627113_usc_ttrojan_k3_mysample2
        │   └── raw
        └── 20210727113_usc_ttrojan_k3_mysample3
            ├── raw
            └── workflow
                └── motioncor2

The session names, such as `20210427113_usc_ttrojan_k3_mysample1` are following the scheme. The
`raw` directory is the data as it comes from the instrument, and the
`workflow` directory is created when processing is requested. The output is being saved 
in the `processed` directory created once the processing is complete.


## Runnning the Service

Create a config file under `~/.cryoem.conf` with the contents like:

    [general]
    
    debug = False
	#full session dir is /cryoem1/<project_id>/sessions/<uscnetid>/<session_id>
    session_dir = /cryoem1
    
    [api]
    
    port = 8115
	#production is running on 8113
    token = somesecret
    
    [params]
    
    maxjobs = 100
    debug_maxjobs = 50
    partition = cryoem
    account = osinski_703
    glite_arguments = --gres=gpu:a40:4 --exclusive --exclude=e17-[20-24],d23-[11-12],a13-06
	gctf_glite_arguments = --gres=gpu:a40:4 --exclusive --exclude=e17-[20-24],d23-[11-12],a13-06
	glite_for_cryoem_partition = --exclude=d23-[11-12],a13-06
    cluster_size = 10
    no_of_files_to_proc_in_cycle = 100
	#Optional for debug. 
	#When not defined here it is being adjusted automatically 
	#to the number of files processed in a cycle
	#pegasus_stageout_clusters = 25



The service is added as a systemd service, and starts with the system. 
For the debug you can simply start the service on the login node by running:

    cd service/
    ./runme.sh


## Interacting with the Service

The endpoints available are:

 * `/{project_id}/{user}/sessions` (gives a list of sessions)
 * `/{project_id}/{user}/session/{session_id}` (gives status of a session)
 * `/{project_id}/{user}/session/{session_id}/start-processing`
 * `/{project_id}/{user}/session/{session_id}/stop-processing`
 * `/{project_id}/{user}/session/{session_id}/resume-processing`

For example, to start a new workflow:

    $ curl 'localhost:8112/ttrojan_123/ttrojan/session/20210427113_usc_ttrojan_k3_mysample1/start-processing?apix=0.813&fmdose=1.224&kev=300&superresolution=False&access_token=somesecret'

To resume the workflow (after it stopped, because the microscope paused during the acquisition session)

    $ curl 'localhost:8112/ttrojan_123/ttrojan/session/20210427113_usc_ttrojan_k3_mysample1/start-processing?apix=0.813&fmdose=1.224&kev=300&superresolution=False&access_token=somesecret'

To get status:

    $ curl 'localhost:8112/ttrojan_123/ttrojan/session/20210427113_usc_ttrojan_k3_mysample1?access_token=somesecret' | python -m json.tool
    {
    "failed_jobs": 0,
    "percent_current_cycle": 100.0,
    "percent_done_total": 100,
    "processed_files": 2481,
    "raw_files": 2481,
    "state": "processing_complete"
    }



