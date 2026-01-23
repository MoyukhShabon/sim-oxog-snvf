#!/bin/bash

## Variant calling via freebayes is disabled.
## Variant calls will be made later via Mutect2 using dedicated pipeline

set -euo pipefail

. ../setup.sh

dataset="sim_200x"

echo -e "dataset\tsample_name\tdepth\tpurity\tdamage_extent\tdamage_type\tgenuine_mutation_rate\tbase_error_rate" > "${annot}/${dataset}.tsv"

if [[ ! -f $ref ]]; then
	echo "Error: $ref does not exist." >&2
	exit 1
fi

berror=0.001  # Base error rate
nreads=20000  # Mean coverage ~200x
purities=( 0.90 0.75 0.50 0.25 0.10 0.05 0.01 )  # Cancer purity
thetas=( 0.05 )  # Rate of genuine mutations
phis=( 0.95 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1 0.05 0.025 )   # Damage rate
damage=oxog  # Damage type
depth=$(($nreads / 100))

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
			param_name=${I}_${J}_${K}
			sample_name=${dataset}_${param_name}

			## Outdir setup
			fq_dir="fq/$dataset/$sample_name"
			mkdir -p $fq_dir
			bam_dir="bam/$dataset/$sample_name"
			mkdir -p $bam_dir

			## Save parameters to json
			params="{ \"purity\": $purity, \"theta\": $theta, \"phi\": $phi, \"depth\": \"${depth}x\" }"
			echo $params | tee $fq_dir/params.json >&2

			## Append parameters to table
			echo -e "$dataset\t$sample_name\t$depth\t$purity\t$phi\t$damage\t$thetas\t$berror" >> "${annot}/${dataset}.tsv"

			# Simulate reads | Outputs orig.r1.fq, orig.r2.fq and orig.snv
			$bin/csrsim.py -s $seed -e $berror -p $purity -T $theta -n $nreads $ref $fq_dir/${sample_name}_orig

			# Use align.sh to align reads with bwa | Outputs orig.bam and orig.bai
			# "usage : $0 <prefix> <reference-fasta>"
			$bin/align.sh $fq_dir/${sample_name}_orig $bam_dir/${sample_name}_orig $ref

			# # call snvs using freebayes | Outputs orig.calls.vcf and orig.calls.snv
			# # "usage : $0 <bam> <reference-fasta>"
			# $bin/freebayes-call.sh $prefix/orig.bam $ref

			# Makes artificial damage (FFPE and oxoG) to reads
			# Damage is called using the phi parameter (-P)
			
			# damage reads | # Outputs oxog.r1.fq, oxog.r2.fq
			$bin/damage.py -s $seed -t $damage -P $phi $fq_dir/${sample_name}_orig.r1.fq $fq_dir/${sample_name}_orig.r2.fq \
				-1 $fq_dir/${sample_name}_${damage}.r1.fq -2 $fq_dir/${sample_name}_${damage}.r2.fq

			# align damaged reads | Outputs ffpe.bam, ffpe.bai, oxog.bam and oxog.bai
			$bin/align.sh $fq_dir/${sample_name}_$damage $bam_dir/${sample_name}_$damage $ref

			# # call damaged snvs | Outputs ffpe.calls.vcf, ffpe.calls.snv, oxog.calls.vcf and oxog.calls.snv
			# $bin/freebayes-call.sh $prefix/$damage.bam $ref
				
			echo -e "\n\n========== ####                Purity_Theta_Phi #### =========="
			echo -e "========== #### Simulated data ${I}_____${J}____${K} #### ==========\n\n"
			((k++))
		done
		((j++))
	done
	((i++))
done
