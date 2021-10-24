#!/usr/bin/env python3

import configparser
import logging
import os
import pprint
import random
import re
import sys
import glob
from pathlib import Path
from argparse import ArgumentParser

logger = logging.getLogger('cryoem')

# --- Import Pegasus API ------------------------------------------------------
from Pegasus.api import *


class PipelineWorkflow:
    wf = None
    sc = None
    tc = None
    props = None

    wf_name = None
    wf_dir = None
    inputs_dir = None
    

    # --- Init ----------------------------------------------------------------
    def __init__(self, base_dir, wf_dir, inputs_dir, outputs_dir, debug=False, partition="debug", account="osinski_703", glite_arguments="--gres=gpu:p100:2", gctf_glite_arguments="", maxjobs=100, debug_maxjobs=10, pgss_stgt_clusters=10, cluster_size=10, no_of_files_to_proc_in_cycle=-1):
        self.wf_name = "motioncor2"
        self.debug = debug
        logger.info("PipelineWorkflow init")
        logger.info("debug {}".format(self.debug))
        self.base_dir = base_dir
        self.wf_dir = wf_dir
        self.inputs_dir = inputs_dir
        self.outputs_dir = outputs_dir
        self.partition = partition
        self.account = account
        self.glite_arguments = glite_arguments
        self.gctf_glite_arguments = gctf_glite_arguments
        self.glite_for_cryoem_partition = "--nodelist=e17-[20-24],d23-[11-12]"
        self.pgss_stgt_clusters = pgss_stgt_clusters
        self.maxjobs = maxjobs
        self.debug_maxjobs = debug_maxjobs
        self.cluster_size = cluster_size
        self.no_of_files_to_proc_in_cycle = no_of_files_to_proc_in_cycle
        if self.debug:
            logger.info("sbase_dir {}".format(self.base_dir))
            logger.info("wf_dir {}".format(self.wf_dir))
            logger.info("inputs_dir {}".format(self.inputs_dir))
            logger.info("outputs_dir {}".format(self.outputs_dir))
            logger.info("partition {}".format(self.partition))
            logger.info("account {}".format(self.account))
            logger.info("glite_arguments {}".format(self.glite_arguments))
            logger.info("pgss_stgt_clusters {}".format(self.pgss_stgt_clusters))
            logger.info("maxjobs {}".format(self.maxjobs))
            logger.info("debug_maxjobs {}".format(self.debug_maxjobs))
            logger.info("cluster_size {}".format(self.cluster_size))
            logger.info("no_of_files_to_proc_in_cycle {}".format(self.no_of_files_to_proc_in_cycle))
        
        self.no_of_processed = 0
        self.no_of_raw = 0
        self.gainref_done = False
        self.defmap_done = False
        #self.processed = []
        

    # --- Write files in directory --------------------------------------------
    def write(self):
        if not self.sc is None:
            self.sc.write()
        self.props.write()
        self.tc.write()
        self.rc.write()
        self.wf.write()

    # --- Configuration (Pegasus Properties) ----------------------------------
    def create_pegasus_properties(self):
        self.props = Properties()
        self.props["pegasus.metrics.app"] = self.wf_name
        self.props["pegasus.data.configuration"] = "sharedfs"
        self.props["pegasus.transfer.links"] = "True"
        self.props["pegasus.stageout.clusters"] = self.pgss_stgt_clusters
        #self.props["pegasus.transfer.refiner"] = "Bundle" 
        self.props["pegasus.transfer.refiner"] = "BalancedCluster"
        # debug queue means we can not put too many jobs in the queue
        # Help Pegasus developers by sharing performance data (optional)
        self.props["pegasus.monitord.encoding"] = "json"
        self.props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
        if self.debug:
            self.props["dagman.maxjobs"] = self.debug_maxjobs
        else:
            self.props["dagman.maxjobs"] = self.maxjobs
        return

    # --- Site Catalog --------------------------------------------------------
    def create_sites_catalog(self, exec_site_name="slurm"):
        self.sc = SiteCatalog()

        shared_scratch_dir = os.path.join(self.wf_dir, "local-scratch")
        local_storage_dir = self.outputs_dir

        local = Site("local").add_directories(
            Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
                FileServer("file://" + shared_scratch_dir, Operation.ALL)
            ),
            Directory(Directory.LOCAL_STORAGE, local_storage_dir).add_file_servers(
                FileServer("file://" + local_storage_dir, Operation.ALL)
            ),
        )

        shared_scratch_dir = os.path.join(self.wf_dir, "scratch")
        self.shared_scratch_dir = shared_scratch_dir
        # exec_site = (
            # Site(exec_site_name)
            # .add_profiles(Namespace.CONDOR, key="grid_resource", value="batch slurm")
            # .add_profiles(Namespace.PEGASUS, key="style", value="glite")
            # .add_profiles(Namespace.PEGASUS, key="project", value=self.account)
            # .add_profiles(Namespace.PEGASUS, key="auxillary.local", value=True)
            # .add_profiles(Namespace.PEGASUS, key="glite.arguments", value=self.glite_for_cryoem_partition)
            # .add_profiles(Namespace.ENV, key="PEGASUS_HOME", value=os.environ["PEGASUS_HOME"])
            # .add_directories(
                # Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
                    # FileServer("file://" + shared_scratch_dir, Operation.ALL)
                # )
            # )
        # )
        exec_site = (
            Site(exec_site_name)
            .add_profiles(Namespace.CONDOR, key="grid_resource", value="batch slurm")
            .add_profiles(Namespace.PEGASUS, key="style", value="glite")
            .add_profiles(Namespace.PEGASUS, key="project", value=self.account)
            .add_profiles(Namespace.PEGASUS, key="auxillary.local", value=True)
            .add_profiles(Namespace.ENV, key="PEGASUS_HOME", value=os.environ["PEGASUS_HOME"])
            .add_directories(
                Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
                    FileServer("file://" + shared_scratch_dir, Operation.ALL)
                )
            )
        )
        if self.debug:
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value=self.partition)
        else:
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value=self.partition)

        self.sc.add_sites(local, exec_site)

    # --- Transformation Catalog (Executables and Containers) -----------------
    def create_transformation_catalog(self, exec_site_name="slurm"):
        self.tc = TransformationCatalog()
        
        # first - let's try to get the Gain reference file:
        dm2mrc_gainref = Transformation(
            "dm2mrc_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_dm2mrc_wrapper.sh"),
            is_stageable=False
        )
        dm2mrc_gainref.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        tif2mrc_gainref = Transformation(
            "tif2mrc_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_tif2mrc_wrapper.sh"),
            is_stageable=False
        )
        tif2mrc_gainref.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        newstack_gainref = Transformation(
            "newstack_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_newstack_wrapper.sh"),
            is_stageable=False
        )
        newstack_gainref.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        clip_gainref = Transformation(
            "clip_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_clip_wrapper.sh"),
            is_stageable=False
        )
        clip_gainref.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        clip_gainref_superres = Transformation(
            "clip_gainref_superres",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_clip_wrapper.sh"),
            is_stageable=False
        )
        clip_gainref_superres.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        # second - let's try to get the Defect map file:
        dm2mrc_defect_map = Transformation(
            "dm2mrc_defect_map",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_dm2mrc_wrapper.sh"),
            is_stageable=False
        )
        dm2mrc_defect_map.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096"
        )
        if self.debug:
            pass
            #self.cluster_size = 1
        #else:
        #    pass
        # third - let's copy the original jpg file to processed dir:
        #copy_jpeg = Transformation(
        #    "copy_jpeg",
        #    site=exec_site_name,
        #    pfn=os.path.join(self.base_dir, "workflow/scripts/cp_wrapper.sh"),
        #    is_stageable=False
        #)
        #copy_jpeg.add_pegasus_profile( cores="1",
        #                                runtime="60"
        #).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        # fourth - let's do the Motioncor2
        # these are fast jobs - cluster to improve performance
        motionCor2 = Transformation(
            "MotionCor2",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper.sh"),
            is_stageable=False
        )
        motionCor2.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        gctf = Transformation(
            "gctf",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gctf_wrapper.sh"),
            is_stageable=False
        )
        gctf.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d = Transformation(
            "e2proc2d",
            site=exec_site_name, 
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper.sh"),
            is_stageable=False
        )
        e2proc2d.add_pegasus_profile(cores="2",
                                     runtime="300",
                                     memory="4096",
                                     #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick = Transformation(
            "magick",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper.sh"),
            is_stageable=False
        )
        magick.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick2 = Transformation(
            "magick2",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper2.sh"),
            is_stageable=False
        )
        magick.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        gaussian = Transformation(
            "gaussian",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gaussian.sh"),
            is_stageable=False
        )
        gaussian.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)


        grep_wrapper = Transformation(
            "grep_wrapper",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/grep_wrapper.sh"),
            is_stageable=False
        )
        grep_wrapper.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        
        slack_notify = Transformation(
            "slack_notify",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/slack_notify.sh"),
            is_stageable=False
        )
        slack_notify.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        #glite_arguments=self.gctf_glite_arguments
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        
        #dealing with gain reference and similar
        self.tc.add_transformations(dm2mrc_gainref)
        self.tc.add_transformations(tif2mrc_gainref)
        self.tc.add_transformations(newstack_gainref)
        self.tc.add_transformations(clip_gainref)
        self.tc.add_transformations(clip_gainref_superres)
        self.tc.add_transformations(dm2mrc_defect_map)
        #dealing with motioncor and ctf
        #self.tc.add_transformations(copy_jpeg) # cannot be used; might be removed soon
        self.tc.add_transformations(motionCor2)
        self.tc.add_transformations(gctf)
        self.tc.add_transformations(e2proc2d)
        self.tc.add_transformations(magick)
        self.tc.add_transformations(magick2)
        self.tc.add_transformations(gaussian)
        self.tc.add_transformations(grep_wrapper)
        self.tc.add_transformations(slack_notify)

    # --- Replica Catalog ------------------------------------------------------
    def create_replica_catalog(self,exec_site_name="slurm"):
        self.rc = ReplicaCatalog()


    # --- Create Workflow -----------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)
        
        # #Try to find Gain reference file - it might not be a part of the dataset, 
        # #so we must take it into account.
        # #define Gain reference Super resolution input and output filename
        # logger.info("self.inputs_dir {}".format(self.inputs_dir))
        # raw_gain_ref_path=None
        # Raw_Gain_Ref_SR_path=[]
        # logger.info("looking for gain reference")
        # possible_gf_files_regexes=['*_gain.tiff','*.gain']
        # #add user provided optional regex:
        # if self.rawgainref!=None:
            # possible_gf_files_regexes.append(self.rawgainref)
        # for i in self.inputs_dir:
            # for possible_gf in possible_gf_files_regexes:
                # logger.info("searching gain ref here: {} with {} regex".format(i, possible_gf))
                # raw_gain_ref_path = self.find_files2(os.path.join(i,"**"), possible_gf)
                # if len(raw_gain_ref_path)>=1:
                    # Raw_Gain_Ref_SR_path=raw_gain_ref_path
                    # break
            # else:
                # continue
            # break


        if len(self._gain_ref_fn) != 0 and self._gainref_done == False:
            logger.info("processing self._gain_ref_fn[0]: {}".format(self._gain_ref_fn[0]))
            Raw_Gain_Ref_SR_path = self._gain_ref_fn[0]
            # get the extension
            gainref_extension=Raw_Gain_Ref_SR_path.split('.')[-1]
            
            
            Raw_Gain_Ref_SR_name = os.path.basename(Raw_Gain_Ref_SR_path)
            logger.info("Found gain reference file {} ...".format(Raw_Gain_Ref_SR_name))
            Raw_Gain_Ref_SR = File(Raw_Gain_Ref_SR_name)
            Gain_Ref_SR_path = "%s_sr.%s"%(".".join(Raw_Gain_Ref_SR_path.split(".")[:-1]), "mrc")
            Gain_Ref_SR_name = os.path.basename(Gain_Ref_SR_path)
            Gain_Ref_SR = File(Gain_Ref_SR_name)
            self.rc.add_replica("slurm", Raw_Gain_Ref_SR_name, "file://{}".format(Raw_Gain_Ref_SR_path))
    
            #define Gain reference output filename
            #TODO: improve lines below
            Gain_Ref_path = Gain_Ref_SR_path.replace('_sr.mrc','_std.mrc')
            Gain_Ref_name = os.path.basename(Gain_Ref_path)
            Gain_Ref = File(Gain_Ref_name)
    
            #define flip Y Super resolution output filename
            #TODO: improve lines below
            FlipY_SR_path = Gain_Ref_SR_path.replace('_sr.mrc','_sr.flipy.mrc')
            #logger.info(" ... found {} ".format(FlipY_SR_path))
            FlipY_SR_name = os.path.basename(FlipY_SR_path)
            FlipY_SR = File(FlipY_SR_name)
    
            #define flip Y std resolution output filename
            #TODO: improve lines below
            FlipY_path = Gain_Ref_path.replace('_std.mrc','_std.flipy.mrc')
            FlipY_name = os.path.basename(FlipY_path)
            FlipY = File(FlipY_name)
            #convert Superres dm4 or tiff file to mrc
            #dm2mrc usage: dm2mrc infile outfile
            #tif2mrc usage: tif2mrc infile outfile
            if gainref_extension=="tiff":
                logger.info("gain reference file extension {} ...".format(gainref_extension))
                tif2mrc_gainref_sr_job = Job("tif2mrc_gainref")
                tif2mrc_gainref_sr_job.add_args(Raw_Gain_Ref_SR, Gain_Ref_SR)
                tif2mrc_gainref_sr_job.add_inputs(Raw_Gain_Ref_SR)
                tif2mrc_gainref_sr_job.add_outputs(Gain_Ref_SR, stage_out=True)
            elif gainref_extension=="dm":
                logger.info("gain reference file extension {} ...".format(gainref_extension))
                dm2mrc_gainref_sr_job = Job("dm2mrc_gainref")
                dm2mrc_gainref_sr_job.add_args(Raw_Gain_Ref_SR, Gain_Ref_SR)
                dm2mrc_gainref_sr_job.add_inputs(Raw_Gain_Ref_SR)
                dm2mrc_gainref_sr_job.add_outputs(Gain_Ref_SR, stage_out=True)
            else:
                logger.info("Unknown gain reference file extension {} ...".format(gainref_extension))
                raise
            #create standard resolution gain ref file from superres gain ref file
            #newstack usage here (decrease the size of Super resolution image by factor of 2): newstack -bin 2 infile outfile
            newstack_gainref_job = Job("newstack_gainref")
            newstack_gainref_job.add_args("-bin", "2", Gain_Ref_SR, Gain_Ref)
            newstack_gainref_job.add_inputs(Gain_Ref_SR)
            newstack_gainref_job.add_outputs(Gain_Ref, stage_out=True)
            #flip both gain reference files on y axis
            #clip usage here (flip img on Y axis): clip flipy infile outfile
            #std resolution
            clip_gainref_job = Job("clip_gainref")
            clip_gainref_job.add_args("flipy", Gain_Ref, FlipY)
            clip_gainref_job.add_inputs(Gain_Ref)
            clip_gainref_job.add_outputs(FlipY, stage_out=True)
            #super resolution
            clip_gainref_superres_job = Job("clip_gainref_superres")
            clip_gainref_superres_job.add_args("flipy", Gain_Ref_SR, FlipY_SR)
            clip_gainref_superres_job.add_inputs(Gain_Ref_SR)
            clip_gainref_superres_job.add_outputs(FlipY_SR, stage_out=True)
            if gainref_extension == "tiff":
                self.wf.add_jobs(tif2mrc_gainref_sr_job)
            elif gainref_extension == "dm":
                self.wf.add_jobs(dm2mrc_gainref_sr_job)
            else:
                raise
            self.wf.add_jobs(newstack_gainref_job)
            self.wf.add_jobs(clip_gainref_job)
            self.wf.add_jobs(clip_gainref_superres_job)
            #self.gainref_done = True
        elif self._gainref_done == True:
            #set variables and that is it
            Gain_Ref_SR_name=os.path.basename(self.gr_sr)
            Gain_Ref_SR = File(Gain_Ref_SR_name)
            self.rc.add_replica("slurm", Gain_Ref_SR_name, self.gr_sr)
            
            FlipY_SR_name = os.path.basename(self.gr_sr_flipy)
            FlipY_SR = File(FlipY_SR_name)
            self.rc.add_replica("slurm", FlipY_SR_name, self.gr_sr_flipy)
            
            Gain_Ref_name=os.path.basename(self.gr_std)
            Gain_Ref = File(Gain_Ref_name)
            self.rc.add_replica("slurm", Gain_Ref_name, self.gr_std)
            
            FlipY_name=os.path.basename(self.gr_std_flipy)
            FlipY = File(FlipY_name)
            self.rc.add_replica("slurm", FlipY_name, self.gr_std_flipy)
        else:
            logger.info("FAILED: gain ref not found")
            sys.exit()
            pass
        
        # #Try to find Defect Map file - it might not be a part of the dataset; file is not needed for now
        # logger.info("looking for Defect Map")
        # possible_dm_files_regexes=['*Map.m1.dm4']
        # raw_defect_map_path=None
        # Raw_Defect_Map_path=[]
        # if self.rawdefectsmap!=None:
            # possible_dm_files_regexes.append(self.rawdefectsmap)
        # for i in self.inputs_dir:
            # for possible_dm in possible_dm_files_regexes:
                # raw_defect_map_path = self.find_files2(os.path.join(i,"**"), possible_dm)
                # if len(raw_defect_map_path)>=1:
                    # logger.info("searching defect map here: {} with {} regex".format(i, possible_dm))
                    # Raw_Defect_Map_path=raw_defect_map_path
                    # break
            # else:
                # continue
            # break

            
        if len(self._defect_map_fn) != 0 and self._defect_map_done == False:
            Raw_Defect_Map_path = self._defect_map_fn[0]
            Raw_Defect_Map_name = os.path.basename(Raw_Defect_Map_path)
            logger.info("Found Defect Map file {} ...".format(Raw_Defect_Map_name))
            Raw_Defect_Map = File(Raw_Defect_Map_name)
            Defect_Map_path = "%s_sr.%s"%(".".join(Raw_Defect_Map_path.split(".")[:-1]), "mrc")
            Defect_Map_name = os.path.basename(Defect_Map_path)
            Defect_Map = File(Defect_Map_name)
            self.rc.add_replica("slurm", Raw_Defect_Map_name, "file://{}".format(Raw_Defect_Map_path))
            #create defect map file
            #dm2mrc usage: dm2mrc infile outfile
            dm2mrc_defect_map_job = Job("dm2mrc_defect_map")
            dm2mrc_defect_map_job.add_args(Raw_Defect_Map, Defect_Map)
            dm2mrc_defect_map_job.add_inputs(Raw_Defect_Map)
            dm2mrc_defect_map_job.add_outputs(Defect_Map, stage_out=True)
            self.wf.add_jobs(dm2mrc_defect_map_job)
            #self.defmap_done = True
        elif self._defect_map_done == True:
            #set variables and that is it
            Defect_Map_name=os.path.basename(self.dmf)
            Defect_Map = File(Defect_Map_name)
            self.rc.add_replica("slurm", Defect_Map, self.dmf)
        else:
            logger.info("Raw_Defect_Map_path not found")
            pass
        
        # # try to find where exactly raw files are. Done this way to speed-up the process
        # possible_raw_files_regexes=['FoilHole*fractions.tiff','FoilHole*fractions.mrc','FoilHole*EER.eer']
        # if self.basename_prefix!=None and self.basename_suffix!=None and self.basename_extension!=None:
            # possible_raw_files_regexes.append("%s*%s.%s"%(self.basename_prefix,self.basename_suffix,self.basename_extension))
        
        # for i in self.inputs_dir:
            # for possible_raw_files in possible_raw_files_regexes:
                # raw_location=(os.path.join(i, "**"), possible_raw_files)
                # self.correct_input_dir=i
                # flist = self.find_files2(raw_location[0], raw_location[1])
                # if len(flist)>=1:
                    # file_list=flist
                    # self.raw_location = raw_location
                    # break
            # else:
                # continue
            # break
                
        # #sort? sort - to make it somewhat FIFO
        # file_list.sort()
        # #define filename extension
        # self.basename_extension=file_list[0].split('.')[-1]
        # self.basename_suffix=file_list[0].split('.')[-2].split('_')[-1]
        
        # #set the number of raw files
        # self.no_of_raw=len(file_list)
        
        # if self.no_of_files_to_proc_in_cycle != -1 and not self.debug:
            # #do all
            # pass
        
        # if self.no_of_files_to_proc_in_cycle != -1 and self.debug:
            # # when debugging, only do a fraction of the files
            # file_list = random.sample(file_list, self.no_of_files_to_proc_in_cycle)
        # else:
            # # even for production, only process a part of the dataset (maybe change this later?)
            # #
            # #file_list = random.sample(file_list, self.no_of_files_to_proc_in_cycle)
            # pass
        
        #set file list to be equal to no_of_files_to_proc_in_cycle based on self.processed_files_list
        # if self.no_of_files_to_proc_in_cycle != -1:
            # file_list = [x for x in file_list if x not in self.processed_files_list][:self.no_of_files_to_proc_in_cycle]
            # #pass
            # # for x in self.processed_files_list: 
                # # file_list.append(x)
        # elif self.no_of_files_to_proc_in_cycle ==-1:
            # #ignore no_of_files_to_proc_in_cycle and do all at once
            # pass
        # else:
            # loger.info("Cannot get file list")
            # pass
        
        logger.info("Currently processing {} files. Processed list length is {}".format(len(self._file_list_to_process), len(self._processed_files_list)))
        #logger.info("Currently processing {} files. Processed list length is {}".format("\n".join(file_list), len(self.processed_files_list)))
        #define filename extension
        self.basename_extension=self._file_list_to_process[0].split('.')[-1]
        self.basename_suffix=self._file_list_to_process[0].split('.')[-2].split('_')[-1]
        #for fraction_file_path in file_list:
        for fraction_file_path in self._file_list_to_process:
            #logger.info("fraction_file_path {}".format(fraction_file_path))
            fraction_file_name = os.path.basename(fraction_file_path)
            fraction_file = File(fraction_file_name)
            self.rc.add_replica("slurm", fraction_file_name, "file://{}".format(fraction_file_path))
            ##find and copy the jpeg file 
            ## 2021-07-23; TO; skipping temprarily due to the uncertain location of the file
            #jpeg_file_path_dirname=os.path.dirname(fraction_file_path)
            #jpeg_file_name=("%s.jpg"%"_".join(fraction_file_name.split("_")[:-1]))
            #jpeg_file_path=os.sep.join([jpeg_file_path_dirname,jpeg_file_name])
            ## use a "fake" input lfn and a real output lfn
            #jpeg_file = File(jpeg_file_name + "-IN")
            #jpeg_file_out = File(jpeg_file_name.replace(".jpg","_raw.jpg"))
            #self.rc.add_replica("slurm", jpeg_file_name + "-IN", "file://{}".format(jpeg_file_path))
            #copy_jpeg_job = Job("copy_jpeg").add_args("-v", "-L", "./{}-IN".format(jpeg_file_name), jpeg_file_out)
            #copy_jpeg_job.add_inputs(jpeg_file)
            #copy_jpeg_job.add_outputs(jpeg_file_out, stage_out=True, register_replica=False)
            #self.wf.add_jobs(copy_jpeg_job)

            # generated files will be named based on the input
            basename = re.sub("_%s.%s$"%(self.basename_suffix,self.basename_extension), "", fraction_file_name)
            mrc_file_name="{}.mrc".format(basename)
            dw_file_name="{}_DW.mrc".format(basename)
            mc2_stdout_file_name="{}_DW.stdout.txt".format(basename)
            mc2_stderr_file_name="{}_DW.stderr.txt".format(basename)
            mrc_file = File(mrc_file_name)
            dw_file = File(dw_file_name)
            mc2_stdout = File(mc2_stdout_file_name)
            mc2_stderr = File(mc2_stderr_file_name)

            # MotionCor2
            #adjust for one of three different extensions: mrc, tiff or eer
            if self.basename_extension=="tiff":
                mc2_in="-InTiff"
            elif self.basename_extension=="mrc":
                mc2_in="-InMrc"
            elif self.basename_extension=="eer":
                mc2_in="-InEer"
            else:
                logger.info("Unknown image extension - %s"%self.basename_extension)
                sys.exit(1)
            
            if len(Gain_Ref_SR_name) != 0:
                #case where we have gain reference file
                if self.throw!=None and self.trunc!=None:
                    # case for k3
                    if str(self.kev) == "300":
                        motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                            mrc_file, "-Gain", FlipY,"-Iter 7 -Tol 0.5",
                            "-PixSize", self.apix, "-FmDose", self.fmdose, "-Throw", self.throw, "-Trunc", self.trunc, "-Gpu 0 -Serial 0",
                            "-OutStack 0", "-SumRange 0 0")
                        motionCor_job.add_inputs(fraction_file, FlipY)
                    # case for f4
                    elif str(self.kev) == "200":
                        motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                            mrc_file, "-Gain", Gain_Ref,"-Iter 7 -Tol 0.5",
                            "-PixSize", self.apix, "-FmDose", self.fmdose, "-Throw", self.throw, "-Trunc", self.trunc, "-Gpu 0 -Serial 0",
                            "-OutStack 0", "-SumRange 0 0")
                        motionCor_job.add_inputs(fraction_file, Gain_Ref)
                else:
                    # case for k3
                    if str(self.kev) == "300":
                        motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                            mrc_file, "-Gain", FlipY,"-Iter 7 -Tol 0.5", "-PixSize", self.apix, "-FmDose", 
                            self.fmdose, "-Gpu 0 -Serial 0", "-OutStack 0", "-SumRange 0 0")
                        motionCor_job.add_inputs(fraction_file, FlipY)
                    # case for f4
                    elif str(self.kev) == "200":
                        motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                            mrc_file, "-Gain", Gain_Ref,"-Iter 7 -Tol 0.5", "-PixSize", self.apix, "-FmDose", 
                            self.fmdose, "-Gpu 0 -Serial 0", "-OutStack 0", "-SumRange 0 0")
                        motionCor_job.add_inputs(fraction_file, Gain_Ref)

            else:
                #case where we do not have gain referencee file
                if self.throw!=None and self.trunc!=None:
                    motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                        mrc_file, "-Iter 7 -Tol 0.5",
                        "-PixSize", self.apix, "-FmDose", self.fmdose, "-Throw", self.throw, "-Trunc", self.trunc, "-Gpu 0 -Serial 0",
                        "-OutStack 0", "-SumRange 0 0")
                else:
                    motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                        mrc_file, "-Iter 7 -Tol 0.5", "-PixSize", self.apix, "-FmDose", "-Gpu 0 -Serial 0",
                        "-OutStack 0", "-SumRange 0 0")
                motionCor_job.add_inputs(fraction_file)

            motionCor_job.add_outputs(mrc_file, stage_out=False, register_replica=False)
            motionCor_job.add_outputs(dw_file, stage_out=True, register_replica=False)
            motionCor_job.set_stdout(mc2_stdout, stage_out=True, register_replica=False)
            motionCor_job.set_stderr(mc2_stderr, stage_out=True, register_replica=False)
            motionCor_job.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            #motionCor_job.add_profiles(Namespace.PEGASUS, "label", "mc2")
            self.wf.add_jobs(motionCor_job)

            # gctf
            ctf_star_file = File(mrc_file_name.replace(".mrc",".star"))
            #ctf_pf_file = File(mrc_file_name.replace(".mrc","_pf.mrc"))
            ctf_file = File(mrc_file_name.replace(".mrc",".ctf"))
            gctf_log_file = File(mrc_file_name.replace(".mrc","_gctf.log"))
                        
            gctf_stdout_file_name=mrc_file_name.replace(".mrc","_gctf_stdout.txt")
            gctf_stderr_file_name=mrc_file_name.replace(".mrc","_gctf_stderr.txt")
            gctf_stdout = File(gctf_stdout_file_name)
            gctf_stderr = File(gctf_stderr_file_name)
            
            
            gctf_job = (
                Job("gctf").add_args("--apix", self.apix, "--kV", self.kev, "--Cs", "2.7", "--ac", "0.1",
                                     "--ctfstar", ctf_star_file, "--gid", "0", "--boxsize", "1024", mrc_file)
            )

            gctf_job.add_inputs(mrc_file)
            gctf_job.add_outputs(ctf_star_file, stage_out=True, register_replica=False)
            #gctf_job.add_outputs(ctf_pf_file, stage_out=True, register_replica=True)
            gctf_job.add_outputs(ctf_file, stage_out=True, register_replica=False)
            gctf_job.add_outputs(gctf_log_file, stage_out=True, register_replica=False)
            gctf_job.set_stdout(gctf_stdout, stage_out=True, register_replica=False)
            gctf_job.set_stderr(gctf_stderr, stage_out=True, register_replica=False)
            gctf_job.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            #gctf_job.add_profiles(Namespace.PEGASUS, "label", "gctf")
            self.wf.add_jobs(gctf_job)

            # e2proc2d - motion-corrected to jpg, then resize to 20% size
            dw_jpg_name = dw_file_name.replace("_DW.mrc","_DW_fs.jpg")
            dw_jpg_file = File(dw_jpg_name)
            e2proc2d_job1 = Job("e2proc2d")            
            e2proc2d_job1.add_inputs(dw_file)
            e2proc2d_job1.add_outputs(dw_jpg_file, stage_out=True, register_replica=False)
            #e2proc2d_job1.add_args("--average", dw_file, dw_jpg_file)
            e2proc2d_job1.add_args("--process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane", dw_file, dw_jpg_file)
            e2proc2d_job1.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            self.wf.add_jobs(e2proc2d_job1)
            
            #imagemagick - resize the input jpg from about 5k to 1k px
            magick_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg",".jpg"))
            magick_resize = Job("magick")
            magick_resize.add_inputs(dw_jpg_file)
            magick_resize.add_outputs(magick_jpg_file, stage_out=True, register_replica=False)
            magick_resize.add_args("convert", "-resize", '20%', dw_jpg_file, magick_jpg_file)
            magick_resize.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            self.wf.add_jobs(magick_resize)
            
            
            # e2proc2d - ctf to jpg
            jpg_ctf_file = File(mrc_file_name.replace(".mrc","_ctf.jpg"))
            e2proc2d_job2 = Job("e2proc2d")            
            e2proc2d_job2.add_inputs(ctf_file)
            e2proc2d_job2.add_outputs(jpg_ctf_file, stage_out=True, register_replica=False)
            e2proc2d_job2.add_args(ctf_file, jpg_ctf_file)
            e2proc2d_job2.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            self.wf.add_jobs(e2proc2d_job2)

            # # make an image file that makes particles more visible using filters
            # gaussian_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg",".filtered.jpg"))
            # gaussian_filter = Job("gaussian")
            # gaussian_filter.add_inputs(magick_jpg_file)
            # gaussian_filter.add_outputs(gaussian_jpg_file, stage_out=True, register_replica=False)
            # gaussian_filter.add_args(magick_jpg_file, gaussian_jpg_file)
            # gaussian_filter.add_profiles(Namespace.PEGASUS, "label", "{}".format(fraction_file_name))
            # self.wf.add_jobs(gaussian_filter)
            


            #imagemagick - stitch together resized jpg and add text
            magick_combined_jpg_fn = dw_jpg_name.replace("_DW_fs.jpg","_combined.jpg")
            magick_combined_jpg_file = File(magick_combined_jpg_fn)
            #magick_combined_jpg_out_fn = dw_jpg_name.replace("_DW_fs.jpg","_combined.txt")
            #magick_combined_jpg_out=File(magick_combined_jpg_out_fn)
            magick_convert = Job("magick2")
            magick_convert.add_inputs(magick_jpg_file)
            magick_convert.add_inputs(jpg_ctf_file)
            magick_convert.add_inputs(gctf_log_file)
            magick_convert.add_inputs(mc2_stdout)
            magick_convert.add_outputs(magick_combined_jpg_file, stage_out=True, register_replica=False)
            #magick_convert.add_outputs(magick_combined_jpg_out, stage_out=True, register_replica=False)
            #magick_convert.add_args("convert", "+append", dw_jpg_file, jpg_ctf_file, "-resize", "x1024", magick_combined_jpg_file)
            #magick_convert.add_args(dw_jpg_file, jpg_ctf_file, magick_combined_jpg_file, os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), gctf_log_file.lfn), os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), mc2_stdout.lfn), magick_combined_jpg_out)
            magick_convert.add_args(magick_jpg_file, jpg_ctf_file, magick_combined_jpg_file, gctf_log_file.lfn, mc2_stdout.lfn)
            magick_convert.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            self.wf.add_jobs(magick_convert)
            
            # # #prepare text output - shifts from motioncor2
            # # magick_combined_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg","_combined.jpg"))
            # # grep_wrapper_shifts = Job("grep_wrapper")
            # # grep_wrapper_shifts.add_inputs(mc2_stdout)
            # # grep_wrapper_shifts.add_outputs(magick_combined_jpg_file, stage_out=True, register_replica=False)
            # # grep_wrapper_shifts.add_args("convert", "+append", dw_jpg_file, jpg_ctf_file, "-resize", "x512", magick_combined_jpg_file)
            # # grep_wrapper_shifts.add_profiles(Namespace.PEGASUS, "label", "{}".format(fraction_file_name))
            # # self.wf.add_jobs(grep_wrapper_shifts)
            
            # # #prepare text output - estimated resolution from ctf
            # # magick_combined_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg","_combined.jpg"))
            # # grep_wrapper_ctf_reso = Job("grep_wrapper")
            # # grep_wrapper_ctf_reso.add_inputs(mc2_stdout)
            # # grep_wrapper_ctf_reso.add_inputs(jpg_ctf_file)
            # # grep_wrapper_ctf_reso.add_outputs(magick_combined_jpg_file, stage_out=True, register_replica=False)
            # # grep_wrapper_ctf_reso.add_args("convert", "+append", dw_jpg_file, jpg_ctf_file, "-resize", "x512", magick_combined_jpg_file)
            # # grep_wrapper_ctf_reso.add_profiles(Namespace.PEGASUS, "label", "{}".format(fraction_file_name))
            # # self.wf.add_jobs(grep_wrapper_ctf_reso)
            
            #send notification to the slack channel
            slack_notify_out=File(mrc_file_name.replace(".mrc","_slack_msg.txt"))
            slack_notify_job = Job("slack_notify")
            #slack_notify_job.add_inputs(mc2_stdout)
            #slack_notify_job.add_inputs(gctf_log_file)
            slack_notify_job.add_inputs(magick_combined_jpg_file)
            slack_notify_job.add_outputs(slack_notify_out, stage_out=True, register_replica=False)
            #slack_notify_job.add_args(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), magick_combined_jpg_fn), gctf_log_file.lfn, mc2_stdout.lfn, slack_notify_out)
            slack_notify_job.add_args(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), magick_combined_jpg_fn), slack_notify_out)
            slack_notify_job.add_profiles(Namespace.PEGASUS, "label", "img-{}".format(fraction_file_name))
            self.wf.add_jobs(slack_notify_job)
            
            self.no_of_processed+=1
            


    def set_params(self, datum):
        self.apix = datum.apix
        self.fmdose = datum.fmdose
        self.kev = datum.kev
        self._gainref_done = datum._gainref_done
        try: self._gain_ref_fn = datum._gain_ref_fn
        except: pass
        self._defect_map_done = datum._defect_map_done
        self._defect_map_fn = datum._defect_map_fn
        self._processed_files_list = datum._processed_files_list
        self._file_list_to_process = datum._file_list_to_process
        #self.particle_size = particle_size
        try:
            self.gr_sr_flipy = datum.gr_sr_flipy
            self.gr_sr = datum.gr_sr
            self.gr_std_flipy = datum.gr_std_flipy
            self.gr_std = datum.gr_std
        except: pass        
        try: self.dmf = datum.dmf
        except: pass
        try: self.rawgainref = datum.rawgainref
        except: pass
        try: self.rawdefectsmap = datum.rawdefectsmap
        except: pass
        try: self.basename_prefix = datum.basename_prefix
        except: pass
        try: self.basename_suffix = datum.basename_suffix
        except: pass
        try: self.basename_extension = datum.basename_extension
        except: pass
        try: self.throw=datum.throw
        except: pass
        try: self.trunc=datum.trunc
        except: pass
        self.superresolution = datum.superresolution

    # --- Submit Workflow -----------------------------------------------------
    # def submit_workflow(self, apix, fmdose, kev, rawgainref, rawdefectsmap, 
                        # basename_prefix, basename_suffix, basename_extension, 
                        # throw, trunc, superresolution):
    def submit_workflow(self):
        # self.apix = apix
        # self.fmdose = fmdose
        # self.kev = kev
        # self.particle_size = particle_size
        # self.rawgainref = rawgainref
        # self.rawdefectsmap = rawdefectsmap
        # self.basename_prefix = basename_prefix
        # self.throw=throw
        # self.trunc=trunc
        # self.superresolution = superresolution
        
        logger.info("Starting a new workflow in {} ...".format(self.wf_dir))
       
        try: 
            os.mkdir(self.wf_dir)
        except:
            pass
        os.chdir(self.wf_dir)
    
        logger.info("Creating workflow properties...")
        self.create_pegasus_properties()
    
        logger.info("Creating execution sites...")
        self.create_sites_catalog()
        
        logger.info("Creating transformation catalog...")
        self.create_transformation_catalog()
    
        logger.info("Creating replica catalog...")
        self.create_replica_catalog()
    
        logger.info("Creating pipeline workflow dag...")
        self.create_workflow()
   
        self.write()
        
        logger.info("os.getcwd() {}".format(os.getcwd()))
        logger.info("self.wf_name {}".format(self.wf_name))
        

        self.wf.plan(submit=True,
                     sites=["slurm"],
                     output_sites=["local"],
                     dir=os.getcwd(),
                     relative_dir=self.wf_name,
                     cluster=["label"]
                    )


    def find_files(self, root_dir, regex):
        '''
        Traverse the directory and find according to the regex
        '''
        count = 0
        found_files = []
        pattern = re.compile(regex)
        for root, dirs, files in os.walk(root_dir):
            for name in files:
                if pattern.search(name):
                    found_files.append(os.path.join(root, name))
                    count += 1
        logger.info(" ... found {} files matching {}".format(count, regex))
        return found_files
        
    def find_files2(self, root_dir, regex):
        '''
        Returns sorted list of files matching regex = root_dir+/+regex (similar to ls)
        Much faster than find_files
        eg. f=find_files2("/project/cryoem/K3_sample_dataset/20210205_mutant/Images-Disc1", "*/Data/*_fractions.tiff") to get all files
        '''
        search_path=os.path.join(root_dir,regex)
        found_files=glob.glob(search_path, recursive=True)
        logger.info(" ... searching for {}".format(search_path))
        logger.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files


    def find_files3(self, regex):
        '''
        Returns sorted list of files matching regex = root_dir+/+regex (similar to ls)
        Much faster than find_files
        eg. f=find_files2("/project/cryoem/K3_sample_dataset/20210205_mutant/Images-Disc1", "*/Data/*_fractions.tiff") to get all files
        '''

        found_files=glob.glob(regex, recursive=True)
        logger.info(" ... searching for {}".format(search_path))
        logger.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files
        
