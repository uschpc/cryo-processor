#!/usr/bin/env python3

import logging
import os
import pprint
import shutil
import time
import glob

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
    _STATE_PROCESSING_START = "processing_start"
    _STATE_PROCESSING = "processing"
    _STATE_PROCESSING_COMPLETE = "processing_complete"
    _STATE_PROCESSING_FAILURE = "processing_failure"

    # state
    _state = None
    _percent = -1
    _no_of_processed = 0
    _no_of_failed = 0
    _next_processing_time = 0
    _no_of_raw = 0


    def __init__(self, config, user, session_id):
        self._config = config
        self._user = user
        self._session_id = session_id
        self._session_dir = os.path.join(config.get('general', 'session_dir'), self._user, self._session_id)

        self._wf_dir = os.path.join(self._session_dir, 'workflow')
        self._run_dir = os.path.join(self._wf_dir, 'motioncor2')
        self._scratch_dir = os.path.join(self._wf_dir, 'scratch')
        self._state = self._STATE_UNKNOWN

        # defaults to get us started
        self.basename_prefix = 'FoilHole'
        self.basename_suffix = 'fractions'
        self.basename_extension = 'tiff'
        self.raw_location = ""
        self.possible_raw_files = ""

    def is_valid(self):
        return os.path.exists(self._session_dir)


    def is_processing(self):
        return self._state == self._STATE_PROCESSING_START or self._state == self._STATE_PROCESSING


    def get_state(self):
        return {
            "user": self._user,
            "session_id": self._session_id,
            "state": self._state,
            "next_processing_time": self._next_processing_time
        }


    def count_raw_files(self):
        if self.raw_location != "" and self.possible_raw_files != "":
            log.info("using raw_location dir %s and %s as regex"%(self.raw_location,self.possible_raw_files))
            flist = self.find_files2(raw_location[0], raw_location[1])
            log.info("No. of raw files in (shortcut) %i"%len(flist))
            return len(flist)
        else:
            try:
                possible_raw_files_regexes=['FoilHole*fractions.tiff','FoilHole*fractions.mrc','FoilHole*EER.eer']
                if self.basename_prefix!=None and self.basename_suffix!=None and self.basename_extension!=None:
                    possible_raw_files_regexes.append("%s*%s.%s"%(self.basename_prefix,self.basename_suffix,self.basename_extension))
            
                for i in self.rawdatadirs:
                    log.info("input dir %s"%i)
                    for possible_raw_files in possible_raw_files_regexes:
                        log.info("Possible RAW regex %s"%possible_raw_files)
                        raw_location=(os.path.join(i, "**"), possible_raw_files)
                        self.correct_input_dir=i
                        flist = self.find_files2(raw_location[0], raw_location[1])
                        if len(flist)>=1:
                            file_list=flist
                            self.raw_location = raw_location
                            self.possible_raw_files = possible_raw_files
                            log.info("RAW files are in %s"%raw_location)
                            log.info("No. of raw files %i"%len(file_list))
                            break
                    else:
                        continue
                    break
                
                
            
                # for i in glob.glob(os.path.join(os.path.join(self._session_dir, "raw"), "*")):
                    # raw_location=(os.path.join(i, "**"),
                            # "%s*%s.%s"%(self.basename_prefix,self.basename_suffix,self.basename_extension))
                    # correct_input_dir=i
                    # flist = self._find_files(raw_location[0], raw_location[1])
                    # if len(flist)>=1:
                        # file_list=flist
                        # self.raw_location = raw_location
                        # break
                # else:
                    # flist = self._find_files(self.raw_location[0], self.raw_location[1])
                    
                    
                log.info("RAW files are in %s"%os.path.join(os.path.join(self._session_dir, "raw")))
                log.info("No. of raw files %i"%len(file_list))
                return len(file_list)
            except Exception as e:
                log.info(e)
                log.info("There is an issue with determining raw_location")
                return 0
      

    def count_processed_files(self):
        try:
            pf = self._find_files(os.path.join(self._session_dir, "processed"),"*DW.mrc")
            log.info("processed files are in: %s"%os.path.join(os.path.join(self._session_dir, "processed")))
            log.info("No. of processed files %i"%len(pf))
            return len(pf)
        except Exception as e:
            log.info(e)
            log.info("self._session_dir is not set yet")
            return 0
        

    def get_status(self):
    
        response = {
            "state": self._state,
            "percent_done": self._percent,
            "failed_jobs": self._no_of_failed,
            "processed_files": self._no_of_processed,
            "raw_files": self._no_of_raw
        }
    
        return response

    
    def start_processing(self, apix, fmdose, kev, superresolution, **data):
        
        self.apix = apix # pixel size
        self.fmdose = fmdose # dose in e-/A^2 per frame
        self.kev = kev # voltage
        self.superresolution = superresolution # bool
        log.info("apix: %s"%self.apix)
        log.info("fmdose: %s"%self.fmdose)
        log.info("kev: %s"%self.kev)
        log.info("superresolution: %s"%self.superresolution)
        
        #self.rawgainref = data.get(rawgainref, default=None)
        try: self.rawgainref = data[rawgainref] # ls like regex to pickup raw gain ref file
        except: self.rawgainref = None
        #self.rawdefectsmap = data.get(rawdefectsmap, default=None)
        try: self.rawdefectsmap = data[rawdefectsmap] # ls like regex to pickup basename prefix
        except: self.rawdefectsmap = None
        #self.basename_prefix = data.get(basename_prefix, default=None)
        try: self.basename_prefix = data[basename_prefix] # ls like regex to pickup basename prefix
        except: self.basename_prefix = None
        #self.basename_suffix = data.get(basename_suffix, default=None)
        try: self.basename_suffix = data[basename_suffix] # ls like regex to pickup basename suffix (no underscores)
        except: self.basename_suffix = None
        #self.basename_extension = data.get(basename_extension, default=None)
        try: self.basename_extension = data[basename_extension] # ls like regex to pickup basename extension
        except: self.basename_extension = None
        #self.throw = data.get(throw, default=None)
        try: self.throw=data[throw] # how many frames discard from the top
        except: self.throw = None
        #self.trunc = data.get(trunc, default=None)
        try: self.trunc = data[trunc] # how many frames keep
        except: self.trunc=None
        #self.particle_size = data.get(particle_size, default=None)
        try: self.particle_size = data[particle_size] # <-- future; stage 2
        except: self.particle_size = None
        
        if self.rawgainref!=None:
            log.info("rawgainref: %s"%self.rawgainref)
        if self.rawdefectsmap!=None:
            log.info("rawdefectsmap: %s"%self.rawdefectsmap)
        if self.basename_prefix!=None:
            log.info("basename_prefix: %s"%self.basename_prefix)
        if self.basename_suffix!=None:
            log.info("basename_suffix: %s"%self.basename_suffix)
        if self.basename_extension!=None:
            log.info("basename_extension: %s"%self.basename_extension)
        if self.throw!=None:
            log.info("throw: %s"%self.throw)
        if self.trunc!=None:
            log.info("trunc: %s"%self.trunc)
        if self.particle_size!=None:
            log.info("particle_size: %s"%self.particle_size)
        self._state = self._STATE_PROCESSING_START
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
            self._update_processing()
        elif self._state == self._STATE_NEEDS_PROCESSING:
            self._update_processing()
        elif self._state == self._STATE_PROCESSING_START:
            self._update_processing()
        elif self._state == self._STATE_PROCESSING:
            self._update_processing()
        else:
            # all other states
            pass


    def _update_processing(self):

        self._no_of_raw = self.count_raw_files()
        self._no_of_processed = self.count_processed_files()
        
        self._percent = 0
        if self._no_of_raw > 0:
            self._percent = round((float(self._no_of_processed) / self._no_of_raw) * 100.0)

        # get the status from Pegasus
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
        wf = Workflow("motioncor2")
        wf._submit_dir = self._run_dir
        try:
            status = wf.get_status()
            status = status['dags']['root']
        except:
            log.info("Unable to get workflow status")
            status = None
            pass
       
        # logic to match the web ui expectations 
        if status is None or "totals" not in status:
            self._no_of_succeeded = 0
            self._no_of_failed = 0
        else:
            self._no_of_succeeded = status['succeeded']
            self._no_of_failed = status['failed']

        # is the workflow already running?
        if status is not None:
            if "state" in status:
                log.info("Workflow status is: {}".format(status["state"]))

            if "state" in status and status["state"] == "Running":
                return False

            # skip this if we are asked to start a new wf
            if self._state != self._STATE_PROCESSING_START:
                if "state" in status and status["state"] == "Failure":
                    self._next_processing_time = 0
                    self._state = self._STATE_PROCESSING_FAILURE
                    return False

        # end condition
        if (self._no_of_processed == self._no_of_raw) and (self._no_of_processed != 0):
            self._next_processing_time = 0
            self._state = self._STATE_PROCESSING_COMPLETE
            return
 
        # time to submit a new one? 
        if self._next_processing_time > 0 and \
           self._next_processing_time < time.time():
            # space the workflows a little bit in case of failure
            self._next_processing_time = time.time() + 60
        else:
            return False
        
        # if we get here, it is time to submit a new workflow 
        log.info("A new workflow is required. Submitting now ...")
        self._state = self._STATE_PROCESSING

        try:
            shutil.rmtree(self._run_dir)
        except:
            pass
        try:
            shutil.rmtree(self._scratch_dir)
        except:
            pass
        self.rawdatadirs=glob.glob(os.path.join(os.path.join(self._session_dir, "raw"), "*"))
        self.wf = PipelineWorkflow(self._config.get("general", "base_dir"),
                                    self._wf_dir,
                                    self.rawdatadirs,
                                    os.path.join(self._session_dir, "processed"),
                                    debug=self._config.getboolean("general", "debug"),
                                    glite_arguments=self._config.get("params", "glite_arguments"),
                                    maxjobs=self._config.get("params", "maxjobs"),
                                    debug_maxjobs=self._config.get("params", "debug_maxjobs"),
                                    partition=self._config.get("params", "partition"),
                                    account=self._config.get("params", "account"),
                                    pgss_stgt_clusters=self._config.get("params", "pegasus_stageout_clusters"),
                                    cluster_size=self._config.get("params", "cluster_size"),
                                    no_of_files_to_proc_in_cycle=self._config.getint("params", "no_of_files_to_proc_in_cycle"),
                                    )
        try:
            self.wf.set_params(self)
        except Exception as e:
            log.exception(e)
        try:
            self.wf.submit_workflow()
        except Exception as e:
            log.exception(e)

        return True


    def _find_files(self, root_dir, regex):
        '''
        Returns sorted list of files matching regex = root_dir+/+regex (similar to ls)
        Much faster than find_files
        eg. f=find_files2("/project/cryoem/K3_sample_dataset/20210205_mutant/Images-Disc1", "*/Data/*_fractions.tiff") to get all files
        '''
        search_path=os.path.join(root_dir,regex)
        found_files=glob.glob(search_path, recursive=True)
        log.info(" ... searching for {}".format(search_path))
        log.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files

    def _find_files3(self, regex):
        '''
        Returns sorted list of files matching regex = root_dir+/+regex (similar to ls)
        Much faster than find_files
        eg. f=find_files2("/project/cryoem/K3_sample_dataset/20210205_mutant/Images-Disc1", "*/Data/*_fractions.tiff") to get all files
        '''

        found_files=glob.glob(regex, recursive=True)
        logger.info(" ... searching for {}".format(search_path))
        logger.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files
