# FROM ubuntu
# ENV DEBIAN_FRONTEND=noninteractive
# RUN apt-get -y update && apt-get -y upgrade && apt-get -y install r-base
FROM satijalab/seurat:5.0.0
RUN apt-get -y install gdebi-core wget apt-transport-https ca-certificates curl gnupg lsb-release

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common dirmngr gpg curl build-essential \
    libudunits2-dev libgdal-dev gfortran fort77 pandoc git nano \
    xorg-dev liblzma-dev libblas-dev gobjc++ aptitude libbz2-dev \
    libpcre3-dev libreadline-dev libcurl4-openssl-dev libssl-dev \
    libgit2-dev libharfbuzz-dev libfribidi-dev cmake libcurl4-gnutls-dev \
    libxml2-dev libcairo2-dev libfontconfig1-dev libfreetype6-dev \
    libpng-dev libtiff5-dev libjpeg-dev make libxt-dev liblapack-dev \
    sudo zlib1g-dev libncurses5-dev && \
    rm -rf /var/lib/apt/lists/*

# RUN wget https://download2.rstudio.org/server/jammy/amd64/rstudio-server-2023.12.1-402-amd64.deb
# RUN gdebi -n rstudio-server-2023.12.1-402-amd64.deb
# RUN useradd rstudio -p "\$y\$j9T\$/.6YKeUOB4ifaPjuG/xaC1\$0162SW98NtTo5c6I7uXbwlNlKGuu9LTcUanCzz6DF/C" -d /home/rstudio -m

# Python
# Install JupyterLab
RUN apt update && apt install -y python3 python3-pip python3-venv
# create a virtual environment in which JupyterLab can be installed
RUN python3 -m venv /opt/venv
# Activate virtual environment and install JupyterLab
RUN /opt/venv/bin/pip install --upgrade pip && /opt/venv/bin/pip install jupyterlab
# Set the virtual environment as the default Python path
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install anndata h5py numpy scipy pandas scanpy scib scvi muon

# R
RUN Rscript -e 'install.packages(c("devtools", "dplyr", "ggplot2", "tidyr", "stringr", "viridis", "ggthemes", "tidyverse", "ggsignif", "umap", "heatmap3", "plyr", "compareGroups", "dbscan", "reshape2", "msigdbr", "BiocManager", "tibble", "purrr", "magrittr", "ggplotify", "ggrepel", "igraph", "readxl", "pathviewr", "Seurat", "SeuratObject"), dependencies = TRUE)'
RUN Rscript -e 'BiocManager::install(c("limma", "Glimma", "edgeR", "scran", "fgsea", "DESeq2", "ensembldb", "BiocGenerics", "DelayedArray", "DelayedMatrixStats", "lme4", "S4Vectors", "SingleCellExperiment", "SummarizedExperiment", "MAST", "batchelor", "HDF5Array", "terra", "ggrastr", "topGO", "org.Hs.eg.db", "clusterProfiler", "enrichplot", "sf", "AnnotationHub", "vsn", "ComplexHeatmap", "ADImpute", "RRHO"), update = TRUE, ask = FALSE)'
RUN Rscript -e 'install.packages(c("RNAseqQC", "misgdbr", "fcors", "FactoMineR", "factoextra", "corrplot", "dendextend", "WGCNA", "pals"), dependencies = TRUE)'
RUN Rscript -e 'devtools::install_github("Biometeor/monocle3", dependencies = TRUE)'
RUN Rscript -e 'devtools::install_github("RRHO2/RRHO2", build_opts = c("--no-resave-data", "--no-manual"))'
RUN Rscript -e 'devtools::install_version("matrixStats", version="1.1.0")'

RUN R -e "remotes::install_github('immunogenomics/presto')"

RUN R -e "devtools::install_github('dviraran/SingleR')"
RUN R -e "install.packages('tictoc')"
RUN R -e "BiocManager::install(c('zellkonverter', 'scuttle', 'scater'))"
RUN R -e "remotes::install_github('mojaveazure/seurat-disk')"

# Plots for october 2025 poster 
WORKDIR /poster_oct2025
COPY Poster_oct2025/functions_poster_oct2025.r .
COPY Poster_oct2025/run_poster_oct2025.r .

RUN chmod +x /home/*
ENV SHELL=/bin/bash
CMD ["/bin/bash"]
#CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=9999", "--no-browser", "--allow-root", "--ServerApp.allow_origin='*'", "--ServerApp.token=''"]
