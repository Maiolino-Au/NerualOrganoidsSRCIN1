from datetime import datetime
start = datetime.now()

import argparse
import os

# Inputs
parser = argparse.ArgumentParser(description='Preprocessing of scRNA-seq data')
parser.add_argument('-f', '--file', required=True, help='Path of the sparse matrix file, either .h5ad or directory containing matrix.mtx, features.tsv, and barcodes.tsv')
parser.add_argument('-n', '--name', required=False, help='Name of the project')
parser.add_argument('-o', '--output', required=True, help='Output directory for the processed .h5ad file', default='Results')
args = parser.parse_args()

# Create output directory if required
output_dir = args.output + args.name if args.name else ''
os.makedirs(output_dir, exist_ok=True) 
sc.settings.figdir = output_dir + '/figures/'

# ------------------------------------------------------------------------------------------

# Load Packages
import scanpy as sc
import scvi
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score

# ------------------------------------------------------------------------------------------
# Define functions

# Funtion to load 10X data from a directory containing containing matrix.mtx, features.tsv, and barcodes.tsv
def load_10Xdata(path):
    # Matrix
    adata = sc.read_mtx(os.path.join(path, 'matrix.mtx')).T
    # Features
    adata.var.index = pd.read_csv(os.path.join(path, 'features.tsv'), sep='\t', header=None)[0]
    adata.var.index.name = 'gene'
    adata.var_names = adata.var_names.astype(str)
    # Barcodes
    adata.obs.index = pd.read_csv(os.path.join(path, 'barcodes.tsv'), sep='\t', header=None)[0]
    adata.obs.index.name = 'barcodes'
    adata.obs_names = adata.obs_names.astype(str)
    return adata

# Doublet removal
def db_removal(adata, min_cells=10, n_top_genes=2000):
    adata_tmp = adata.copy() 
    sc.pp.filter_genes(adata_tmp, min_cells=min_cells)
    sc.pp.highly_variable_genes(adata_tmp, n_top_genes=n_top_genes, subset=True, flavor='seurat_v3')

    scvi.model.SCVI.setup_anndata(adata_tmp)
    vae = scvi.model.SCVI(adata_tmp)
    scvi.settings.dl_num_workers = 16
    vae.train()

    solo =scvi.external.SOLO.from_scvi_model(vae)
    solo.train()

    df = solo.predict()
    df['prediction']= solo.predict(soft=False)
    # df.index = df.index.map(lambda x:x[:-2])

    df.groupby('prediction').count()

    df['dif']= df.doublet - df.singlet

    subset = df[df.prediction == 'doublet']
    doublets = df[(df.prediction == 'doublet') & (df.dif >0.5)]

    adata.obs['doublet'] = adata.obs.index.isin(doublets.index)
    adata = adata[~adata.obs.doublet]
    return adata

# Remove mitochondrial and ribosomal genes 
def rm_mt_ribo(adata):
    adata.var['mt']=adata.var.index.str.startswith('MT-')

    ribo_url = "http://software.broadinstitute.org/gsea/msigdb/download_geneset.jsp?geneSetName=KEGG_RIBOSOME&fileType=txt"

    ribo_genes = pd.read_table(ribo_url, skiprows=2, header = None)

    adata.var['ribo']=adata.var_names.isin(ribo_genes[0].values)

    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt', 'ribo'], percent_top=None, log1p=False, inplace=True)

    sc.pp.filter_genes(adata, min_cells=3)

    sc.pp.filter_cells(adata, min_genes=400)

    sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt', 'pct_counts_ribo'], 
                 jitter=0.4, 
                 multi_panel=True,
                 show=False,
                 save='_QC_violin.png')

    upper_lim = np.quantile(adata.obs.n_genes_by_counts, .98)
    upper_lim

    adata = adata[adata.obs.n_genes_by_counts< upper_lim]

    adata = adata[adata.obs.pct_counts_mt< 20]
    return adata

# Normalization and log transformation
def norm_log(adata):
    if adata.X.max() > 20:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        adata.X.sum(axis =1)
        adata.raw = adata
    else:
        print('Data appears to be already normalized and log-transformed. Skipping this step.')
    return adata

# Clustering
def clustering(adata, res=1, pcs=30):
    sc.pp.regress_out(adata, ['total_counts_mt', 'pct_counts_mt', 'total_counts_ribo'])

    sc.pp.scale(adata, max_value=10)

    sc.tl.pca(adata, svd_solver='arpack')

    sc.pp.neighbors(adata, n_pcs=pcs)

    sc.tl.leiden(adata, resolution=res)

    return adata

# ------------------------------------------------------------------------------------------
# Run

# Check input type and load data accordingly
if args.file.endswith('.h5ad'): # If .h5ad file
    adata = sc.read_h5ad(args.file)
    print(f'--> {args.file} loaded successfully')
elif os.path.isdir(args.file) and all(os.path.exists(os.path.join(args.file, f)) for f in ['matrix.mtx', 'features.tsv', 'barcodes.tsv']): # If directory with 10X files
    adata = load_10Xdata(args.file)
    print(f'--> Data loaded successfully from directory {args.file}')
else: # If neither
    raise ValueError('Input file must be either a .h5ad file or a directory containing matrix.mtx, features.tsv, and barcodes.tsv')

# Preprocessing steps
db_removal(adata)   # Doublet removal
rm_mt_ribo(adata)   # Remove mitochonrial and ribosomal genes
norm_log(adata)     # Normalization and log transformation
clustering(adata)   # Clustering

# Save preprodessed data
adata.write_h5ad(os.path.join(output_dir, f'{args.name}_preprocessed.h5ad') if args.name else os.path.join(output_dir, 'preprocessed.h5ad'))

print(f'--> Preprocessed data saved to {output_dir}\nEnd of preprocessing for {args.name}' if args.name else f'--> Preprocessed data saved to {output_dir}/preprocessed.h5ad\nEnd of preprocessing')

end = datetime.now()
print(f"Duration: {end - start}")