#!/usr/bin/env Rscript
library(io)
library(precrec)
source("../common-ffpe-snvf/R/eval.R")

#' Wrapper function to evaluate a model on a dataset
#' @param dataset Name of the dataset
#' @param snvf_paths Vector of paths to SNV files with model scores
#' @param model_name Name of the model
#' @param outdir_root Root output directory for evaluation results
#' @return None
evaluate_dataset <- function(dataset, snvf_paths, model_name, outdir_root) {

	message("Evaluating model: ", model_name, " on dataset: ", dataset)

	for (snvf_path in snvf_paths) {
		
		sample_name <- unlist(strsplit(snvf_path, "/"))[5]
		message(cat("\tProcessing sample: ", sample_name, "\n"))

		ground_truth <- read.delim(file.path("../ground-truth", dataset, sample_name, sprintf("%s_orig.snv", sample_name)))
		ground_truth <- add_id(ground_truth)

		d <- read.delim(snvf_path)
		d <- preprocess_vafsnvf(d, ground_truth)
		
		## Check if true labels exist in the variant_score_truth table (d)
		## If not this means there's no overlap between FFPE and FF variants
		## Cases like these are skipped as evaluation is not supported by precrec
		if((nrow(d[d$truth, ]) == 0)){
			message(sprintf("	no true labels exist for %s", snvf_path))
			write_sample_eval(d, NULL, outdir_root, sample_name, model_name)
			next
		}
		if((nrow(d[!d$truth, ]) == 0)){
			message(sprintf("	no false labels exist for %s", snvf_path))
			write_sample_eval(d, NULL, outdir_root, sample_name, model_name)
			next
		}

		# Evaluate model performance
		eval_res <- evaluate_filter(d, model_name, sample_name)
		write_sample_eval(d, eval_res, outdir_root, sample_name, model_name)

	}


	# Overall Evaluation
	## The scores annotated with ground truth is combined into a single dataframe
	message(cat("\tperforming Evaluation across all samples from dataset: ", dataset, "\n"))

	all_eval_paths <- Sys.glob(file.path(dataset, "model-scores_truths", "*", sprintf("*%s-scores_truths.tsv", model_name)))

	all_score_truth <- do.call(
		rbind,
		lapply(all_eval_paths, function(path) {
			tokens <- unlist(strsplit(path, "/"))
			sample_name <- tokens[length(tokens) - 1]

			d <- read.delim(path)
			d$sample_name <- sample_name
			d
		})
	)

	agg_name <- sprintf("all-samples_%s", dataset)
	overall_res <- evaluate_filter(all_score_truth, model_name, agg_name)
	write_overall_eval(all_score_truth, overall_res, outdir_root, agg_name, model_name)

}

##--------------------------------------------------


## Name of model being evaluated
model_name <- "vafsnvf"

datasets <- c("sim_10x", "sim_20x", "sim_50x", "sim_100x", "sim_200x", "sim_500x", "sim_1000x")

for (dataset in datasets) {
	outdir_root <- 	dataset
	snvf_paths <- Sys.glob(file.path("../oxog-snvf", dataset, model_name, "*",  sprintf("*_oxog.%s.snv", model_name)))
	evaluate_dataset(dataset, snvf_paths, model_name, outdir_root)
}


