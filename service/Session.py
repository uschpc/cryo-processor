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
    #CF project_id
    _project_id = None
    
    # USC netid
    _user = None
    
    # session as the directory is named under /cryoem1/test/cryo-pegasus-test/[project_id]/sessions/[user]/[session_id]
    _session_id = None
 
    # list of potenatial states for tracking
    _STATE_UNKNOWN = "unknown"
    _STATE_NEEDS_PROCESSING = "needs_processing"
    _STATE_PROCESSING_START = "processing_start"
    _STATE_PROCESSING = "processing"
    _STATE_PROCESSING_COMPLETE = "processing_complete"
    _STATE_PROCESSING_FAILURE = "processing_failure"
    _STATE_INCOMPLETE_OR_EMPTY = "incomplete_or_empty"

    # state
    _state = None
    _percent = -1
    _no_of_processed = 0
    _no_of_failed = 0
    _percent_current_cycle = 0
    _next_processing_time = 0
    _no_of_raw = 0


    def __init__(self, config, project_id, user, session_id):
        self._config = config
        self._project_id = project_id
        self._user = user
        self._session_id = session_id
        self._session_dir = os.path.join(config.get('general', 'session_dir'), self._project_id, "sessions", self._user, self._session_id)
        log.info("using _session_dir dir %s"%(self._session_dir))
        self._wf_dir = os.path.join(self._session_dir, 'workflow')
        self._processed_dir = os.path.join(self._session_dir, 'processed')
        self._run_dir = os.path.join(self._wf_dir, 'motioncor2')
        self._scratch_dir = os.path.join(self._wf_dir, 'scratch')
        self.rawdatadirs=glob.glob(os.path.join(os.path.join(self._session_dir, "raw"), "*"))
        log.info("using rawdatadirs dirs %s"%(' '.join(self.rawdatadirs)))

        
        self._state = self._STATE_UNKNOWN

        # defaults to get us started
        self.basename_prefix = 'FoilHole'
        self.basename_suffix = 'fractions'
        self.basename_extension = 'tiff'
        self.raw_location = ""
        self.possible_raw_files = ""
        
        #handling files for processing moved here
        self._gainref_done = False
        self._gain_ref_fn = []
        self._defect_map_done = False
        self._defect_map_fn = []
        #list of raw files (read from processed directory)
        self._file_list = []
        #list of already processed files to not process them again (read from processed directory)
        self._processed_files_list = []
        #list of files to process in a cycle
        self._file_list_to_process = []
        #filenames sent for processing
        self._sent_for_processing = []
        
        

    def is_valid(self):
        return os.path.exists(self._session_dir)


    def is_processing(self):
        return self._state == self._STATE_PROCESSING_START or self._state == self._STATE_PROCESSING


    def get_state(self):
        return {
            "project_id": self._project_id,
            "user": self._user,
            "session_id": self._session_id,
            "state": self._state,
            "next_processing_time": self._next_processing_time
        }


    def count_raw_files(self):
        if self.raw_location != "" and self.possible_raw_files != "":
            log.info("using raw_location dir %s and %s as regex"%(self.raw_location,self.possible_raw_files))
            self._file_list = self._find_files(self.raw_location[0], self.raw_location[1])
            log.info("No. of raw files in (shortcut) %i"%len(self._file_list))
            return len(self._file_list)
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
                        flist = self._find_files(raw_location[0], raw_location[1])
                        if len(flist)>=1:
                            self._file_list=flist
                            self.raw_location = raw_location
                            self.possible_raw_files = possible_raw_files
                            log.info("RAW files are in %s"%os.path.join(raw_location[0],raw_location[1]))
                            log.info("No. of raw files %i"%len(self._file_list))
                            break
                    else:
                        continue
                    break
                #log.info("RAW files are in %s"%os.path.join(os.path.join(self._session_dir, "raw")))
                #log.info("No. of raw files %i"%len(self._file_list))
                return len(self._file_list)
            except Exception as e:
                log.info(e)
                log.info("There is an issue with determining raw_location")
                return 0
      

    def count_processed_files(self):
        try:
            pf = self._find_files(self._processed_dir,"*DW.mrc")
            log.info("processed files are in: %s"%self._processed_dir)
            log.info("No. of processed files %i"%len(pf))
            self._processed_files_list=pf
            return len(pf)
        except Exception as e:
            log.info(e)
            log.info("self._session_dir is not set yet")
            return 0
        

    def get_status(self):
    
        response = {
            "state": self._state,
            "percent_done_total": self._percent,
            "percent_current_cycle": self._percent_current_cycle,
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
        self._sent_for_processing = []
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
        log.info("Workflow wf._submit_dir is: {}".format(wf._submit_dir))
        try:
            status = wf.get_status()
            status = status['dags']['root']
            log.info("1-status {}".format(status))
        except:
            log.info("Unable to get workflow status")
            status = None
            pass
       
        # logic to match the web ui expectations 
        #if status is None or "totals" not in status:
        if status is None:
            self._no_of_succeeded = 0
            self._no_of_failed = 0
            self._percent_current_cycle = 0
        else:
            log.info("2-status {}".format(status))
            self._no_of_succeeded = status['succeeded']
            self._no_of_failed = status['failed']
            #self._percent_current_cycle = status['dags']['root']['percent_done']
            self._percent_current_cycle = status['percent_done']

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
            self._next_processing_time = time.time() + 120
        else:
            return False
        
        # if we get here, it is time to submit a new workflow 
        log.info("A new workflow is required. Submitting now ...")
        self._state = self._STATE_PROCESSING

        try:
            log.info("removing run_dir: {}".format(self._run_dir))
            shutil.rmtree(self._run_dir)
        except:
            log.info("FAILED: removing run_dir: {}".format(self._run_dir))
            pass
        try:
            log.info("removing _scratch_dir: {}".format(self._scratch_dir))
            shutil.rmtree(self._scratch_dir)
        except:
            log.info("FAILED: removing _scratch_dir: {}".format(self._scratch_dir))
            pass
        
        self.wf = PipelineWorkflow(self._config.get("general", "base_dir"),
                                    self._wf_dir,
                                    self.rawdatadirs,
                                    self._processed_dir,
                                    debug=self._config.getboolean("general", "debug"),
                                    glite_arguments=self._config.get("params", "glite_arguments"),
                                    gctf_glite_arguments=self._config.get("params", "gctf_glite_arguments"),
                                    maxjobs=self._config.get("params", "maxjobs"),
                                    debug_maxjobs=self._config.get("params", "debug_maxjobs"),
                                    partition=self._config.get("params", "partition"),
                                    account=self._config.get("params", "account"),
                                    pgss_stgt_clusters=self._config.get("params", "pegasus_stageout_clusters"),
                                    cluster_size=self._config.get("params", "cluster_size"),
                                    no_of_files_to_proc_in_cycle=self._config.getint("params", "no_of_files_to_proc_in_cycle"),
                                    )
        try:
            #prepare gain reference jobs (to ensure we are doing it only once)
            #check if there is one already, if not process
            #check if gainrref was processed already
            gr_sr_flipy = self._find_files(self._processed_dir, '*_sr.flipy.mrc')
            gr_sr = self._find_files(self._processed_dir, '*_sr.mrc')
            gr_std_flipy = self._find_files(self._processed_dir, '*_std.flipy.mrc')
            gr_std = self._find_files(self._processed_dir, '*_std.mrc')
            if len(gr_sr_flipy) != 0 and len(gr_sr) != 0 and len(gr_std_flipy) != 0 and len(gr_std) != 0:
                self.gr_sr_flipy = gr_sr_flipy[0]
                self.gr_sr = gr_sr[0]
                self.gr_std_flipy = gr_std_flipy[0]
                self.gr_std = gr_std[0]
                self._gainref_done = True
            if self._gainref_done == False:
                #Try to find Gain reference file - it might not be a part of the dataset, 
                #so we must take it into account.
                #define Gain reference Super resolution input and output filename
                log.info("self.rawdatadirs {}".format(self.rawdatadirs))
                log.info("looking for gain reference")
                possible_gf_files_regexes=['*_gain.tiff','*.gain']
                #add user provided optional regex:
                if self.rawgainref!=None:
                    possible_gf_files_regexes.append(self.rawgainref)
                raw_gain_ref_path=None
                for i in self.rawdatadirs:
                    for possible_gf in possible_gf_files_regexes:
                        log.info("searching gain ref here: {} with {} regex".format(i, possible_gf))
                        raw_gain_ref_path = self._find_files(os.path.join(i,"**"), possible_gf)
                        if len(raw_gain_ref_path)>=1:
                            self._gain_ref_fn=raw_gain_ref_path
                            break
                    else:
                        continue
                    break
            # mark as incomplete in case of the gainref missing
            # if len(self._gain_ref_fn)==0:
                # pass
            
            
            #prepare defect map jobs (to ensure we are doing it only once)
            #check if there is one already, if not process     
            dmf = self._find_files(self._processed_dir, '*Map.m1.mrc')
            if len(dmf) != 0:
                self.dmf = dmf[0]
                self._defect_map_done = True
            if self._defect_map_done == False:
                #Try to find Defect Map file - it might not be a part of the dataset; file is not needed for now
                log.info("looking for Defect Map")
                possible_dm_files_regexes=['*Map.m1.dm4']
                raw_defect_map_path=None
                if self.rawdefectsmap!=None:
                    possible_dm_files_regexes.append(self.rawdefectsmap)
                #check if dm was processed already
                for possible_dm in possible_dm_files_regexes:
                    raw_defect_map_path = self._find_files(os.path.join(self._processed_dir,"**"), possible_dm)
                    if len(raw_defect_map_path)>=1:
                        self._defect_map_fn=raw_defect_map_path
                        break
                raw_defect_map_path=None
                for i in self.rawdatadirs:
                    for possible_dm in possible_dm_files_regexes:
                        raw_defect_map_path = self._find_files(os.path.join(i,"**"), possible_dm)
                        if len(raw_defect_map_path)>=1:
                            log.info("searching defect map here: {} with {} regex".format(i, possible_dm))
                            self._defect_map_fn=raw_defect_map_path
                            break
                    else:
                        continue
                    break

            #prepare a list of files for processing
            #list of files should be here from first status check and counting raw files
            #ensure the list order (oldest files should be first after sort)
            self._file_list.sort()
            log.info("self._file_list BEFORE TRIM: len {}".format(len(self._file_list)))
            self._file_list_to_process=[]
            for x in self._file_list:
                if x not in self._sent_for_processing:
                    self._file_list_to_process.append(x)
            self._file_list_to_process=self._file_list_to_process[:self._config.getint("params", "no_of_files_to_proc_in_cycle")]
            log.info("self._file_list_to_process: len {}".format(len(self._file_list_to_process)))
            log.info("self._sent_for_processing BEFOR: len {}".format(len(self._sent_for_processing)))
            #mark as incomplete if no files are found
            # if len(self._file_list_to_process)==0:
                # pass
            
            
            for x in self._file_list_to_process:
                if x not in self._sent_for_processing:
                    self._sent_for_processing.append(x)
            log.info("self._sent_for_processing AFTER: len {}".format(len(self._sent_for_processing)))
            
            
            
        except Exception as e:
            log.exception(e)
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
        log.info(" ... searching for {}".format(search_path))
        log.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files
