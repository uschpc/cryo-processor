#!/bin/sh

export PYTHONPATH=/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu/lib64/python3.6/site-packages:/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu/lib64/pegasus/externals/python:/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu/lib64/python3.6/site-packages

#### Executing Workflow Generator ####
./cryoem-workflow/workflow_generator.py -s -e slurm -o workflow.yml
#### Generating Pegasus Properties ####
echo "pegasus.transfer.arguments = -m 1" > pegasus.properties
#### Generating Sites Catalog ####
python3 /home1/csul/.pegasus/pegasushub/5.0/Sites.py \
    --execution-site SLURM \
    --project-name "hpcroot" \
    --queue-name "debug" \
    --pegasus-home "/spack/apps/linux-centos7-x86_64/gcc-8.3.0/pegasus-5.0.0-esezn6jgoegtjkugiaacbdotigbgevwu" \
    --scratch-parent-dir /project/cryoem/sample-datasets/sample_workflow \
    --storage-parent-dir /project/cryoem/sample-datasets/sample_workflow
