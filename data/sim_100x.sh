#!/bin/bash

set -euo pipefail

. ../setup.sh

echo $home

outdir=grid1/input

mkdir -p $outdir

if [[ ! -f $ref ]]; then
	echo "Error: $ref does not exist." >&2
	exit 1
fi

berror=0.001  # Base error rate
nreads=10000  # Mean coverage ~100x
purities=( 0.90 0.75 0.50 0.25 0.10 )  # Cancer purity
thetas=( 0.05 )  # Rate of genuine mutations
phis=( 0.4 0.2 0.1 0.05 0.025 )   # Damage rate
damages=( ffpe oxog )  # Damage type

seed=1

i=1
for purity in "${purities[@]}"; do
	j=1
	for theta in "${thetas[@]}"; do
		k=1
		for phi in "${phis[@]}"; do
			I=$(printf '%02d' $i)
			J=$(printf '%02d' $j)
			K=$(printf '%02d' $k)

			# File path prefix
			prefix=$outdir/${I}_${J}_${K}
			mkdir -p $prefix

			params="{ \"purity\": $purity, \"theta\": $theta, \"phi\": $phi, \"depth\": \"$(($nreads / 100))x\" }"
			echo $params | tee $prefix/params.json >&2

			# Simulate reads | Outputs orig.r1.fq, orig.r2.fq and orig.snv
			$bin/csrsim.py -s $seed -e $berror -p $purity -T $theta -n $nreads $ref $prefix/orig

			# Use align.sh to align reads with bwa | Outputs orig.bam and orig.bai
			# "usage : $0 <prefix> <reference-fasta>"
			$bin/align.sh $prefix/orig $ref

			# call snvs using freebayes | Outputs orig.calls.vcf and orig.calls.snv
			# "usage : $0 <bam> <reference-fasta>"
			$bin/freebayes-call.sh $prefix/orig.bam $ref

			# Makes artificial damage (FFPE and oxoG) to reads
			# Damage is called using the phi parameter (-P)
			for damage in "${damages[@]}"; do
				# damage reads | # Outputs oxog.r1.fq, oxog.r2.fq, ffpe.r1.fq and ffpe.r2.fq
				$bin/damage.py -s $seed -t $damage -P $phi $prefix/orig.r1.fq $prefix/orig.r2.fq \
					-1 $prefix/${damage}.r1.fq -2 $prefix/${damage}.r2.fq

				# align damaged reads | Outputs ffpe.bam, ffpe.bai, oxog.bam and oxog.bai
				$bin/align.sh $prefix/$damage $ref

				# call damaged snvs | Outputs ffpe.calls.vcf, ffpe.calls.snv, oxog.calls.vcf and oxog.calls.snv
				$bin/freebayes-call.sh $prefix/$damage.bam $ref
				
			done
			echo -e "\n\n${BLUE}========== ####                Purity_Theta_Phi #### ==========${NC}\n\n"
			echo -e "\n\n${BLUE}========== #### Simulated data ${I}_____${J}____${K} #### ==========${NC}\n\n"
			((k++))
		done
		((j++))
	done
	((i++))
done

