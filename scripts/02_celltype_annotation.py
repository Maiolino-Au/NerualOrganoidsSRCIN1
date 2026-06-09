from datetime import datetime
start = datetime.now()

import argparse
import os

# Inputs
parser = argparse.ArgumentParser(description='Cell type annotation of scRNA-seq data using a reference dataset')
parser.add_argument('-f', '--file', required=True, help='Path of preprocessed data (.h5ad filetype required)')
parser.add_argument('-r', '--reference', required=True, help='Path of the reference dataset (.h5ad filetype required)')
parser.add_argument('-l', '--level', required=True, help='Level(s) to transfer from the reference. If more than one, seprate them with a comma: level_1,level_2. For HNOA: annot_level_1, annot_level_2, annot_level_3_rev2, annot_level_4_rev2, cell_type')
parser.add_argument('-n', '--name', required=False, help='Name of the project')
parser.add_argument('-o', '--output', required=True, help='Output directory ', default='Results')
args = parser.parse_args()

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

# Load reference dataset
ref = sc.read_h5ad(args.reference)
ref.var.set_index('gene_names', inplace=True)
ref.var_names_make_unique()
print(f"--> Reference dataset loaded form {args.reference}")  

# Load data
adata = sc.read_h5ad(args.file)
print(f"--> Data loaded from {args.file}")  

# Genes intersection
var_names = ref.var_names.intersection(adata.var_names)
adata = adata[:, var_names].copy()
ref = ref[:, var_names].copy()

# Computing neighbors on reference
print("--> Computing neighbors on reference...")
sc.pp.pca(ref)
sc.pp.neighbors(ref)

# Annotate
print("--> Ingesting...")
levels_to_transfer = args.level.split(',')
sc.tl.ingest(adata, ref, obs=levels_to_transfer, embedding_method='pca')
print(adata.obs.columns)

sc.tl.umap(adata)

# Save annotated data
adata.write_h5ad(os.path.join(args.output, f'{args.name}_annotated.h5ad') if args.name else os.path.join(args.output, 'annotated.h5ad'))
print(f'--> Annotated data saved to {args.output}\nEnd of annotation for {args.name}' if args.name else f'--> Annotated data saved to {args.output}/annotated.h5ad\nEnd of annotation')

end = datetime.now()
print(f"Duration: {end - start}")