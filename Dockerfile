FROM ghcr.io/maiolino-au/neuralorganoidssrcin1:v1.0.3

USER root

ARG PYVER=3.11.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    ca-certificates \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    liblzma-dev \
    tk-dev \
    uuid-dev

RUN mkdir -p /tmp/python-src /home/python4Jup \
    && wget -O /tmp/python-src/Python.tgz https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz \
    && cd /tmp/python-src \
    && tar -xzf Python.tgz \
    && cd Python-${PYVER} \
    && ./configure --prefix=/home/python4Jup --with-ensurepip=install \
    && make -j"$(nproc)" \
    && make install

RUN /home/python4Jup/bin/python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

RUN /home/python4Jup/bin/python3 -m pip install --no-cache-dir \
        jupyterhub==5.3.0 \
        jupyterlab \
        notebook \
        ipykernel \
    && useradd -m jovyan || true \
    && mkdir -p /home/python4Jup/share/jupyter/kernels

RUN /home/python4Jup/bin/python3 -m ipykernel install \
        --prefix=/home/python4Jup \
        --name py-homepython4jup \
        --display-name "Python (/home/python4Jup)" \
    && if [ -x /usr/local/anaconda/bin/python3 ]; then \
         /usr/local/anaconda/bin/python3 -m pip install --no-cache-dir ipykernel && \
         /usr/local/anaconda/bin/python3 -m ipykernel install \
           --prefix=/home/python4Jup \
           --name py-anaconda-base \
           --display-name "Python (anaconda base)"; \
       fi \
    && if [ -d /usr/local/anaconda/envs ]; then \
         for py in /usr/local/anaconda/envs/*/bin/python3; do \
           if [ -x "$py" ]; then \
             envname="$(basename "$(dirname "$(dirname "$py")")")"; \
             "$py" -m pip install --no-cache-dir ipykernel && \
             "$py" -m ipykernel install \
               --prefix=/home/python4Jup \
               --name "py-${envname}" \
               --display-name "Python (${envname})" || true; \
           fi; \
         done; \
       fi

RUN if command -v R >/dev/null 2>&1; then \
         R -e "if (!requireNamespace('IRkernel', quietly=TRUE)) install.packages('IRkernel', repos='https://cloud.r-project.org')" && \
         PATH="/home/python4Jup/bin:$PATH" R -e "IRkernel::installspec(user = FALSE, name = 'ir', displayname = 'R', prefix='/home/python4Jup')"; \
       fi \
    && chown -R jovyan:jovyan /home/jovyan /home/python4Jup \
    && rm -rf /var/lib/apt/lists/* /tmp/python-src

ENV HOME=/home/jovyan
WORKDIR /home/jovyan
USER jovyan

ENTRYPOINT []
CMD ["/home/python4Jup/bin/jupyterhub-singleuser", "--allow-root"]
