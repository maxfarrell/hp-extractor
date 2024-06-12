# hp-extractor
Host-Pathogen Relation Extraction


## Dataset

The underlying dataset comes from the CLOVERT database (a more inclusive version of [CLOVER](https://researchonline.lshtm.ac.uk/id/eprint/4661906/7/Gibb_etal_2021_Data-proliferation-reconciliation-and-synthesis.pdf))

I have pulled abstracts for as many of the underlying papers as possible. 

Due to the way this database was built, We can assume that the abstracts descibe some evidence of an interaction between the **Host** and **Parasite** taxa (names in meta-data).

## Name issues

For some subset of the entries in the **Host** and **Parasite** columns, these names match the abstract verbatim, and can be converted to labels for training, testing, and validation of models. 

However, the CLOVERT meta-data has undergone some name harmonization (essentially making sure different versions of a species name are converted to a single accepted form). If I remember corretly, this harmonization is more common for host names than parasite names. Therefore, one task could be to identify the host and parasite names as they appear in each abstract, and their positions. This would help greatly increase the amount of labelled training data we have for downstream tasks. 

## Existing Language Models for Biodiversity

[TaxoNERD](https://github.com/nleguillarme/taxonerd/releases) is a model that can recognize species names (including common names and Latin binomials) and may be good for identifying host and parasite names out of the box.

[BiodivBERT](https://huggingface.co/NoYo25/BiodivBERT) is a model that can do both Named Entity Recognition and Relation Extraction, so may be a good foundation model for identifying host-parasite interactions.

