#!/usr/bin/env python3

import configparser
import logging
import os
import pprint
import random
import re
import sys
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
    def __init__(self, base_dir, wf_dir, inputs_dir, outputs_dir, debug=False):
        self.wf_name = "motioncor2"
        self.base_dir = base_dir
        self.wf_dir = wf_dir
        self.inputs_dir = inputs_dir
        self.outputs_dir = outputs_dir
        self.debug = debug

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
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value="debug")
        else:
            exec_site.add_profiles(Namespace.PEGASUS, key="queue", value="main")

        self.sc.add_sites(local, exec_site)

    # --- Transformation Catalog (Executables and Containers) -----------------
    def create_transformation_catalog(self, exec_site_name="slurm"):
        self.tc = TransformationCatalog()

        if self.debug:
            cluster_size = 5
        else:
            cluster_size = 100

        # these are fast jobs - cluster to improve performance
        motionCor2 = Transformation(
            "MotionCor2",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper.sh"),
            is_stageable=False
        )
        motionCor2.add_pegasus_profile( cores="8",
                                        runtime="180",
                                        glite_arguments="--gres=gpu:p100:2"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=cluster_size)

        gctf = Transformation(
            "gctf",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gctf_wrapper.sh"),
            is_stageable=False
        )
        gctf.add_pegasus_profile( cores="4",
                                        runtime="180",
                                        memory="2048",
                                        glite_arguments="--gres=gpu:p100:2"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=cluster_size)

        e2proc2d = Transformation(
            "e2proc2d",
            site=exec_site_name, 
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper.sh"),
            is_stageable=False
        )
        e2proc2d.add_pegasus_profile(cores="1",
                                     runtime="180",
                                     memory="2048"
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=cluster_size)

        self.tc.add_transformations(motionCor2)
        self.tc.add_transformations(gctf)
        self.tc.add_transformations(e2proc2d)

    # --- Replica Catalog ------------------------------------------------------
    def create_replica_catalog(self,exec_site_name="slurm"):
        self.rc = ReplicaCatalog()

        

    # --- Create Workflow -----------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)

        raw_prefix="raw_"
        mc_prefix = "mc_"
        K3_Gain_Ref = File("K3_Gain_Ref_20200530_CL1g4_1x.m1.mrc")

        K3_Gain_Ref_path = self.find_files(self.inputs_dir, "_1x.m1.mrc$")[0]
        K3_Gain_Ref_name = os.path.basename(K3_Gain_Ref_path)
        K3_Gain_Ref = File(K3_Gain_Ref_name)
        self.rc.add_replica("slurm", K3_Gain_Ref_name, "file://{}".format(K3_Gain_Ref_path))

        # for each _fractions.tiff in the Images-Disc1 dir - is this correct?
        file_list = self.find_files(
                            os.path.join(self.inputs_dir, "Images-Disc1"),
                            "_fractions.tiff$")
        if self.debug:
            # when debugging, only do a fraction of the files
            file_list = random.sample(file_list, 10)
        else:
            # even for production, only process a part of the dataset (maybe change this later?)
            file_list = random.sample(file_list, 1000)

        for fraction_file_path in file_list:

            fraction_file_name = os.path.basename(fraction_file_path)
            fraction_file = File(fraction_file_name)
            self.rc.add_replica("slurm", fraction_file_name, "file://{}".format(fraction_file_path))

            # generated files will be named based on the input
            basename = re.sub("_fractions.tiff$", "", fraction_file_name)

            mrc_file = File("{}.mrc".format(basename))
            dws_file = File("{}_DWS.mrc".format(basename))

            # MotionCor2
            motionCor_job = Job("MotionCor2").add_args("-InTiff", "./{}".format(fraction_file_name), "-OutMrc",
                mrc_file, "-Gain", K3_Gain_Ref,"-Iter 7 -Tol 0.5 -RotGain 2",
                "-PixSize 1.08 -FmDose 1.275 -Throw 1 -Trunc 23 -Gpu 0 -Serial 1",
                "-OutStack 0")

            motionCor_job.add_inputs(fraction_file, K3_Gain_Ref)
            motionCor_job.add_outputs(mrc_file, dws_file, stage_out=True, register_replica=False)
            self.wf.add_jobs(motionCor_job)

            # gctf
            star_file = File("{}.star".format(basename))
            gctf_job = (
                Job("gctf").add_args("--apix", "1.08", "--kV", "300", "--Cs", "2.7", "--ac", "0.1",
                                     "--Do_phase_flip", "--ctfstar", star_file, "--boxsize", "1024")
            )

            gctf_job.add_inputs(mrc_file, dws_file)
            gctf_job.add_args(mrc_file, dws_file)
            gctf_job.add_outputs(star_file, stage_out=True, register_replica=True)

            # e2proc2d            
            jpg_motionCor_file = File("{}.jpg".format(basename))
            e2proc2d_job1 = Job("e2proc2d")            
            e2proc2d_job1.add_inputs(mrc_file)
            e2proc2d_job1.add_outputs(jpg_motionCor_file, stage_out=True)
            e2proc2d_job1.add_args("--scale 0.25", mrc_file, jpg_motionCor_file)
            
            for suffix in ['','_DWS']:
                POW_file = File("{}{}.pow".format(basename, suffix))
                gctf_job.add_outputs(POW_file, stage_out=False, register_replica=True)

                pf_file = File("{}{}_pf.mrc".format(basename, suffix))
                gctf_job.add_outputs(pf_file, stage_out=True, register_replica=True)

                gctf_log_file = File("{}{}_gctf.log".format(basename, suffix))
                gctf_job.add_outputs(gctf_log_file, stage_out=False, register_replica=True)

                epa_log_file = File("{}{}_EPA.log".format(basename, suffix))
                gctf_job.add_outputs(epa_log_file, stage_out=False, register_replica=True)

                ctf_file = File("{}{}.ctf".format(basename, suffix))
                gctf_job.add_outputs(ctf_file, stage_out=True, register_replica=True)

                if suffix != '_DWS':
                    jpg_gctf_pf_file = File("{}_pf.jpg".format(basename))

                    e2proc2d_job2=Job("e2proc2d")            
                    e2proc2d_job2.add_inputs(pf_file)
                    e2proc2d_job2.add_outputs(jpg_gctf_pf_file, stage_out=True)
                    e2proc2d_job2.add_args("--scale 0.25", pf_file, jpg_gctf_pf_file)

                    jpg_gctf_ctf_file = File("{}_ctf.jpg".format(basename))

                    e2proc2d_job3 = Job("e2proc2d")            
                    e2proc2d_job3.add_inputs(ctf_file)
                    e2proc2d_job3.add_outputs(jpg_gctf_ctf_file, stage_out=True)
                    e2proc2d_job3.add_args("--scale 0.25",ctf_file, jpg_gctf_ctf_file)

            self.wf.add_jobs(gctf_job)
            self.wf.add_jobs(e2proc2d_job1)
            self.wf.add_jobs(e2proc2d_job2)
            self.wf.add_jobs(e2proc2d_job3)


    # --- Submit Workflow -----------------------------------------------------
    def submit_workflow(self):
        
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


