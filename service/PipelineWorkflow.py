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
    def __init__(self, base_dir, wf_dir, inputs_dir, outputs_dir, debug=False, cluster_size=10, no_of_files_to_proc_in_cycle=5):
        self.wf_name = "motioncor2"
        self.base_dir = base_dir
        self.wf_dir = wf_dir
        self.inputs_dir = inputs_dir
        self.outputs_dir = outputs_dir
        self.debug = debug
        self.cluster_size = cluster_size
        self.no_of_files_to_proc_in_cycle = no_of_files_to_proc_in_cycle
        self.no_of_processed = 0

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
        # debug queue means we can not put too many jobs in the queue
        if self.debug:
            self.props["dagman.maxjobs"] = "5"
        else:
            self.props["dagman.maxjobs"] = "50"
        return
        # Help Pegasus developers by sharing performance data (optional)
        self.props["pegasus.monitord.encoding"] = "json"
        self.props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"

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
        exec_site = (
            Site(exec_site_name)
            .add_profiles(Namespace.CONDOR, key="grid_resource", value="batch slurm")
            .add_profiles(Namespace.PEGASUS, key="style", value="glite")
            .add_profiles(Namespace.PEGASUS, key="project", value="osinski_703")
            .add_profiles(Namespace.PEGASUS, key="auxillary.local", value=True)
            .add_profiles(Namespace.ENV, key="PEGASUS_HOME", value=os.environ["PEGASUS_HOME"])
            .add_directories(
                Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
                    FileServer("file://" + shared_scratch_dir, Operation.ALL)
                )
            )
        )
        if self.debug:
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value="gpu")
        else:
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value="gpu")

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
            self.cluster_size = 1
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
                                        #use p100 as soon as permanently available
                                        #glite_arguments="--gres=gpu:p100:2"
                                        glite_arguments="--gres=gpu:k40:2"
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
                                        #glite_arguments="--gres=gpu:p100:2"
                                        glite_arguments="--gres=gpu:k40:1"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d = Transformation(
            "e2proc2d",
            site=exec_site_name, 
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper.sh"),
            is_stageable=False
        )
        e2proc2d.add_pegasus_profile(cores="1",
                                     runtime="600",
                                     memory="4096"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick = Transformation(
            "magick",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper.sh"),
            is_stageable=False
        )
        magick.add_pegasus_profile( cores="1",
                                        runtime="300",
                                        memory="2048"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        
        self.tc.add_transformations(dm2mrc_gainref)
        self.tc.add_transformations(tif2mrc_gainref)
        self.tc.add_transformations(newstack_gainref)
        self.tc.add_transformations(clip_gainref)
        self.tc.add_transformations(clip_gainref_superres)
        self.tc.add_transformations(dm2mrc_defect_map)
        #self.tc.add_transformations(copy_jpeg)
        self.tc.add_transformations(motionCor2)
        self.tc.add_transformations(gctf)
        self.tc.add_transformations(e2proc2d)
        self.tc.add_transformations(magick)

    # --- Replica Catalog ------------------------------------------------------
    def create_replica_catalog(self,exec_site_name="slurm"):
        self.rc = ReplicaCatalog()

        

    # --- Create Workflow -----------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)
        
        #tho lines below can probably be removed - TO will check for it
        #raw_prefix="raw_"
        #mc_prefix = "mc_"
        
        
        #Try to find Gain reference file - it might not be a part of the dataset, 
        #so we must take it into account.
        #define Gain reference Super resolution input and output filename
        logger.info("self.inputs_dir {}".format(self.inputs_dir))
        raw_gain_ref_path=None
        Raw_Gain_Ref_SR_path=[]
        logger.info("looking for gain reference")
        for i in self.inputs_dir:
            logger.info("searching gain ref here: {} with {}".format(i, self.rawgainref))
            raw_gain_ref_path = self.find_files2(os.path.join(i,"**"), self.rawgainref)
            if len(raw_gain_ref_path)>=1:
                Raw_Gain_Ref_SR_path=raw_gain_ref_path
                break
        #Raw_Gain_Ref_SR_path = self.find_files2(self.inputs_dir, self.rawgainref)
        if len(Raw_Gain_Ref_SR_path) != 0:
            #try:
                Raw_Gain_Ref_SR_path = Raw_Gain_Ref_SR_path[0]
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
            #except:
            #    logger.info("Raw_Gain_Ref_SR_path {} ...".format(Raw_Gain_Ref_SR_path))
        else:
            logger.info("Raw_Gain_Ref_SR_path {} from else...".format(Raw_Gain_Ref_SR_path))
            pass
        #Try to find Defect Map file - it might not be a part of the dataset, 
        #so we must take it into account.        
        #define Defect Map input and output filename
        raw_defect_map_path=None
        Raw_Defect_Map_path=[]
        for i in self.inputs_dir:
            raw_defect_map_path = self.find_files2(os.path.join(i,"**"), self.rawdefectsmap)
            if len(raw_defect_map_path)>=1:
                Raw_Defect_Map_path=raw_defect_map_path
                break
        #Raw_Defect_Map_path = self.find_files2(self.inputs_dir, self.rawdefectsmap)
        if len(Raw_Defect_Map_path) != 0:
            try: 
                Raw_Defect_Map_path = Raw_Defect_Map_path[0]
                Raw_Defect_Map_name = os.path.basename(Raw_Defect_Map_path)
                logger.info("Found Defect Map file {} ...".format(Raw_Defect_Map_name))
                Raw_Defect_Map = File(Raw_Defect_Map_name)
                Defect_Map_path = "%s_sr.%s"%(".".join(Raw_Defect_Map_path.split(".")[:-1]), "mrc")
                Defect_Map_name = os.path.basename(Defect_Map_path)
                Defect_Map = File(Defect_Map_name)
                self.rc.add_replica("slurm", Raw_Defect_Map_name, "file://{}".format(Raw_Defect_Map_path))
                #we do this, but if it impacts the processing speed to much it can be disabled for now
                #create defect map file
                #dm2mrc usage: dm2mrc infile outfile
                dm2mrc_defect_map_job = Job("dm2mrc_defect_map")
                dm2mrc_defect_map_job.add_args(Raw_Defect_Map, Defect_Map)
                dm2mrc_defect_map_job.add_inputs(Raw_Defect_Map)
                dm2mrc_defect_map_job.add_outputs(Defect_Map, stage_out=True)
                self.wf.add_jobs(dm2mrc_defect_map_job)
            except: 
                logger.info("Raw_Defect_Map_path {} ...".format(Raw_Defect_Map_path))
        else:
            logger.info("Raw_Defect_Map_path {} from else...".format(Raw_Defect_Map_path))
            pass
        
        # for each _fractions.(tiff|mrc) in the Images-Disc1 dir 
        #file_list = self.find_files(
        #                    os.path.join(self.inputs_dir, "Images-Disc1"),
        #                    "_fractions.tiff$")
        for i in self.inputs_dir:
            flist = self.find_files2(os.path.join(i, "**"),
                            "%s*%s.%s"%(self.basename_prefix,self.basename_suffix,self.basename_extension))
            if len(flist)>=1:
                file_list=flist
                break
                
        #file_list = self.find_files2(
        #                    os.path.join(self.inputs_dir, "Images-Disc1","*","Data"),
        #                    "%s*%s.%s"%(self.basename_prefix,self.basename_suffix,self.basename_extension))
        #sort?
        file_list.sort()
        #define filename extension
        self.basename_extension=file_list[0].split('.')[-1]
        
        if self.no_of_files_to_proc_in_cycle != -1:
            file_list = random.sample(file_list, self.no_of_files_to_proc_in_cycle)
        
        if self.debug:
            # when debugging, only do a fraction of the files
            file_list = random.sample(file_list, self.no_of_files_to_proc_in_cycle)
        
        else:
            # even for production, only process a part of the dataset (maybe change this later?)
            #
            file_list = random.sample(file_list, self.no_of_files_to_proc_in_cycle)
            pass

        for fraction_file_path in file_list:

            fraction_file_name = os.path.basename(fraction_file_path)
            fraction_file = File(fraction_file_name)
            self.rc.add_replica("slurm", fraction_file_name, "file://{}".format(fraction_file_path))

            # generated files will be named based on the input
            basename = re.sub("_%s.%s$"%(self.basename_suffix,self.basename_extension), "", fraction_file_name)

            mrc_file_name="{}.mrc".format(basename)
            dw_file_name="{}_DW.mrc".format(basename)
            mrc_file = File(mrc_file_name)
            dw_file = File(dw_file_name)

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
            
            if len(Raw_Gain_Ref_SR_path) != 0:
                #case where we have gain referencee file
                motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                    mrc_file, "-Gain", FlipY,"-Iter 7 -Tol 0.5 -RotGain 2",
                    "-PixSize", self.apix, "-FmDose", self.fmdose, "-Throw", self.throw, "-Trunc", self.trunc, "-Gpu 0 1 -Serial 0",
                    "-OutStack 0", "-SumRange 0 0")
                motionCor_job.add_inputs(fraction_file, FlipY)
            else:
                #case where we do not have gain referencee file
                motionCor_job = Job("MotionCor2").add_args(mc2_in, "./{}".format(fraction_file_name), "-OutMrc",
                    mrc_file, "-Iter 7 -Tol 0.5 -RotGain 2",
                    "-PixSize", self.apix, "-FmDose", self.fmdose, "-Throw", self.throw, "-Trunc", self.trunc, "-Gpu 0 1 -Serial 0",
                    "-OutStack 0", "-SumRange 0 0")
                motionCor_job.add_inputs(fraction_file)

            
            motionCor_job.add_outputs(mrc_file, stage_out=False, register_replica=False)
            motionCor_job.add_outputs(dw_file, stage_out=True, register_replica=False)
            self.wf.add_jobs(motionCor_job)

            # gctf
            ctf_star_file = File(mrc_file_name.replace(".mrc",".star"))
            #ctf_pf_file = File(mrc_file_name.replace(".mrc","_pf.mrc"))
            ctf_file = File(mrc_file_name.replace(".mrc",".ctf"))
            gctf_log_file = File(mrc_file_name.replace(".mrc","_gctf.log"))
                        
            
            gctf_job = (
                Job("gctf").add_args("--apix", self.apix, "--kV", self.kev, "--Cs", "2.7", "--ac", "0.1",
                                     "--ctfstar", ctf_star_file, "--gid", "0", "--boxsize", "512", mrc_file)
            )

            gctf_job.add_inputs(mrc_file)
            gctf_job.add_outputs(ctf_star_file, stage_out=True, register_replica=False)
            #gctf_job.add_outputs(ctf_pf_file, stage_out=True, register_replica=True)
            gctf_job.add_outputs(ctf_file, stage_out=True, register_replica=False)
            gctf_job.add_outputs(gctf_log_file, stage_out=True, register_replica=False)
            self.wf.add_jobs(gctf_job)

            # e2proc2d - motion-corrected to jpg, then resize to 20% size
            dw_jpg_name = dw_file_name.replace("_DW.mrc","_DW_fs.jpg")
            dw_jpg_file = File(dw_jpg_name)
            e2proc2d_job1 = Job("e2proc2d")            
            e2proc2d_job1.add_inputs(dw_file)
            e2proc2d_job1.add_outputs(dw_jpg_file, stage_out=True, register_replica=False)
            e2proc2d_job1.add_args("--average", dw_file, dw_jpg_file)
            self.wf.add_jobs(e2proc2d_job1)
            magick_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg",".jpg"))
            magick_resize = Job("magick")
            magick_resize.add_inputs(dw_jpg_file)
            magick_resize.add_outputs(magick_jpg_file, stage_out=True, register_replica=False)
            magick_resize.add_args("convert", "-resize", '20%', dw_jpg_file, magick_jpg_file)
            self.wf.add_jobs(magick_resize)
            
            
            # e2proc2d - ctf to jpg
            jpg_ctf_file = File(mrc_file_name.replace(".mrc","_ctf.jpg"))
            e2proc2d_job2 = Job("e2proc2d")            
            e2proc2d_job2.add_inputs(ctf_file)
            e2proc2d_job2.add_outputs(jpg_ctf_file, stage_out=True, register_replica=False)
            e2proc2d_job2.add_args(ctf_file, jpg_ctf_file)
            self.wf.add_jobs(e2proc2d_job2)
            self.no_of_processed+=1
            
            


    def set_params(self, datum):
        self.apix = datum.apix
        self.fmdose = datum.fmdose
        self.kev = datum.kev
        #self.particle_size = particle_size
        self.rawgainref = datum.rawgainref
        self.rawdefectsmap = datum.rawdefectsmap
        self.basename_prefix = datum.basename_prefix
        self.basename_suffix = datum.basename_suffix
        self.basename_extension = datum.basename_extension
        self.throw=datum.throw
        self.trunc=datum.trunc
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

        self.wf.plan(submit=True,
                     sites=["slurm"],
                     output_sites=["local"],
                     dir=os.getcwd(),
                     relative_dir=self.wf_name,
                     cluster=["horizontal"]
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

    def find_files3(self, root_dir, regex):
        '''
        Returns sorted list of files matching regex = root_dir+/+regex (similar to ls)
        Much faster than find_files
        eg. f=find_files2("/project/cryoem/K3_sample_dataset/20210205_mutant/Images-Disc1", "*/Data/*_fractions.tiff") to get all files
        '''
        search_path=os.path.join(root_dir,regex)
        logger.info(" ... searching for {} {}".format(search_path, regex))
        found_files = []
        for path in Path(root_dir).rglob(regex):
            found_files.append(path.name)
        
        logger.info(" ... found {} files matching {}".format(len(found_files), regex))
        return found_files

