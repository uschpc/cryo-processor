#!/bin/sh

pegasus-plan --conf pegasus.properties \
    --dir submit \
    --sites slurm \
    --output-sites local \
    --cleanup leaf \
    --force \
    workflow.yml
