from datetime import datetime
start = datetime.now()

import argparse
import os

# Inputs
parser = argparse.ArgumentParser(description='Analysis of scRNA-seq data')
parser.add_argument('-f', '--file', required=True, help='Path to data (.h5ad filetype required)')
parser.add_argument('-l', '--level', required=True, help='Level(s) of annotation and/or clustering. If more than one, seprate them with a comma: level_1,level_2')
parser.add_argument('-g', '--genes_of_interest', required=True, help='Genes of interest. If more than one, seprate them with a comma')
parser.add_argument('-h', '--housekeeping_genes', required=False, help='Housekeeping genes. If more than one, seprate them with a comma', default='RPL13A,RPLP0,ACTB,GAPDH')
parser.add_argument('-n', '--name', required=False, help='Name of the project')
parser.add_argument('-o', '--output', required=True, help='Output directory ', default='Results')
args = parser.parse_args()

output_dir = args.output + '/' + args.name if args.name else args.output
os.makedirs(output_dir, exist_ok=True)
sc.settings.figdir = output_dir + '/figures/'

# Header for the logs
print(f'Analysis of {args.name}' if args.name else 'Analysis',
      f'\n--> File path: {args.file}',
      f'\n--> Output directory: {output_dir}',
      f'\n--> Annotation/clustering level(s): {args.level}',
      f'\n--> Genes of interest: {args.genes_of_interest}',
      f'\n--> Housekeeping genes: ' + (f'{args.housekeeping_genes}' if args.housekeeping_genes else 'none'),
      '\n\n--> Starting now\n\n')

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
import scvelo as scv

# ------------------------------------------------------------------------------------------

# Load data
print(f'--> Loading data from {args.file}')
adata = sc.read_h5ad(args.file)
#if : # Check the object

print(f'--> Data loaded from {args.file}')

# UMAPs, Violin plots, and args separation
print(f'--> Making plots for {args.name}')

# Plain UMAPs
args.levels = args.level.split(',')
for level in args.levels: # FIX THE LEVEL MESS ______________________________________________________________________________++++++++++++++++++++++++++++++++++++++++++++
    sc.pl.umap(adata, 
               color=level, 
               title=f'{args.name} - {level}', 
               save=f'{args.name}_{level}_umap.png',
               show=False)
    
# Genes of interest
args.goi = args.genes_of_interest.split(',')
for gene in args.goi:
    sc.pl.umap(adata, 
               color=gene, 
               use_raw=True, 
               color_map='Reds', 
               vmax='p99',
               title=f'{args.name} - {gene}', 
               save=f'{args.name}_goi_raw_{gene}_umap.png',
               show=False)
    
    sc.pl.violin(adata, 
               keys=gene,
               groupby=level,
               use_raw=True,
               rotation=90,
               title=f'{args.name} - {gene}', 
               save=f'{args.name}_goi_raw_{gene}_violin.png',
               show=False)
    
# Housekeeping genes
args.hk = args.housekeeping_genes.split(',')
valid_hk = [g for g in args.hk if g in adata.raw.var_names]
sc.pl.stacked_violin(
    adata, 
    var_names=valid_hk, 
    groupby='leiden', 
    use_raw=True,
    title="Housekeeping Gene Distribution across Clusters",
    save=f'_{args.name}_hk_distribution.png'
)    

# Subset adata
print(f'--> Subsetting adata for {args.name}')
cells_to_remove = ['EC', 'MC', 'NC Derivatives', 'CP', 'PSC', 'Microglia']
mask = (~adata.obs[level].isin(cells_to_remove)) & (~adata.obs['leiden'].isin(clusters_to_remove))
adata = adata[mask]

# UMAPs, Violin plots, and args separation
print(f'--> Making plots for subsetted adata: {args.name}')

# Plain UMAPs
args.levels = args.level.split(',')
for level in args.levels:
    sc.pl.umap(adata, 
               color=level, 
               title=f'{args.name} - {level}', 
               save=f'{args.name}_{level}_umap.png',
               show=False)
    
# Genes of interest
args.goi = args.genes_of_interest.split(',')
for gene in args.goi:
    sc.pl.umap(adata, 
               color=gene, 
               use_raw=True, 
               color_map='Reds', 
               vmax='p99',
               title=f'{args.name} - {gene}', 
               save=f'{args.name}_goi_raw_{gene}_umap.png',
               show=False)
    
    sc.pl.violin(adata, 
               keys=gene,
               groupby=level,
               use_raw=True,
               rotation=90,
               title=f'{args.name} - {gene}', 
               save=f'{args.name}_goi_raw_{gene}_violin.png',
               show=False)
    
