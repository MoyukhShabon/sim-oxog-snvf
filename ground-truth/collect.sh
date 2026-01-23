#!/usr/bin/env bash

set -euo pipefail

for snv in ../data/fq/*/*/*.snv; do
    
    file_name=$(basename $snv)
    sample=$(basename $(dirname $snv))
    dataset=$(basename $(dirname $(dirname $snv)))

    outdir=$dataset/$sample
    mkdir -p $outdir

    cp -l $snv $outdir/

done