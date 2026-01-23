#!/usr/bin/env python
import os
import glob
import json

def return_path_if_exists(path: str, abs=True) -> str:
	if os.path.exists(path):
		return os.path.abspath(path) if abs else path
	else:
		raise FileNotFoundError(f"File not found: {path}")

# absolute path is required in the json input files for WDL
ref_root = '../data/ref'
ref_fname = 'tp53_hg38'
vcf_root = "../data/gatk-best-practices/somatic-hg38"
bam_root = "../data/PRJEB8754/bam"
bundle_root = "../data/gatk-test-data/mutect2"


outdir = 'inputs'
batch_script_dir = "run_batch_mutect2"

os.makedirs(outdir, exist_ok=True)
os.makedirs(batch_script_dir, exist_ok=True)

ref_fpath = os.path.abspath(os.path.join(ref_root, ref_fname))
vcf_path = os.path.abspath(vcf_root)
bundle_path = os.path.abspath(bundle_root)
gatk_path = "/home/moyukh/miniconda3/envs/ffpe-bench/share/gatk4-4.6.2.0-0/gatk-package-4.6.2.0-local.jar"
mutect2_wdl_path = return_path_if_exists("../common-ffpe-snvf/wdl/bam_variant_mutect2.wdl", abs=True)


bam_paths = sorted(glob.glob("../data/bam/*/*/*.bam"))

base = {
	'bam_variant_mutect2.run_funcotator': False,
	'bam_variant_mutect2.ref_fasta': return_path_if_exists(ref_fpath + '.fasta'),
	'bam_variant_mutect2.ref_fai': return_path_if_exists(ref_fpath + '.fasta.fai'),
	'bam_variant_mutect2.ref_dict': return_path_if_exists(ref_fpath + '.dict'),
	'bam_variant_mutect2.m2_extra_args': '--disable-read-filter NotDuplicateReadFilter --downsampling-stride 1 --linked-de-bruijn-graph --max-reads-per-alignment-start 0', ## Our data is similar to targeted/amplicon sequencing. So these extra flags are used
	'bam_variant_mutect2.scatter_count': 1,
	'bam_variant_mutect2.gatk_docker': 'broadinstitute/gatk:4.6.2.0',
	'bam_variant_mutect2.gatk_override': return_path_if_exists(gatk_path),
	'bam_variant_mutect2.run_orientation_bias_mixture_model_filter': True,
	# 'bam_variant_mutect2.mutect2_scatter_mem_gb': 8,
}

for path in bam_paths:
	sample_name = path.split("/")[-1].split(".")[0]

	bam = return_path_if_exists(path, abs=True)
	bai = return_path_if_exists(f"{path}.bai", abs=True)

	# write wdl input json file for each sample
	out = base.copy()
	out['bam_variant_mutect2.tumor_bam'] = bam
	out['bam_variant_mutect2.tumor_bai'] = bai
	input_path = os.path.join(outdir, f"{sample_name}.inputs")
	with open(input_path, 'w') as outf:
		outf.write(json.dumps(out, indent=True, sort_keys=True))

	print(f"Prepared inputs for: {path}")

	content = [
		"#!/usr/bin/env bash\n",
		f"cromwell run {mutect2_wdl_path} -i {os.path.abspath(input_path)}"
	]

	with open(f"{batch_script_dir}/{sample_name}.sh", "w") as sh:
		sh.writelines(content)

	print(f"Prepared execution script for: {input_path}")

