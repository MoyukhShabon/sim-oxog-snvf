#!/usr/bin/env python3

# Prepare json input files for WDL fastq_aligned_paired workflow 

import os
import json
import glob

def return_path_if_exists(path, absolute = True):
	if os.path.exists(path):
		return os.path.abspath(path) if absolute else path
	else:
		raise FileNotFoundError(f"File not found at {os.path.abspath(path)}")


# ---

# absolute path is required in the json input files for WDL
ref_root = '../../ref_hg38'
ref_fname = 'Homo_sapiens_assembly38.fasta'
align_wdl = return_path_if_exists("../../../common-ffpe-snvf/wdl/fastq_align_paired.wdl")

fq_root = '../../fq'
rg_root = os.path.abspath('../../rg')
inputs_outdir = os.path.abspath('inputs')
batch_exec_outdir = 'batch_align'
os.makedirs(batch_exec_outdir, exist_ok=True)


if not os.path.exists(inputs_outdir):
	os.makedirs(inputs_outdir)

fq_names = {path.removesuffix(".r1.fq").removesuffix(".r2.fq") for path in glob.glob(f"{fq_root}/*/*/*.fq")}



# ----

samples = []

for name in fq_names:
	sample_name = os.path.basename(name)

	rg = f"@RG\\tID:{sample_name}\\tPU:{sample_name}\\tSM:{sample_name}\\tLB:{sample_name}\\tPL:illumina"

	rg_dir = f"{rg_root}/{sample_name.removesuffix("_oxog").removesuffix("_orig")}"
	os.makedirs(rg_dir, exist_ok=True)
	
	rg_path = f"{rg_dir}/{sample_name}.rg"
	with open(rg_path, "w") as f:
		f.write(rg)

	samples.append(
		{
			'sample_name': sample_name,
			'fastqs_r1': return_path_if_exists(f"{name}.r1.fq"),
			'fastqs_r2': return_path_if_exists(f"{name}.r2.fq"),
			'rg_path' : rg_path
		}
	)
	
	




ref_fpath = os.path.join(ref_root, ref_fname)

# base wdl input
base = {
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta': return_path_if_exists(ref_fpath),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_amb': return_path_if_exists(ref_fpath + '.64.amb'),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_ann': return_path_if_exists(ref_fpath + '.64.ann'),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_alt': return_path_if_exists(ref_fpath + '.64.alt'),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_pac': return_path_if_exists(ref_fpath + '.64.pac'),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_bwt': return_path_if_exists(ref_fpath + '.64.bwt'),
	'fastq_align_paired.fastq_bwa_mem_paired.ref_fasta_sa': return_path_if_exists(ref_fpath + '.64.sa'),
	'fastq_align_paired.fastq_bwa_mem_paired.cpu': 4,
	'fastq_align_paired.fastq_bwa_mem_paired.memory_gb': 12,
	'fastq_align_paired.fastq_bwa_mem_paired.preemptible_tries': 1,
	'fastq_align_paired.bam_sort_coord.cpu': 4,
	'fastq_align_paired.bam_sort_coord.memory_gb': 4,
	'fastq_align_paired.bam_sort_coord.preemptible_tries': 1,
}

# write wdl input json file for each sample
for x in samples:
	out = base.copy()
	out['fastq_align_paired.sample_id'] = x['sample_name']
	out['fastq_align_paired.fastq_bwa_mem_paired.fastqs_r1'] = [x['fastqs_r1']]
	out['fastq_align_paired.fastq_bwa_mem_paired.fastqs_r2'] = [x['fastqs_r2']]
	out['fastq_align_paired.fastq_bwa_mem_paired.rg_header'] = x["rg_path"]
	inputs_outpath = os.path.join(inputs_outdir, x['sample_name'] + '.inputs')
	with open(inputs_outpath, 'w') as outf:
		outf.write(json.dumps(out, indent=True, sort_keys=True))

	exec_outpath = os.path.join(batch_exec_outdir, x['sample_name'] + '.sh')
	content = f"cromwell run {align_wdl} -i {inputs_outpath}\n"
	with open(exec_outpath, 'w') as outf:
		outf.write(content)





