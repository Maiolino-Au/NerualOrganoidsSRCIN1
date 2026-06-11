FROM mambaorg/micromamba:1.5.8

# Set environment variables
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH=/opt/conda/bin:$PATH

USER root

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy environment files (optional future extension)
WORKDIR /workspace

########################################
# Create Python environment
########################################
COPY environment.yml /tmp/environment.yml

# 1. Create the base conda environment
RUN micromamba create -y -f /tmp/environment.yml && \
    micromamba clean --all --yes

# 2. Explicitly install pip packages
RUN micromamba run -n py_env pip install --upgrade setuptools pip
RUN micromamba run -n py_env pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN micromamba run -n py_env pip install scvi-tools hnoca matplotlib-inline==0.1.6
RUN micromamba run -n py_env pip install cellrank
RUN micromamba clean --all --yes

# 3. Register the kernel
RUN micromamba run -n py_env python -m ipykernel install \
    --name py_env \
    --display-name "Python"

########################################
# Cleanup
########################################
RUN micromamba clean --all --yes

########################################
# Expose port and launch JupyterLab
########################################
EXPOSE 8888

WORKDIR /
ENV SHELL=/bin/bash
CMD ["micromamba", "run", "-n", "py_env", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.allow_origin=*", "--ServerApp.token="]
