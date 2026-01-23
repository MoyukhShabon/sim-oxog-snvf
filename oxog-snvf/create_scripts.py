#!/usr/bin/env python
import polars as pl
import os
import glob

def return_path_if_exists(path, absolute=True):
	if os.path.exists(path):
		return os.path.abspath(path) if absolute else path
	else:
		raise FileNotFoundError(f"File not found: {path}")

def get_script_content(model, vcf_path, bam_path, outdir, ref_path):
	if model in ["mobsnvf"]:
		script_content = [
			"#!/usr/bin/env bash\n",
			"set -euo pipefail\n\n",
			f"bash {model_script_path(model)} {bam_path} {vcf_path} {outdir} {ref_path}\n"
		]
		
	elif model in ["vafsnvf", "sobdetector"]:
		script_content = [
			"#!/usr/bin/env bash\n",
			"set -euo pipefail\n\n",
			f"bash {model_script_path(model)} {bam_path} {vcf_path} {outdir}\n"
		]

	return script_content

##-------------------


ref_path = return_path_if_exists("../data/ref/tp53_hg38.fasta")
model_script_path = lambda model : return_path_if_exists(f"../common-ffpe-snvf/templates/oxog-snvf/{model}.sh.template")
models = ["mobsnvf", "vafsnvf", "sobdetector"]

##--------------------


vcf_paths = [os.path.abspath(path) for path in sorted(glob.glob("../vcf/mutect2/*/*/*.vcf.gz")) if "oxog" in os.path.basename(path)]


for model in models:
	
	print(f"Creating execution scripts for '{model}'")
	exec_script_outdir  = f"batch_scripts-{model}"
	os.makedirs(exec_script_outdir, exist_ok=True)

	for i, vcf_path in enumerate(vcf_paths):
		
		dataset = vcf_path.split("/")[-3]
		sample = vcf_path.split("/")[-2]
		file_stem = vcf_path.split("/")[-1].split(".")[0]
		bam_path = return_path_if_exists(f"../data/bam/{dataset}/{sample}/{sample}_oxog.bam")

		print(f"\t {i+1} sample: {vcf_path}")

		result_outdir = os.path.abspath(f"{dataset}/{model}/{sample}")
		
		script_content = get_script_content(model, vcf_path, bam_path, result_outdir, ref_path)

		with open(f"{exec_script_outdir}/{model}_{file_stem}.sh", "w") as f:
			f.writelines(script_content)

		


