# sim-oxog-snvf
Evaluate the performance of MOBSNVF for OXOG artifact filtering on simulated data.

The performance for MOBSNVF is benchmarked against other models - VAFSNVF (our in-house VAF based filter), SOBDetector and GATK Orientation Bias Mixture Model (GATK-OBMM).


## Dependencies

- BWA - 0.7.19
- GATK - 4.6.2.0
- bcftools
- samtools
- dlazy
- Python
- R
- SOBDetector (included)
- OpenJDK
- cromwell

### Python Libraries
- Polars
- Numpy

### R libraries

- argparser
- io
- ggplot2
- patchwork
- hrbrthemes
- viridis
- precrec
- glue
- tidyR


## Analysis Replication

All paths mentioned are relative to the repository root.

1. Clone the repository and submodules

	```bash
	git clone --recursive
	```

2. Go to the data directory and run

	```bash
	bash simulate_data.sh
	```

	- This will generate simulated data - fastqs and bams, across tumor purity, and damage extent and sequencing depth. 
	- The data is separated into datasets according to sequencing coverage.
	- Annotations describing each samples are found in the `annot/` directory.

3. Go to the ground-truth directory and run

	```bash
	bash collect.sh
	```

	This will collect the ground truths from wgsim to this directory.

4. Go to the VCF directory and run:

	```bash
	python prepare.py
	dlazy run_batch_mutect2
	python link.py
	```

	This will create VCFs from the synthesized BAM samples.

Then navigate to the 

4. Go to the oxog-snvf directory and run

	```bash
	python get_gatk.py
	python create_scripts.py
	```

	Running the `get_gatk.py` script will fetch the results from the GATK orientation bias mixture model.
	The `create_scripts.py` will generate execution script for MOBSNVF, VAFSNVF and SOBDetector in the following directories:

- `batch_scripts-mobsnvf/`, `batch_scripts-sobdetector/`, `batch_scripts-vafsnvf/`


5. From the `oxog-snvf` directory, run the OXOG filters in batch:

	```bash
	dlazy batch_scripts-mobsnvf
	dlazy batch_scripts-sobdetector
	dlazy batch_scripts-vafsnvf
	```

	- The snvf results are placed in the `oxog-snvf` directory in the following structure: `<dataset>/<oxog_filtering_model>/<sample_name>/<sample_name_oxog.<model_name>.<extension>>`

6. Navigate to the eval directory and run:

	```bash
	bash eval-all.sh
	```

	- This will generate for each samples and also overall:
		- The variants with score and ground truth for each model
		- The AUC table with AUROC and AUPRC
		- ROC coordinates
		- PRC coordinates
		- ROC and PRC plots



