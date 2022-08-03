#!/usr/bin/env python3

import configparser
import logging
import os
import pprint
import random
import re
import sys
import glob
import datetime
from pathlib import Path
from argparse import ArgumentParser

logger = logging.getLogger('cryoem')

# --- Import Pegasus API ------------------------------------------------------
from Pegasus.api import *

def split_into_n(l, n):
    """
    splits a list l into elements of length n.
    """
    result=[]
    for i in range(0, len(l), n):
        slice_item = slice(i, i + n, 1)
        result.append(l[slice_item])
    return result

class PipelineWorkflow:
    """
    Workflow handling: creation, submission etc.
    """
    wf = None
    sc = None
    tc = None
    props = None

    wf_name = None
    wf_dir = None
    session_dir = None
    inputs_dir = None


    # --- Init ----------------------------------------------------------------
    def __init__(self, base_dir, session_dir, inputs_dir, outputs_dir, debug=True, partition="debug", \
                    account="osinski_703", glite_arguments="--gres=gpu:p100:2", \
                    maxjobs=100, debug_maxjobs=10, pgss_stgt_clusters=10, cluster_size=10, \
                    no_of_files_to_proc_in_cycle=-1,no_of_gpus=2):
        self.wf_name = "motioncor2"
        self.debug = debug
        logger.info("PipelineWorkflow init")
        logger.info("debug {}".format(self.debug))
        self.base_dir = base_dir
        self.session_dir = session_dir
        
        self.wf_dir = os.path.join(self.session_dir, 'workflow-{}'.format(datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d-%H-%M-%S")))
        

        self._run_dir = os.path.join(self.wf_dir, 'motioncor2')
        self._scratch_dir = os.path.join(self.wf_dir, 'scratch')
        
        self.glite_arguments=glite_arguments
        self.inputs_dir = inputs_dir
        self.outputs_dir = outputs_dir
        self.partition = partition
        self.account = account
        self.pgss_stgt_clusters = pgss_stgt_clusters
        self.maxjobs = maxjobs
        self.debug_maxjobs = debug_maxjobs
        self.cluster_size = cluster_size
        self.no_of_files_to_proc_in_cycle = no_of_files_to_proc_in_cycle
        self.no_of_gpus = no_of_gpus
        if self.debug:
            logger.info("sbase_dir {}".format(self.base_dir))
            logger.info("session_dir {}".format(self.session_dir))
            logger.info("inputs_dir {}".format(self.inputs_dir))
            logger.info("outputs_dir {}".format(self.outputs_dir))
            logger.info("partition {}".format(self.partition))
            logger.info("account {}".format(self.account))
            logger.info("glite_arguments {}".format(self.glite_arguments))
            logger.info("no_of_gpus {}".format(self.no_of_gpus))
            logger.info("pgss_stgt_clusters {}".format(self.pgss_stgt_clusters))
            logger.info("maxjobs {}".format(self.maxjobs))
            logger.info("debug_maxjobs {}".format(self.debug_maxjobs))
            logger.info("cluster_size {}".format(self.cluster_size))
            logger.info("no_of_files_to_proc_in_cycle {}".format(self.no_of_files_to_proc_in_cycle))
        self.no_of_processed = 0
        self.no_of_raw = 0
        self.gainref_done = False
        self.defmap_done = False


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
        purl = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
        self.props["pegasus.catalog.workflow.amqp.url"] = purl
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
        dm2mrc_gainref.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        tif2mrc_gainref = Transformation(
            "tif2mrc_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_tif2mrc_wrapper.sh"),
            is_stageable=False
        )
        tif2mrc_gainref.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        newstack_gainref = Transformation(
            "newstack_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_newstack_wrapper.sh"),
            is_stageable=False
        )
        newstack_gainref.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        clip_gainref = Transformation(
            "clip_gainref",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_clip_wrapper.sh"),
            is_stageable=False
        )
        clip_gainref.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        clip_gainref_superres = Transformation(
            "clip_gainref_superres",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_clip_wrapper.sh"),
            is_stageable=False
        )
        clip_gainref_superres.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        # second - let's try to get the Defect map file:
        dm2mrc_defect_map = Transformation(
            "dm2mrc_defect_map",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imod_dm2mrc_wrapper.sh"),
            is_stageable=False
        )
        dm2mrc_defect_map.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        )
        
        #temporarily commented out
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
        
        eer2tiff = Transformation(
            "eer2tiff",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/eer2tiff_wrapper.sh"),
            is_stageable=False
        )
        eer2tiff.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #).add_profiles(Namespace.PEGASUS, key="job.aggregator.arguments", value="-n auto")
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size).add_profiles(Namespace.PEGASUS, key="job.aggregator.arguments", value="-n auto")
        
        #single GPU
        motionCor2 = Transformation(
            "MotionCor2",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper.sh"),
            is_stageable=False
        )
        motionCor2.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        gctf = Transformation(
            "gctf",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gctf_wrapper.sh"),
            is_stageable=False
        )
        gctf.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d = Transformation(
            "e2proc2d",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper.sh"),
            is_stageable=False
        )
        e2proc2d.add_pegasus_profile(cores="1",
                                     runtime="600",
                                     memory="4096",
                                     glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick = Transformation(
            "magick",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper.sh"),
            is_stageable=False
        )
        magick.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick2 = Transformation(
            "magick2",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper2.sh"),
            is_stageable=False
        )
        magick2.add_pegasus_profile( cores="1",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        slack_notify = Transformation(
            "slack_notify",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/slack_notify.sh"),
            is_stageable=False
        )
        slack_notify.add_pegasus_profile( cores="1",
                                        runtime="300",
                                        memory="2048",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        #dual GPU
        motionCor2_dual = Transformation(
            "MotionCor2_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_dual.sh"),
            is_stageable=False
        )
        motionCor2_dual.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_dual_g = Transformation(
            "MotionCor2_dual_g",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_dual_g.sh"),
            is_stageable=False
        )
        motionCor2_dual_g.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_dual_gtt = Transformation(
            "MotionCor2_dual_gtt",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_dual_gtt.sh"),
            is_stageable=False
        )
        motionCor2_dual_gtt.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_dual_tt = Transformation(
            "MotionCor2_dual_tt",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_dual_tt.sh"),
            is_stageable=False
        )
        motionCor2_dual_tt.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        gctf_dual = Transformation(
            "gctf_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gctf_wrapper_dual.sh"),
            is_stageable=False
        )
        gctf_dual.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d_dual = Transformation(
            "e2proc2d_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper_dual.sh"),
            is_stageable=False
        )
        e2proc2d_dual.add_pegasus_profile(cores="2",
                                     runtime="600",
                                     memory="4096",
                                     glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d2_dual = Transformation(
            "e2proc2d2_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d2_wrapper_dual.sh"),
            is_stageable=False
        )
        e2proc2d2_dual.add_pegasus_profile(cores="2",
                                     runtime="600",
                                     memory="4096",
                                     glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick_dual = Transformation(
            "magick_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper_dual.sh"),
            is_stageable=False
        )
        magick_dual.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick2_dual = Transformation(
            "magick2_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper2_dual.sh"),
            is_stageable=False
        )
        magick2_dual.add_pegasus_profile( cores="2",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        slack_notify_dual = Transformation(
            "slack_notify_dual",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/slack_notify_dual.sh"),
            is_stageable=False
        )
        slack_notify_dual.add_pegasus_profile( cores="2",
                                        runtime="300",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        #quad GPU
        motionCor2_quad = Transformation(
            "MotionCor2_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_quad.sh"),
            is_stageable=False
        )
        motionCor2_quad.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_quad_g = Transformation(
            "MotionCor2_quad_g",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_quad_g.sh"),
            is_stageable=False
        )
        motionCor2_quad_g.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_quad_gtt = Transformation(
            "MotionCor2_quad_gtt",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_quad_gtt.sh"),
            is_stageable=False
        )
        motionCor2_quad_gtt.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)
        motionCor2_quad_tt = Transformation(
            "MotionCor2_quad_tt",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/motioncor2_wrapper_quad_tt.sh"),
            is_stageable=False
        )
        motionCor2_quad_tt.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        gctf_quad = Transformation(
            "gctf_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/gctf_wrapper_quad.sh"),
            is_stageable=False
        )
        gctf_quad.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d_quad = Transformation(
            "e2proc2d_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d_wrapper_quad.sh"),
            is_stageable=False
        )
        e2proc2d_quad.add_pegasus_profile(cores="4",
                                     runtime="600",
                                     memory="4096",
                                     glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        e2proc2d2_quad = Transformation(
            "e2proc2d2_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/e2proc2d2_wrapper_quad.sh"),
            is_stageable=False
        )
        e2proc2d2_quad.add_pegasus_profile(cores="4",
                                     runtime="600",
                                     memory="4096",
                                     glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick_quad = Transformation(
            "magick_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper_quad.sh"),
            is_stageable=False
        )
        magick_quad.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        magick2_quad = Transformation(
            "magick2_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/imagemagick_wrapper2_quad.sh"),
            is_stageable=False
        )
        magick2_quad.add_pegasus_profile( cores="4",
                                        runtime="600",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
        ).add_profiles(Namespace.PEGASUS, key="clusters.size", value=self.cluster_size)

        slack_notify_quad = Transformation(
            "slack_notify_quad",
            site=exec_site_name,
            pfn=os.path.join(self.base_dir, "workflow/scripts/slack_notify_quad.sh"),
            is_stageable=False
        )
        slack_notify_quad.add_pegasus_profile( cores="4",
                                        runtime="300",
                                        memory="4096",
                                        glite_arguments=self.glite_arguments
        #)
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
        #single gpu
        self.tc.add_transformations(motionCor2)
        self.tc.add_transformations(gctf)
        self.tc.add_transformations(e2proc2d)
        self.tc.add_transformations(magick)
        self.tc.add_transformations(magick2)
        self.tc.add_transformations(slack_notify)
        #dual gpu
        self.tc.add_transformations(motionCor2_dual)
        self.tc.add_transformations(motionCor2_dual_g)
        self.tc.add_transformations(motionCor2_dual_gtt)
        self.tc.add_transformations(motionCor2_dual_tt)
        self.tc.add_transformations(gctf_dual)
        self.tc.add_transformations(e2proc2d_dual)
        self.tc.add_transformations(e2proc2d2_dual)
        self.tc.add_transformations(magick_dual)
        self.tc.add_transformations(magick2_dual)
        self.tc.add_transformations(slack_notify_dual)
        #quad gpu
        self.tc.add_transformations(motionCor2_quad)
        self.tc.add_transformations(motionCor2_quad_g)
        self.tc.add_transformations(motionCor2_quad_gtt)
        self.tc.add_transformations(motionCor2_quad_tt)
        self.tc.add_transformations(gctf_quad)
        self.tc.add_transformations(e2proc2d_quad)
        self.tc.add_transformations(e2proc2d2_quad)
        self.tc.add_transformations(magick_quad)
        self.tc.add_transformations(magick2_quad)
        self.tc.add_transformations(slack_notify_quad)

    # --- Replica Catalog ------------------------------------------------------
    def create_replica_catalog(self,exec_site_name="slurm"):
        self.rc = ReplicaCatalog()


    # --- Create Workflow -----------------------------------------------------
    def create_workflow(self):
        self.wf = Workflow(self.wf_name, infer_dependencies=True)

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
            Gain_Ref_path = Gain_Ref_SR_path.replace('_sr.mrc','_std.mrc')
            Gain_Ref_name = os.path.basename(Gain_Ref_path)
            Gain_Ref = File(Gain_Ref_name)
            #define flip Y Super resolution output filename
            FlipY_SR_path = Gain_Ref_SR_path.replace('_sr.mrc','_sr.flipy.mrc')
            #logger.info(" ... found {} ".format(FlipY_SR_path))
            FlipY_SR_name = os.path.basename(FlipY_SR_path)
            FlipY_SR = File(FlipY_SR_name)
            #define flip Y std resolution output filename
            FlipY_path = Gain_Ref_path.replace('_std.mrc','_std.flipy.mrc')
            FlipY_name = os.path.basename(FlipY_path)
            FlipY = File(FlipY_name)
            #convert Superres dm4 or tiff file to mrc
            #dm2mrc usage: dm2mrc infile outfile
            #tif2mrc usage: tif2mrc infile outfile
            if gainref_extension=="tiff" or gainref_extension=="gain":
                logger.info("gain reference file extension {} ...".format(gainref_extension))
                tif2mrc_gainref_sr_job = Job("tif2mrc_gainref")
                tif2mrc_gainref_sr_job.add_args(Raw_Gain_Ref_SR, Gain_Ref_SR)
                tif2mrc_gainref_sr_job.add_inputs(Raw_Gain_Ref_SR)
                tif2mrc_gainref_sr_job.add_outputs(Gain_Ref_SR, stage_out=True)
                tif2mrc_gainref_sr_job.add_profiles(Namespace.PEGASUS, "label", "grf")
            elif gainref_extension=="dm":
                logger.info("gain reference file extension {} ...".format(gainref_extension))
                dm2mrc_gainref_sr_job = Job("dm2mrc_gainref")
                dm2mrc_gainref_sr_job.add_args(Raw_Gain_Ref_SR, Gain_Ref_SR)
                dm2mrc_gainref_sr_job.add_inputs(Raw_Gain_Ref_SR)
                dm2mrc_gainref_sr_job.add_outputs(Gain_Ref_SR, stage_out=True)
                dm2mrc_gainref_sr_job.add_profiles(Namespace.PEGASUS, "label", "grf")
            else:
                logger.info("Unknown gain reference file extension {} ...".format(gainref_extension))
                raise
            #create standard resolution gain ref file from superres gain ref file
            #newstack usage here (decrease the size of Super resolution image by factor of 2)
            #newstack -bin 2 infile outfile
            newstack_gainref_job = Job("newstack_gainref")
            newstack_gainref_job.add_args("-bin", "2", Gain_Ref_SR, Gain_Ref)
            newstack_gainref_job.add_inputs(Gain_Ref_SR)
            newstack_gainref_job.add_outputs(Gain_Ref, stage_out=True)
            newstack_gainref_job.add_profiles(Namespace.PEGASUS, "label", "grf")
            #flip both gain reference files on y axis
            #clip usage here (flip img on Y axis): clip flipy infile outfile
            #std resolution
            clip_gainref_job = Job("clip_gainref")
            clip_gainref_job.add_args("flipy", Gain_Ref, FlipY)
            clip_gainref_job.add_inputs(Gain_Ref)
            clip_gainref_job.add_outputs(FlipY, stage_out=True)
            clip_gainref_job.add_profiles(Namespace.PEGASUS, "label", "grf")
            #super resolution
            clip_gainref_superres_job = Job("clip_gainref_superres")
            clip_gainref_superres_job.add_args("flipy", Gain_Ref_SR, FlipY_SR)
            clip_gainref_superres_job.add_inputs(Gain_Ref_SR)
            clip_gainref_superres_job.add_outputs(FlipY_SR, stage_out=True)
            clip_gainref_superres_job.add_profiles(Namespace.PEGASUS, "label", "grf")
            if gainref_extension == "tiff" or gainref_extension=="gain":
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
            logger.info("Gain ref NOT found - continuing without")
            Gain_Ref_SR_name = []
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
            dm2mrc_defect_map_job.add_profiles(Namespace.PEGASUS, "label", "dmf")
            self.wf.add_jobs(dm2mrc_defect_map_job)
            #self.defmap_done = True
        elif self._defect_map_done == True:
            #set variables and that is it
            Defect_Map_name=os.path.basename(self.dmf)
            Defect_Map = File(Defect_Map_name)
            self.rc.add_replica("slurm", Defect_Map, self.dmf)
        else:
            logger.info("Raw_Defect_Map_path not found")
        logger.info("Currently processing {} files. Processed list length is {}".format(len(self._file_list_to_process), len(self._processed_files_list)))
        #define filename extension
        try:
            self.basename_extension=self._file_list_to_process[0].split('.')[-1]
            self.basename_suffix=self._file_list_to_process[0].split('.')[-2].split('_')[-1]
        except:
            logger.info("Currently processing {} files. Processed list length is {}. Failed to get basename extension and suffix - using tiff and fractions".format(len(self._file_list_to_process), len(self._processed_files_list)))
            self.basename_extension="tiff"
            self.basename_suffix="fractions"

        #prepare for labelling to cluster more jobs (fastcounter tells how many images (and all jobs per image) to bundle in a cluster se;f.cluster_size) (slowcounter is the varying part of the label)
        fastcounter=0
        slowcounter=0
        #prep list of self.no_of_gpus elems
        list_of_lists_of_files_to_process=split_into_n(self._file_list_to_process, self.no_of_gpus)
        #prepare jobs
        logger.info("no_of_gpus bef loop {}".format(self.no_of_gpus))
        for element in list_of_lists_of_files_to_process:
            joblabel_index= list_of_lists_of_files_to_process.index(element)
            if fastcounter % self.cluster_size == 0:
                slowcounter+=1
            if self.no_of_gpus==1:
                for fraction_file_path in element:
                    #ffp_index is the gpu id
                    #ffp_index = element.index(fraction_file_path)
                    #single gpu, so ffp_index is 0
                    ffp_index = 0
                    fraction_file_name = os.path.basename(fraction_file_path)
                    fraction_file = File(fraction_file_name)
                    self.rc.add_replica("slurm", fraction_file_name, "file://{}".format(fraction_file_path))
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
                    if self.basename_extension=="tiff": mc2_in="-InTiff"
                    elif self.basename_extension=="mrc": mc2_in="-InMrc"
                    elif self.basename_extension=="eer": mc2_in="-InEer"
                    else:
                        logger.info("Unknown image extension - {}".format(self.basename_extension))
                        sys.exit(1)
                    mc_cmd0="{} {} -OutMrc {} -Iter 7 -Tol 0.5 -Kv {} -PixSize {} -FmDose {} -Serial 0 -OutStack 0 -SumRange 0 0 -GpuMemUsage 0.75 -Gpu {}"
                    mc_cmd1=mc_cmd0+" -Gain {} -Throw {} -Trunc {}"
                    mc_cmd2=mc_cmd0+" -Gain {}"
                    mc_cmd3=mc_cmd0+" -Throw {} -Trunc {}"
                    if len(Gain_Ref_SR_name) != 0:
                        #case where we have gain reference file and superresolution
                        if self.superresolution == True:
                            if FlipY or Gain_Ref:
                                if str(self.kev) == "300": gff=FlipY_SR
                                elif str(self.kev) == "200": gff=Gain_Ref_SR
                                else: gff=None
                        else:
                            if FlipY or Gain_Ref:
                                if str(self.kev) == "300": gff=FlipY
                                elif str(self.kev) == "200": gff=Gain_Ref
                                else: gff=None
                        if gff!=None:
                            if self.throw!=0 and self.trunc!=0:
                                motionCor_job = Job("MotionCor2").add_args(mc_cmd1.format(mc2_in, "./{}".format(fraction_file_name), \
                                                mrc_file, str(self.kev), self.apix, self.fmdose, ffp_index, gff, self.throw, self.trunc))
                            else:
                                motionCor_job = Job("MotionCor2").add_args(mc_cmd2.format(mc2_in, "./{}".format(fraction_file_name), \
                                                mrc_file, str(self.kev), self.apix, self.fmdose, ffp_index, gff))
                            motionCor_job.add_inputs(gff)
                        else:
                            #do bare mc
                            motionCor_job = Job("MotionCor2").add_args(mc_cmd0.format(mc2_in, "./{}".format(fraction_file_name), \
                                                mrc_file, str(self.kev), self.apix, self.fmdose, ffp_index))
                    else:
                        #case where we do not have gain referencee file
                        if self.throw!=0 and self.trunc!=0:
                            motionCor_job = Job("MotionCor2").add_args(mc_cmd3.format(mc2_in, "./{}".format(fraction_file_name), \
                                            mrc_file, str(self.kev), self.apix, self.fmdose, ffp_index, self.throw, self.trunc))
                        else:
                            motionCor_job = Job("MotionCor2").add_args(mc_cmd0.format(mc2_in, "./{}".format(fraction_file_name), \
                                            mrc_file, str(self.kev), self.apix, self.fmdose, ffp_index))
                    motionCor_job.add_inputs(fraction_file)
                    motionCor_job.add_outputs(mrc_file, stage_out=False, register_replica=False)
                    motionCor_job.add_outputs(dw_file, stage_out=True, register_replica=False)
                    motionCor_job.set_stdout(mc2_stdout, stage_out=True, register_replica=False)
                    motionCor_job.set_stderr(mc2_stderr, stage_out=True, register_replica=False)
                    ##motionCor_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                    motionCor_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
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
                        Job("gctf").add_args("--apix {} --kV {} --Cs 2.7 --ac 0.1 --ctfstar {} --boxsize 1024 {} --gid {}".format(\
                        self.apix, self.kev, ctf_star_file, mrc_file, ffp_index))
                    )
                    gctf_job.add_inputs(mrc_file)
                    gctf_job.add_outputs(ctf_star_file, stage_out=True, register_replica=False)
                    #gctf_job.add_outputs(ctf_pf_file, stage_out=True, register_replica=True)
                    gctf_job.add_outputs(ctf_file, stage_out=True, register_replica=False)
                    gctf_job.add_outputs(gctf_log_file, stage_out=True, register_replica=False)
                    gctf_job.set_stdout(gctf_stdout, stage_out=True, register_replica=False)
                    gctf_job.set_stderr(gctf_stderr, stage_out=True, register_replica=False)
                    ##gctf_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                    gctf_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                    self.wf.add_jobs(gctf_job)
                    # e2proc2d - motion-corrected to jpg, then resize to 20% size
                    dw_jpg_name = dw_file_name.replace("_DW.mrc","_DW_fs.jpg")
                    dw_jpg_file = File(dw_jpg_name)
                    e2proc2d_job1 = Job("e2proc2d")            
                    e2proc2d_job1.add_inputs(dw_file)
                    e2proc2d_job1.add_outputs(dw_jpg_file, stage_out=True, register_replica=False)
                    e2proc2d_job1.add_args("--process=filter.lowpass.gauss:cutoff_freq=0.1 --fixintscaling=sane", dw_file, dw_jpg_file)
                    ##e2proc2d_job1.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                    e2proc2d_job1.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))                
                    self.wf.add_jobs(e2proc2d_job1)
                    #imagemagick - resize the input jpg from about 5k to 1k px
                    magick_jpg_file = File(dw_jpg_name.replace("_DW_fs.jpg",".jpg"))
                    magick_resize = Job("magick")
                    magick_resize.add_inputs(dw_jpg_file)
                    magick_resize.add_outputs(magick_jpg_file, stage_out=True, register_replica=False)
                    magick_resize.add_args("convert", "-resize", '20%', dw_jpg_file, magick_jpg_file)
                    ##magick_resize.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                    magick_resize.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                    self.wf.add_jobs(magick_resize)
                    # e2proc2d - ctf to jpg
                    jpg_ctf_file = File(mrc_file_name.replace(".mrc","_ctf.jpg"))
                    e2proc2d_job2 = Job("e2proc2d")            
                    e2proc2d_job2.add_inputs(ctf_file)
                    e2proc2d_job2.add_outputs(jpg_ctf_file, stage_out=True, register_replica=False)
                    e2proc2d_job2.add_args("--fixintscaling=sane", ctf_file, jpg_ctf_file)
                    ##e2proc2d_job2.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                    e2proc2d_job2.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                    self.wf.add_jobs(e2proc2d_job2)
                    #imagemagick - stitch together resized jpg and add text
                    magick_combined_jpg_fn = dw_jpg_name.replace("_DW_fs.jpg","_combined.jpg")
                    magick_combined_jpg_file = File(magick_combined_jpg_fn)
                    magick_convert = Job("magick2")
                    magick_convert.add_inputs(magick_jpg_file)
                    magick_convert.add_inputs(jpg_ctf_file)
                    magick_convert.add_inputs(gctf_log_file)
                    magick_convert.add_inputs(mc2_stdout)
                    magick_convert.add_outputs(magick_combined_jpg_file, stage_out=True, register_replica=False)
                    magick_convert.add_args(magick_jpg_file, jpg_ctf_file, magick_combined_jpg_file, gctf_log_file.lfn, mc2_stdout.lfn)
                    ##magick_convert.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                    magick_convert.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                    self.wf.add_jobs(magick_convert)
                    #send notification to the slack channel
                    slack_notify_out=File(mrc_file_name.replace(".mrc","_slack_msg.txt"))
                    slack_notify_job = Job("slack_notify")
                    slack_notify_job.add_inputs(magick_combined_jpg_file)
                    slack_notify_job.add_outputs(slack_notify_out, stage_out=True, register_replica=False)
                    slack_notify_job.add_args(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), magick_combined_jpg_fn), slack_notify_out)
                    ##slack_notify_job.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                    slack_notify_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                    self.wf.add_jobs(slack_notify_job)
                    self.no_of_processed+=1
                fastcounter+=1
                
            elif self.no_of_gpus==2:
                #logger.info("no_of_gpus in the loop {}".format(self.no_of_gpus))
                #logger.info("no_of_gpus {}".format(self.no_of_gpus))
                fraction_file_path0 = element[0]
                fraction_file_path1 = element[1]
                fraction_file_name0 = os.path.basename(fraction_file_path0)
                fraction_file_name1 = os.path.basename(fraction_file_path1)
                fraction_file0 = File(fraction_file_name0)
                fraction_file1 = File(fraction_file_name1)
                self.rc.add_replica("slurm", fraction_file_name0, "file://{}".format(fraction_file_path0))
                self.rc.add_replica("slurm", fraction_file_name1, "file://{}".format(fraction_file_path1))
                # generated files will be named based on the input
                basename0 = re.sub("_%s.%s$"%(self.basename_suffix,self.basename_extension), "", fraction_file_name0)
                basename1 = re.sub("_%s.%s$"%(self.basename_suffix,self.basename_extension), "", fraction_file_name1)
                mrc_file_name0="{}.mrc".format(basename0)
                mrc_file_name1="{}.mrc".format(basename1)
                dw_file_name0="{}_DW.mrc".format(basename0)
                dw_file_name1="{}_DW.mrc".format(basename1)
                mc2_stdout_file_name0="{}_DW.stdout.txt".format(basename0)
                mc2_stdout_file_name1="{}_DW.stdout.txt".format(basename1)
                mc2_stderr_file_name0="{}_DW.stderr.txt".format(basename0)
                mc2_stderr_file_name1="{}_DW.stderr.txt".format(basename1)
                mrc_file0 = File(mrc_file_name0)
                mrc_file1 = File(mrc_file_name1)
                dw_file0 = File(dw_file_name0)
                dw_file1 = File(dw_file_name1)
                mc2_stdout0 = File(mc2_stdout_file_name0)
                mc2_stdout1 = File(mc2_stdout_file_name1)
                mc2_stderr0 = File(mc2_stderr_file_name0)
                mc2_stderr1 = File(mc2_stderr_file_name1)
                if self.basename_extension=="tiff": mc2_in="-InTiff"
                elif self.basename_extension=="mrc": mc2_in="-InMrc"
                elif self.basename_extension=="eer": mc2_in="-InEer"
                else:
                    logger.info("Unknown image extension - {}".format(self.basename_extension))
                    sys.exit(1)
                if len(Gain_Ref_SR_name) != 0:
                    #case where we have gain reference file and superresolution
                    if self.superresolution == True:
                        if FlipY or Gain_Ref:
                            if str(self.kev) == "300": gff=FlipY_SR
                            elif str(self.kev) == "200": gff=Gain_Ref_SR
                            else: gff=None
                    else:
                        if FlipY or Gain_Ref:
                            if str(self.kev) == "300": gff=FlipY
                            elif str(self.kev) == "200": gff=Gain_Ref
                            else: gff=None
                    if gff!=None:
                        if self.throw!=0 and self.trunc!=0:
                            motionCor_job = Job("MotionCor2_dual_gtt").add_args(\
                                            mc2_in, str(self.kev), self.apix, self.fmdose, gff, self.throw, self.trunc,\
                                            "./{}".format(fraction_file_name0), \
                                            mrc_file0, \
                                            "./{}".format(mc2_stderr_file_name0), \
                                            "./{}".format(mc2_stdout_file_name0), \
                                            "./{}".format(fraction_file_name1), \
                                            mrc_file1, \
                                            "./{}".format(mc2_stderr_file_name1), \
                                            "./{}".format(mc2_stdout_file_name1), \
                                            )
                            motionCor_job.add_inputs(gff)
                            motionCor_job.add_inputs(fraction_file0)
                            motionCor_job.add_inputs(fraction_file1)
                            motionCor_job.add_outputs(mrc_file0, stage_out=False, register_replica=False)
                            motionCor_job.add_outputs(mrc_file1, stage_out=False, register_replica=False)
                            motionCor_job.add_outputs(dw_file0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(dw_file1, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stdout0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stdout1, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stderr0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stderr1, stage_out=True, register_replica=False)
                        else:
                            motionCor_job = Job("MotionCor2_dual_g")
                            motionCor_job.add_args(\
                                            mc2_in, str(self.kev), self.apix, self.fmdose, gff,\
                                            "./{}".format(fraction_file_name0), \
                                            mrc_file0, \
                                            "./{}".format(mc2_stderr_file_name0), \
                                            "./{}".format(mc2_stdout_file_name0), \
                                            "./{}".format(fraction_file_name1), \
                                            mrc_file1, \
                                            "./{}".format(mc2_stderr_file_name1), \
                                            "./{}".format(mc2_stdout_file_name1), \
                                            )
                            motionCor_job.add_inputs(gff, fraction_file0, fraction_file1)
                            motionCor_job.add_outputs(mrc_file0, stage_out=False, register_replica=False)
                            motionCor_job.add_outputs(mrc_file1, stage_out=False, register_replica=False)
                            motionCor_job.add_outputs(dw_file0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(dw_file1, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stdout0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stdout1, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stderr0, stage_out=True, register_replica=False)
                            motionCor_job.add_outputs(mc2_stderr1, stage_out=True, register_replica=False)
                    else:
                        #do bare mc
                        motionCor_job = Job("MotionCor2_dual").add_args(\
                                            mc2_in, str(self.kev), self.apix, self.fmdose,\
                                            "./{}".format(fraction_file_name0), \
                                            mrc_file0, \
                                            "./{}".format(mc2_stderr_file_name0), \
                                            "./{}".format(mc2_stdout_file_name0), \
                                            "./{}".format(fraction_file_name1), \
                                            mrc_file1, \
                                            "./{}".format(mc2_stderr_file_name1), \
                                            "./{}".format(mc2_stdout_file_name1), \
                                            )
                        motionCor_job.add_inputs(fraction_file0)
                        motionCor_job.add_inputs(fraction_file1)
                        motionCor_job.add_outputs(mrc_file0, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(mrc_file1, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(dw_file0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(dw_file1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr1, stage_out=True, register_replica=False)
                else:
                    #case where we do not have gain referencee file
                    if self.throw!=0 and self.trunc!=0:
                        motionCor_job = Job("MotionCor2_dual_tt").add_args(\
                                            mc2_in, str(self.kev), self.apix, self.fmdose, self.throw, self.trunc,\
                                            "./{}".format(fraction_file_name0), \
                                            mrc_file0, \
                                            "./{}".format(mc2_stderr_file_name0), \
                                            "./{}".format(mc2_stdout_file_name0), \
                                            "./{}".format(fraction_file_name1), \
                                            mrc_file1, \
                                            "./{}".format(mc2_stderr_file_name1), \
                                            "./{}".format(mc2_stdout_file_name1), \
                                            )
                        motionCor_job.add_inputs(fraction_file0)
                        motionCor_job.add_inputs(fraction_file1)
                        motionCor_job.add_outputs(mrc_file0, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(mrc_file1, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(dw_file0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(dw_file1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr1, stage_out=True, register_replica=False)
                    else:
                        #do bare mc (just in case as a fallback)
                        motionCor_job = Job("MotionCor2_dual").add_args(\
                                            mc2_in, str(self.kev), self.apix, self.fmdose,\
                                            "./{}".format(fraction_file_name0), \
                                            mrc_file0, \
                                            "./{}".format(mc2_stderr_file_name0), \
                                            "./{}".format(mc2_stdout_file_name0), \
                                            "./{}".format(fraction_file_name1), \
                                            mrc_file1, \
                                            "./{}".format(mc2_stderr_file_name1), \
                                            "./{}".format(mc2_stdout_file_name1), \
                                            )
                        motionCor_job.add_inputs(fraction_file0)
                        motionCor_job.add_inputs(fraction_file1)
                        motionCor_job.add_outputs(mrc_file0, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(mrc_file1, stage_out=False, register_replica=False)
                        motionCor_job.add_outputs(dw_file0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(dw_file1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stdout1, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr0, stage_out=True, register_replica=False)
                        motionCor_job.add_outputs(mc2_stderr1, stage_out=True, register_replica=False)
                motionCor_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                ##motionCor_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                #motionCor_job.add_profiles(Namespace.PEGASUS, "label", "mc2")
                self.wf.add_jobs(motionCor_job)

                # gctf
                ctf_star_file0 = File(mrc_file_name0.replace(".mrc",".star"))
                ctf_star_file1 = File(mrc_file_name1.replace(".mrc",".star"))
                ctf_file0 = File(mrc_file_name0.replace(".mrc",".ctf"))
                ctf_file1 = File(mrc_file_name1.replace(".mrc",".ctf"))
                gctf_log_file0 = File(mrc_file_name0.replace(".mrc","_gctf.log"))
                gctf_log_file1 = File(mrc_file_name1.replace(".mrc","_gctf.log"))
                gctf_stdout_file_name0=mrc_file_name0.replace(".mrc","_gctf_stdout.txt")
                gctf_stdout_file_name1=mrc_file_name1.replace(".mrc","_gctf_stdout.txt")
                gctf_stderr_file_name0=mrc_file_name0.replace(".mrc","_gctf_stderr.txt")
                gctf_stderr_file_name1=mrc_file_name1.replace(".mrc","_gctf_stderr.txt")
                gctf_stdout0 = File(gctf_stdout_file_name0)
                gctf_stdout1 = File(gctf_stdout_file_name1)
                gctf_stderr0 = File(gctf_stderr_file_name0)
                gctf_stderr1 = File(gctf_stderr_file_name1)
                gctf_job = Job("gctf_dual")
                gctf_job.add_args(self.kev, self.apix,\
                    ctf_star_file0, mrc_file0, gctf_stdout0, gctf_stderr0,\
                    ctf_star_file1, mrc_file1, gctf_stdout1, gctf_stderr1,\
                    )
                gctf_job.add_inputs(mrc_file0)
                gctf_job.add_inputs(mrc_file1)
                gctf_job.add_outputs(ctf_star_file0, stage_out=True, register_replica=False)
                gctf_job.add_outputs(ctf_star_file1, stage_out=True, register_replica=False)
                gctf_job.add_outputs(ctf_file0, stage_out=True, register_replica=False)
                gctf_job.add_outputs(ctf_file1, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_log_file0, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_log_file1, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_stdout0, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_stdout1, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_stderr0, stage_out=True, register_replica=False)
                gctf_job.add_outputs(gctf_stderr1, stage_out=True, register_replica=False)
                gctf_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                ##gctf_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                #gctf_job.add_profiles(Namespace.PEGASUS, "label", "gctf")
                self.wf.add_jobs(gctf_job)




                # e2proc2d - motion-corrected to jpg, then resize to 20% size
                dw_jpg_name0 = dw_file_name0.replace("_DW.mrc","_DW_fs.jpg")
                dw_jpg_name1 = dw_file_name1.replace("_DW.mrc","_DW_fs.jpg")
                dw_jpg_file0 = File(dw_jpg_name0)
                dw_jpg_file1 = File(dw_jpg_name1)
                e2proc2d_job1 = Job("e2proc2d_dual")
                e2proc2d_job1.add_inputs(dw_file0)
                e2proc2d_job1.add_inputs(dw_file1)
                e2proc2d_job1.add_outputs(dw_jpg_file0, stage_out=True, register_replica=False)
                e2proc2d_job1.add_outputs(dw_jpg_file1, stage_out=True, register_replica=False)
                e2proc2d_job1.add_args(dw_file0, dw_jpg_file0,dw_file1, dw_jpg_file1)
                e2proc2d_job1.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                ##e2proc2d_job1.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))                
                self.wf.add_jobs(e2proc2d_job1)

                #imagemagick - resize the input jpg from about 5k to 1k px
                magick_jpg_file0 = File(dw_jpg_name0.replace("_DW_fs.jpg",".jpg"))
                magick_jpg_file1 = File(dw_jpg_name1.replace("_DW_fs.jpg",".jpg"))
                magick_resize = Job("magick_dual")
                magick_resize.add_inputs(dw_jpg_file0)
                magick_resize.add_inputs(dw_jpg_file1)
                magick_resize.add_outputs(magick_jpg_file0, stage_out=True, register_replica=False)
                magick_resize.add_outputs(magick_jpg_file1, stage_out=True, register_replica=False)
                magick_resize.add_args(dw_jpg_file0, magick_jpg_file0, dw_jpg_file0, magick_jpg_file0)
                magick_resize.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(slowcounter))
                ##magick_resize.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                self.wf.add_jobs(magick_resize)

                # e2proc2d - ctf to jpg
                jpg_ctf_file0 = File(mrc_file_name0.replace(".mrc","_ctf.jpg"))
                jpg_ctf_file1 = File(mrc_file_name1.replace(".mrc","_ctf.jpg"))
                e2proc2d_job2 = Job("e2proc2d2_dual")
                e2proc2d_job2.add_inputs(ctf_file0, ctf_file1)
                e2proc2d_job2.add_outputs(jpg_ctf_file0, stage_out=True, register_replica=False)
                e2proc2d_job2.add_outputs(jpg_ctf_file1, stage_out=True, register_replica=False)
                e2proc2d_job2.add_args(ctf_file0, jpg_ctf_file0, ctf_file1, jpg_ctf_file1)
                e2proc2d_job2.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                ##e2proc2d_job2.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                self.wf.add_jobs(e2proc2d_job2)

                #imagemagick - stitch together resized jpg and add text
                magick_combined_jpg_fn0 = dw_jpg_name0.replace("_DW_fs.jpg","_combined.jpg")
                magick_combined_jpg_fn1 = dw_jpg_name1.replace("_DW_fs.jpg","_combined.jpg")
                magick_combined_jpg_file0 = File(magick_combined_jpg_fn0)
                magick_combined_jpg_file1 = File(magick_combined_jpg_fn1)
                magick_convert = Job("magick2_dual")
                magick_convert.add_inputs(\
                                        magick_jpg_file0, jpg_ctf_file0, gctf_log_file0, mc2_stdout0,\
                                        magick_jpg_file1, jpg_ctf_file1, gctf_log_file1, mc2_stdout1,\
                                        )
                magick_convert.add_outputs(magick_combined_jpg_file0, stage_out=True, register_replica=False)
                magick_convert.add_outputs(magick_combined_jpg_file1, stage_out=True, register_replica=False)
                magick_convert.add_args(\
                        magick_jpg_file0, jpg_ctf_file0, magick_combined_jpg_file0, gctf_log_file0.lfn, mc2_stdout0.lfn,\
                        magick_jpg_file1, jpg_ctf_file1, magick_combined_jpg_file1, gctf_log_file1.lfn, mc2_stdout1.lfn,\
                        )
                magick_convert.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                ##magick_convert.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                self.wf.add_jobs(magick_convert)
                
                #send notification to the slack channel
                slack_notify_out0=File(mrc_file_name0.replace(".mrc","_slack_msg.txt"))
                slack_notify_out1=File(mrc_file_name1.replace(".mrc","_slack_msg.txt"))
                slack_notify_job = Job("slack_notify_dual")
                slack_notify_job.add_inputs(magick_combined_jpg_file0)
                slack_notify_job.add_inputs(magick_combined_jpg_file1)
                slack_notify_job.add_outputs(slack_notify_out0, stage_out=True, register_replica=False)
                slack_notify_job.add_outputs(slack_notify_out1, stage_out=True, register_replica=False)
                slack_notify_job.add_args(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), magick_combined_jpg_fn0), slack_notify_out0)
                slack_notify_job.add_args(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), magick_combined_jpg_fn1), slack_notify_out1)
                slack_notify_job.add_profiles(Namespace.PEGASUS, "label", "2-{}".format(slowcounter))
                ##slack_notify_job.add_profiles(Namespace.PEGASUS, "label", "1-{}".format(joblabel_index))
                self.wf.add_jobs(slack_notify_job)
                self.no_of_processed+=1

                fastcounter+=1
                
            elif self.no_of_gpus==4:
                #modify dual
                pass


    def set_params(self, datum):
        self.apix = datum.apix
        self.fmdose = datum.fmdose
        self.kev = datum.kev
        self._gainref_done = datum._gainref_done
        #make it go even if gain ref not found
        try: self._gain_ref_fn = datum._gain_ref_fn
        except: pass
        self._defect_map_done = datum._defect_map_done
        self._defect_map_fn = datum._defect_map_fn
        self._processed_files_list = datum._processed_files_list
        self._file_list_to_process = datum._file_list_to_process
        #TODO: future feature
        #self.particle_size = particle_size
        try:
            self.gr_sr_flipy = datum.gr_sr_flipy
            self.gr_sr = datum.gr_sr
            self.gr_std_flipy = datum.gr_std_flipy
            self.gr_std = datum.gr_std
        except: pass
        #try to set all params. do not worry if some fail
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

        logger.info("os.getcwd() {}".format(os.getcwd()))
        logger.info("self.wf_name {}".format(self.wf_name))

        self.wf.plan(submit=True,
                     sites=["slurm"],
                     output_sites=["local"],
                     dir=os.getcwd(),
                     relative_dir=self.wf_name,
                     cluster=["label"]
                    )
