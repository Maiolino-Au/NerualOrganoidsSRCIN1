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

# Create the standard 'jovyan' user early
RUN useradd -m jovyan

WORKDIR /workspace

########################################
# Create Python environment
########################################
COPY environment.yml /tmp/environment.yml

# 1. Create the base conda environment
RUN micromamba create -y -f /tmp/environment.yml && \
    micromamba clean --all --yes

# 2. Explicitly install pip packages & JupyDo requirements
RUN micromamba run -n py_env pip install --upgrade setuptools pip && \
    micromamba run -n py_env pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    micromamba run -n py_env pip install scvi-tools hnoca matplotlib-inline==0.1.6 cellrank && \
    micromamba run -n py_env pip install 'jupyterhub-singleuser>=4.0' 'jupyterlab>=4.0' 'notebook' && \
    micromamba clean --all --yes

# 3. Register the kernel
RUN micromamba run -n py_env python -m ipykernel install \
    --name py_env \
    --display-name "Python"

########################################
# Permissions & User Switch
########################################
# Ensure jovyan owns the required directories
RUN chown -R jovyan:jovyan /workspace /opt/conda

USER jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME

########################################
# Expose port and launch JupyDo Server
########################################
EXPOSE 8888

# Wrap the JupyDo command in micromamba to ensure it runs inside py_env
CMD ["micromamba", "run", "-n", "py_env", "jupyterhub-singleuser", "--allow-root"]
