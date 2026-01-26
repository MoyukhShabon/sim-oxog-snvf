#!/usr/bin/env bash

set -euo pipefail

Rscript eval_gatk-obmm_precrec.R
Rscript eval_mobsnvf_precrec.R
Rscript eval_sobdetector_precrec.R
Rscript eval_vafsnvf_precrec.R
Rscript combine_results.R
Rscript make-plots.R

