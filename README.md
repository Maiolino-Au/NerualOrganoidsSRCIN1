# Title?


## Environment


## Code


## Single Cell RNA sequencing Analyses
Single-cell RNA sequencing (scRNA-seq) data from [Uzquiano A. et al., 2022](https://doi.org/10.1016/j.cell.2022.09.010), comprising human neural organoids generated with Velasco's protocol CIT24  sampled at 1, 2, 3, 4, 5, and 6 months, were downloaded [here](https://singlecell.broadinstitute.org/single_cell/study/SCP1756/cortical-organoids-atlas?genes=SRCIN1&cluster=1month%20scRNA-seq&spatialGroups=1month%20Org1%20Slide-seq%2C1month%20Org2%20Slide-seq%2C1month%20Org3%20Slide-seq%2C1month%20Org4%20Slide-seq&annotation=CellType--group--cluster&subsample=all&tab=distribution#study-download). Computational analyses were conducted in Python (v3.11) within a Docker container built upon mambaorg/micromamba:1.5.8.

Preprocessing utilized scanpy (v1.10) and anndata (v0.12.16). Doublets were identified and removed using the SOLO algorithm via scvi-tools (v1.4.2). Quality control excluded genes expressed in fewer than 3 cells, cells expressing fewer than 400 genes, and low-quality cells exhibiting >20% mitochondrial transcripts or falling within the top 2% of total counts. Raw counts were normalized to 10,000 counts per cell, log1p-transformed, and scaled to a maximum value of 10 after regressing out mitochondrial and ribosomal counts. Dimensionality reduction was performed via Principal Component Analysis (PCA). A neighborhood graph was constructed using 30 principal components, and cells were clustered using the Leiden algorithm (resolution = 1.0). Cell type annotation was performed by transferring labels from [The Human Neural Organoid Atlas (HNOA)](https://doi.org/10.1038/s41586-024-08172-8) via the ingest function based on PCA embeddings.

Differential gene expression across annotated clusters was assessed using the Wilcoxon rank-sum test, with significant marker genes filtered by an adjusted p-value < 0.05. Downstream lineage analysis and visualizations, including UMAPs and violin plots, were generated using cellrank (v2.0.7), pandas (v2.3.3), numpy (v2.4.6), matplotlib (v3.10.9), seaborn (v0.13.2), and plotly (v6.8.0).
