#!/usr/bin/env python3

import logging
import os
import pprint
import shutil
import time

from Pegasus.api import *

from PipelineWorkflow import PipelineWorkflow

log = logging.getLogger('cryoem')


class Session:

    # USC netid
    _user = None

    # session as the directory is named under /project/cryoem/sessions/[user]/[session_id]
    _session_id = None
 
    # list of potenatial states for tracking
    _STATE_UNKNOWN = "unknown"
    _STATE_NEEDS_PROCESSING = "needs_processing"
    _STATE_PROCESSING = "processing"
    _STATE_PROCESSING_COMPLETE = "processing_complete"
    _STATE_PROCESSING_FAILURE = "processing_failure"

    # state
    _state = None
    _percent = -1
    _next_processing_time = 0


    def __init__(self, config, user, session_id):
        self._config = config
        self._user = user
        self._session_id = session_id

        self._session_dir = os.path.join(config.get('general', 'session_dir'), self._user, self._session_id)
        self._wf_dir = os.path.join(self._session_dir, 'workflow')
        self._run_dir = os.path.join(self._wf_dir, 'motioncor2')
        self._scratch_dir = os.path.join(self._wf_dir, 'scratch')

        self._state = self._STATE_UNKNOWN


    def is_valid(self):
        return os.path.exists(self._session_dir)


    def is_processing(self):
        return self._state == self._STATE_PROCESSING


    def get_state(self):
        return {
            "user": self._user,
            "session_id": self._session_id,
            "state": self._state,
            "next_processing_time": self._next_processing_time
        }


    def get_status(self):
    
        response = {
            "state": self._state,
            "percent_done": self._percent
        }
    
        return response


    def start_processing(self):
        self._state = self._STATE_PROCESSING
        self._next_processing_time = time.time()
    

    def stop_processing(self):
        self._state = self._STATE_NEEDS_PROCESSING
        self._next_processing_time = 0
        # also cancel any potential workflows
        wf = Workflow("motioncor2")
        wf._submit_dir = self._run_dir
        try:
            state = wf.remove()
        except:
            pass


    def update(self):
        '''
        This is called periodically and is used to check the status
        and see if there is any additional processing we need to do
        '''

        if self._state == self._STATE_UNKNOWN:
            self._update_unknown()
        elif self._state == self._STATE_NEEDS_PROCESSING:
            pass
        elif self._state == self._STATE_PROCESSING:
            self._update_processing()
        else:
            # all other states
            pass


    def _update_unknown(self):
        # try to determine the state

        wf = Workflow("motioncor2")
        wf._submit_dir = self._run_dir
        status = wf.get_status()

        # FIXME: how do we know we have completed?
 
        if status is None or "totals" not in status:
            self._state = self._STATE_NEEDS_PROCESSING
            self._percent = -1
            return
        else:
            self._state = self._STATE_PROCESSING
            self._percent = status['dags']['root']['percent_done']
            return


    def _update_processing(self):

        # get the status from Pegasus
        wf = Workflow("motioncor2")
        wf._submit_dir = self._run_dir
        status = wf.get_status()
    
        # {'dagname': 'motioncor2-0.dag',
        # 'failed': 0,
        # 'percent_done': 100.0,
        # 'post': 0,
        # 'pre': 0
        # 'queued': 0,
        # 'ready': 0,
        # 'state': 'Running',
        # 'succeeded': 22,
        # 'unready': 0}
       
        # FIXME: improve this logic to match the web ui expectations 
        if status is None or "totals" not in status:
            self._percent = -1
        else:
            self._state = self._STATE_PROCESSING
            self._percent = status['dags']['root']['percent_done']

        # is the workflow already running?
        if status is not None:
            if "state" in status and status["state"] == "Running":
                return False
 
        # time to submit a new one? 
        if self._next_processing_time > 0 and \
           self._next_processing_time < time.time():
            self._next_processing_time = 0
        else:
            return False
        
        # if we get here, it is time to submit a new workflow 
        log.info("A new workflow is required. Submitting now ...")

        try:
            shutil.rmtree(self._run_dir)
        except:
            pass
        try:
            shutil.rmtree(self._scratch_dir)
        except:
            pass
 
        self.wf = PipelineWorkflow(self._config.get("general", "base_dir"),
                                   self._wf_dir,
                                   os.path.join(self._session_dir, "raw"),
                                   os.path.join(self._session_dir, "processed"),
                                   debug=self._config.getboolean("general", "debug"))
        try:
            self.wf.submit_workflow()
        except Exception as e:
            log.exception(e)

        return True


