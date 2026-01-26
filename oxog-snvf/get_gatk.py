#!/usr/bin/env python
import polars as pl
import glob
import os
from tqdm import tqdm

def read_variants(path:str, columns: list = ["#CHROM", "POS", "REF", "ALT", "FILTER"]) -> pl.DataFrame:
	variants = (
		pl.read_csv(path, separator="\t", comment_prefix="##", infer_schema_length=1000, columns=columns)
		.rename(lambda x: x.lstrip("#").lower())
		.with_columns(pl.col("alt").str.split(","))
		.explode("alt")
	)
	return variants

##-------------------

repo_root = ".."
vcf_paths = glob.glob(f"{repo_root}/vcf/mutect2/*/*/*_oxog.vcf.gz")


for path in tqdm(vcf_paths):
	tokens = path.split("/")
	dataset = tokens[-3]
	sample = tokens[-2]
	fname = tokens[-1].removesuffix(".gz").removesuffix(".vcf")

	vcf = read_variants(path)

	outdir = f"{dataset}/gatk-obmm/{sample}"
	os.makedirs(outdir, exist_ok=True)

	vcf.write_csv(f"{outdir}/{fname}.gatk-obmm.tsv")
	
	


