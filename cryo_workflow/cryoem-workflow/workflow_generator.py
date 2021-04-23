#!/usr/bin/env python3
import os
import logging
from pathlib import Path
from argparse import ArgumentParser

logging.basicConfig(level=logging.DEBUG)

# --- Import Pegasus API ------------------------------------------------------
from Pegasus.api import *


class PipelineWorkflow:
    wf = None
    sc = None
    tc = None
    props = None

    dagfile = None
    wf_name = None
    wf_dir = None

    # --- Init ----------------------------------------------------------------
    def __init__(self, dagfile="workflow.yml"):
        self.dagfile = dagfile
        self.wf_name = "motioncor2"
        self.wf_dir = str(Path(__file__).parent.resolve())

    # --- Write files in directory --------------------------------------------
    def write(self):
        if not self.sc is None:
            self.sc.write()
        self.props.write()
        self.tc.write()
        self.wf.write()

    # --- Configuration (Pegasus Properties) ----------------------------------
    def create_pegasus_properties(self):
        self.props = Properties()

        # props["pegasus.monitord.encoding"] = "json"
        # self.properties["pegasus.integrity.checking"] = "none"
        return

    # --- Site Catalog --------------------------------------------------------
    def create_sites_catalog(self, exec_site_name="condorpool"):
        self.sc = SiteCatalog()

        shared_scratch_dir = os.path.join(self.wf_dir, "scratch")
        local_storage_dir = os.path.join(self.wf_dir, "output")

        local = Site("local").add_directories(
            Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
                FileServer("file://" + shared_scratch_dir, Operation.ALL)
            ),
            Directory(Directory.LOCAL_STORAGE, local_storage_dir).add_file_servers(
                FileServer("file://" + local_storage_dir, Operation.ALL)
            ),
        )

        exec_site = (
            Site(exec_site_name)
            .add_pegasus_profile(style="condor",queue="main")
            .add_condor_profile(universe="vanilla")
            .add_profiles(Namespace.PEGASUS, key="data.configuration", value="condorio")
        )

        self.sc.add_sites(local, exec_site)

    # --- Transformation Catalog (Executables and Containers) -----------------
    def create_transformation_catalog(self, exec_site_name="condorpool"):
        self.tc = TransformationCatalog()

        motionCor2 = Transformation(
            "MotionCor2", site=exec_site_name, pfn="/project/cryoem/sample-datasets/sample_workflow/scripts/motioncor2_wrapper.sh", is_stageable=False
        )
        motionCor2.add_pegasus_profile( cores="8",
                                        runtime="600",
                                        glite_arguments="--gres=gpu:p100:2",
        )
        gctf = Transformation(
            "gctf", site=exec_site_name, pfn="/project/cryoem/sample-datasets/sample_workflow/scripts/gctf_wrapper.sh", is_stageable=False
        )
        gctf.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="2048",
                                        glite_arguments="--gres=gpu:p100:2",
        )

        e2proc2d = Transformation(
            "e2proc2d", site=exec_site_name, 
            pfn="/project/cryoem/sample-datasets/sample_workflow/scripts/e2proc2d_wrapper.sh",
            is_stageable=False
        )
        self.tc.add_transformations(motionCor2)
        self.tc.add_transformations(gctf)
        self.tc.add_transformations(e2proc2d)
    # --- Replica Catalog ------------------------------------------------------
    def create_replica_catalog(self,exec_site_name="condorpool"):
        self.rc = ReplicaCatalog()

        sample_dataset_dir="/project/cryoem/sample-datasets"
        raw_format="raw_{index:d}.tiff"
        for i in range(1,31):
            self.rc.add_replica( "local", raw_format.format(index=i+10000), os.path.join(sample_dataset_dir, "K3_2","raw", raw_format.format(index=i+10000) ) ) 
        self.rc.add_replica( "local", "K3_Gain_Ref_20200530_CL1g4_1x.m1.mrc", os.path.join(sample_dataset_dir, "K3_2","K3_Gain_Ref_20200530_CL1g4_1x.m1.mrc")) 
        self.rc.write()
    # --- Create Workflow -----------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)

        raw_prefix="raw_"
        mc_prefix = "mc_"
        K3_Gain_Ref = File("K3_Gain_Ref_20200530_CL1g4_1x.m1.mrc")


        for i in range(1,31):

            motionCor_job = (
            Job("MotionCor2").add_args("-InTiff", "./"+raw_prefix, "-OutMrc",
            "./"+mc_prefix, "-Gain", K3_Gain_Ref,"-Iter 7 -Tol 0.5 -RotGain 2",
            "-PixSize 1.08 -FmDose 1.275 -Throw 1 -Trunc 23 -Gpu 0 -Serial 1",
            "-OutStack 0")
            )

            motionCor_job.add_inputs(K3_Gain_Ref)

            gctf_job = (
            Job("gctf").add_args("--apix 1.08 --kV 300 --Cs 2.7 --ac 0.1",
            "--Do_phase_flip --ctfstar output.star --boxsize 1024 ")
            )

            infile_mc   = File(raw_prefix+"%d.tiff"   %(10000+i))
            mrc  = File(mc_prefix+"%d.mrc"     %(10000+i))
            DWS = File(mc_prefix+"%d_DWS.mrc" %(10000+i))

            motionCor_job.add_inputs(infile_mc)
            motionCor_job.add_outputs(mrc, stage_out=True, register_replica=True)
            motionCor_job.add_outputs(DWS, stage_out=True, register_replica=True)

            gctf_job.add_inputs(mrc)
            gctf_job.add_inputs(DWS)

            gctf_job.add_args(mrc,DWS)

            
            jpg_motionCor=File(mc_prefix+"%d.jpg"%(10000+i))
            e2proc2d_job1=Job("e2proc2d")            
            e2proc2d_job1.add_inputs(mrc)
            e2proc2d_job1.add_outputs(jpg_motionCor,stage_out=True)
            e2proc2d_job1.add_args("--scale 0.25",mrc,jpg_motionCor)

            
            for suffix in ['','_DWS']:
                POW=File(mc_prefix+"%d%s.pow" %(10000+i,suffix))
                gctf_job.add_outputs(POW, stage_out=False, register_replica=True)

                pf=File(mc_prefix+"%d%s_pf.mrc" %(10000+i,suffix))
                gctf_job.add_outputs(pf, stage_out=True, register_replica=True)

                gctf_log=File(mc_prefix+"%d%s_gctf.log" %(10000+i,suffix))
                gctf_job.add_outputs(gctf_log, stage_out=False, register_replica=True)

                epa_log=File(mc_prefix+"%d%s_EPA.log" %(10000+i,suffix))
                gctf_job.add_outputs(epa_log, stage_out=False, register_replica=True)

                ctf=File(mc_prefix+"%d%s.ctf" %(10000+i,suffix))
                gctf_job.add_outputs(ctf, stage_out=True, register_replica=True)

                if suffix != '_DWS':
                    jpg_gctf_pf=File(mc_prefix+"%d_pf.jpg"%(10000+i))

                    e2proc2d_job2=Job("e2proc2d")            
                    e2proc2d_job2.add_inputs(pf)
                    e2proc2d_job2.add_outputs(jpg_gctf_pf,stage_out=True)
                    e2proc2d_job2.add_args("--scale 0.25",pf,jpg_gctf_pf)

                    jpg_gctf_ctf=File(mc_prefix+"%d%s_ctf.jpg"%(10000+i,suffix))

                    e2proc2d_job3=Job("e2proc2d")            
                    e2proc2d_job3.add_inputs(ctf)
                    e2proc2d_job3.add_outputs(jpg_gctf_ctf,stage_out=True)
                    e2proc2d_job3.add_args("--scale 0.25",ctf,jpg_gctf_ctf)

        star_file = File("output.star")
        gctf_job.add_outputs(star_file, stage_out=True, register_replica=True)

        self.wf.add_jobs(motionCor_job)
        self.wf.add_jobs(gctf_job)
        self.wf.add_jobs(e2proc2d_job1)
        self.wf.add_jobs(e2proc2d_job2)
        self.wf.add_jobs(e2proc2d_job3)


if __name__ == "__main__":
    parser = ArgumentParser(description="Motion Correction 2 test")

    parser.add_argument(
        "-s",
        "--skip_sites_catalog",
        action="store_true",
        help="Skip site catalog creation",
    )
    parser.add_argument(
        "-e",
        "--execution_site_name",
        metavar="STR",
        type=str,
        default="condorpool",
        help="Execution site name (default: condorpool)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="STR",
        type=str,
        default="workflow.yml",
        help="Output file (default: workflow.yml)",
    )

    args = parser.parse_args()

    workflow = PipelineWorkflow(args.output)

    if not args.skip_sites_catalog:
        print("Creating execution sites...")
        workflow.create_sites_catalog(args.execution_site_name)

    print("Creating workflow properties...")
    workflow.create_pegasus_properties()
    
    print("Creating transformation catalog...")
    workflow.create_transformation_catalog(args.execution_site_name)

    print("Creating replica catalog...")
    workflow.create_replica_catalog(args.execution_site_name)

    print("Creating pipeline workflow dag...")
    workflow.create_workflow()

    workflow.write()
