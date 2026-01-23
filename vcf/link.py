#!/usr/bin/env python
import polars as pl
import glob
import os
import subprocess

paths = sorted(glob.glob("cromwell-executions/bam_variant_mutect2/*/call-vcf_filter/execution/*-filtered.vcf"))


for path in paths:
    
	fname = os.path.basename(path).split("-filtered.vcf")[0]
	dataset = "_".join(fname.split("_")[:2])
	sample_name = "_".join(fname.split("_")[:-1])

	print(f"Processing {sample_name} from {dataset}")
	outdir = f"mutect2/{dataset}/{sample_name}"
	os.makedirs(outdir, exist_ok=True)
	
	outpath = f"{outdir}/{sample_name}.vcf.gz"

	strip = subprocess.run(["bcftools", "view", "-Oz", "-o", outpath, path], capture_output=True, text=True)
	print(strip.stdout)
	if strip.returncode != 0:
		raise RuntimeError(f"Error compressing {path}: {strip.stderr}")

	index = subprocess.run(["bcftools", "index", "-tf", outpath], capture_output=True, text=True)
	print(index.stdout)
	if index.returncode != 0:
		raise RuntimeError(f"Error indexing {outpath}: {index.stderr}")
	
	print(f"Written and indexed {outpath}")



## FFPolish and Ideafix will work on only PASS variants. So we create another set of VCFs with FILTER field stripped and set to PASS
for path in paths:
    
	fname = os.path.basename(path).split("-filtered.vcf")[0]
	dataset = "_".join(fname.split("_")[:2])
	sample_name = "_".join(fname.split("_")[:-1])

	print(f"Processing {sample_name} from {dataset}")
	outdir = f"mutect2_stripped-filter-annot/{dataset}/{sample_name}"
	os.makedirs(outdir, exist_ok=True)
	
	outpath = f"{outdir}/{sample_name}.vcf.gz"

	strip = subprocess.run(["bcftools", "annotate", "-x", "FILTER", "-s", "PASS", path, "-Oz", "-o", outpath], capture_output=True, text=True)
	print(strip.stdout)
	if strip.returncode != 0:
		raise RuntimeError(f"Error compressing {path}: {strip.stderr}")

	index = subprocess.run(["bcftools", "index", "-tf", outpath], capture_output=True, text=True)
	print(index.stdout)
	if index.returncode != 0:
		raise RuntimeError(f"Error indexing {outpath}: {index.stderr}")
	
	print(f"Written and indexed {outpath}")