# Housekeeping genes
args.hk = args.housekeeping_genes.split(',')
valid_hk = [g for g in args.hk if g in adata.raw.var_names]
sc.pl.stacked_violin(
    adata, 
    var_names=valid_hk, 
    groupby='leiden', 
    use_raw=True,
    title="Housekeeping Gene Distribution across Clusters",
    save=f'_{args.name}_hk_distribution.png'
)    

#___________________________________________________________________________________________________-
print('--> Relative expression of genes of interest compared to housekeeping baseline')
args.housekeeping_genes = args.housekeeping_genes.split(',')
valid_hk = [g for g in args.housekeeping_genes if g in adata.raw.var_names]

if valid_hk:
        print(f'--> Calculating background signature score using: {valid_hk}')
        sc.tl.score_genes(adata, gene_list=valid_hk, score_name='hk_signature_score', use_raw=True)
        
        # Gene of interest normalized against the housekeeping signature
        for gene in args.goi:
            if gene in adata.raw.var_names:
                # Extract the raw expression array for the gene of interest
                # (.X might be sparse, so we convert to a dense 1D array)
                import scipy.sparse as sp
                gene_expr = adata.raw[:, gene].X
                if sp.issparse(gene_expr):
                    gene_expr = gene_expr.toarray().flatten()
                else:
                    gene_expr = gene_expr.flatten()
                
                # Using Subtraction because adata.raw is typically log1p transformed
                # log(Gene) - log(HK_baseline) = log(Gene / HK_baseline)
                new_col_name = f'{gene}_relative_to_hk_baseline'
                adata.obs[new_col_name] = gene_expr - adata.obs['hk_signature_score']

                #print(adata.obs)

                sc.pl.umap(adata, 
                           color=level, 
                           title=f'{args.name} - {level}', 
                           show=True)
                
                sc.pl.umap(adata, 
                           color=new_col_name, 
                           color_map='coolwarm', # coolwarm is great for showing over/under expression (diverging)
                           title=f'{args.name} - {gene} relative to HK baseline', #save=f'{args.name}_{gene}_relative_to_hk_umap.png',
                           show=True)

                ax = sc.pl.violin(adata, 
                           keys=new_col_name,
                           groupby=level,
                           rotation=90, 
                           show=False)
                ax.set_title(f'{args.name} - {gene} relative to HK baseline')
                plt.savefig(f"violin_{args.name}_{level}_{gene}_relative_to_hk_boxplot.png", bbox_inches="tight")
                plt.close()
                print(ax)


                #___________________________________________________________________________________________________-



# Gene of inerest normalized for the housekeeping gene
for gene in args.goi:
    for hk in args.hk:
        adata.obs[f'{gene}_normalized_by_{hk}'] = adata.raw[:, gene].X / adata.raw[:, hk].X

        sc.pl.umap(adata, 
                   color=f'{gene}_normalized_by_{hk}', 
                   color_map='Reds', 
                   vmax='p99',
                   title=f'{args.name} - {gene} normalized by {hk}', 
                   save=f'{args.name}_{gene}_normalized_by_{hk}_umap.png',
                   show=False)

        sc.pl.violin(adata, 
                   keys=f'{gene}_normalized_by_{hk}',
                   groupby=level,
                   rotation=90,
                   title=f'{args.name} - {gene} normalized by {hk}', 
                   save=f'{args.name}_{gene}_normalized_by_{hk}_violin.png',
                   show=False)

# DIFFERENTIALLY EXPRESSED GENES
print('--> Computing differentially expressed genes')
# Check pre-processing 
if adata.X.max() > 20: 
    print("Il dataset sembra contenere raw counts. Procedo con normalizzazione e log1p...")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

# Dizionario per salvare i risultati filtrati se vuoi usarli dopo nel notebook
filtered_results = {}

for level in args.levels:
    print(f"\n{'='*20} Analisi per: {level} {'='*20}")

# Check whether the column exists in adata.obs
    if level not in adata.obs.columns:
        print(f"ATTENZIONE: Colonna '{level}' non trovata in adata.obs. Salto.")
        continue

end = datetime.now()
print(f"Duration: {end - start}")