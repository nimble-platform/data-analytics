# Copyright (c) Salzburg Research

FROM jupyter/all-spark-notebook

LABEL maintainer="Christoph Schranz <iotlab@salzburgresarch.at>"

USER root

# Installing basic tools
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  git wget python-pip unzip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip

ENV PYSPARK_PYTHON /opt/conda/bin/python


## installing es-hadoop
RUN apt-get update \
 && curl -sL http://central.maven.org/maven2/org/elasticsearch/elasticsearch-hadoop/6.2.1/elasticsearch-hadoop-6.2.1.jar
RUN set -ex \
 && apt-get update \
 && apt-get -y upgrade \
 && apt-get -y install r-base \
 && pip install --no-cache-dir elasticsearch==6.1.1 \
 && rm -rf /home/$NB_USER/.local \
 && fix-permissions $CONDA_DIR \
 && fix-permissions /home/$NB_USER


# Installing R
RUN gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9 \
 && gpg -a --export E084DAB9 | sudo apt-key add -

#RUN set -ex \
# && apt-get update \
# && apt-get -y upgrade \
# && apt-get -y install r-base \
## && pip install --no-cache-dir rpy2==2.9.2 \
# && rm -rf /home/$NB_USER/.local \
# && fix-permissions $CONDA_DIR \
# && fix-permissions /home/$NB_USER



# R packages including IRKernel which gets installed globally.
RUN conda install --quiet --yes \
    'rpy2=2.9*' \
    'r-base=3.4.1' \
    'r-irkernel=0.8*' \
    'r-plyr=1.8*' \
    'r-devtools=1.13*' \
    'r-tidyverse=1.1*' \
    'r-shiny=1.0*' \
    'r-rmarkdown=1.8*' \
    'r-forecast=8.2*' \
    'r-rsqlite=2.0*' \
    'r-reshape2=1.4*' \
    'r-nycflights13=0.2*' \
    'r-caret=6.0*' \
    'r-rcurl=1.95*' \
    'r-crayon=1.3*' \
    'r-randomforest=4.6*' \
    'r-htmltools=0.3*' \
    'r-sparklyr=0.7*' \
    'r-htmlwidgets=1.0*' \
    'r-hexbin=1.27*' && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER



# Install Julia
# install Julia packages in /opt/julia instead of $HOME
ENV JULIA_PKGDIR=/opt/julia
ENV JULIA_VERSION=0.6.2

RUN mkdir /opt/julia-${JULIA_VERSION} && \
    cd /tmp && \
    wget -q https://julialang-s3.julialang.org/bin/linux/x64/`echo ${JULIA_VERSION} | cut -d. -f 1,2`/julia-${JULIA_VERSION}-linux-x86_64.tar.gz && \
    echo "dc6ec0b13551ce78083a5849268b20684421d46a7ec46b17ec1fab88a5078580 *julia-${JULIA_VERSION}-linux-x86_64.tar.gz" | sha256sum -c - && \
    tar xzf julia-${JULIA_VERSION}-linux-x86_64.tar.gz -C /opt/julia-${JULIA_VERSION} --strip-components=1 && \
    rm /tmp/julia-${JULIA_VERSION}-linux-x86_64.tar.gz
RUN ln -fs /opt/julia-*/bin/julia /usr/local/bin/julia

# Show Julia where conda libraries are \
RUN mkdir /etc/julia && \
    echo "push!(Libdl.DL_LOAD_PATH, \"$CONDA_DIR/lib\")" >> /etc/julia/juliarc.jl && \
    # Create JULIA_PKGDIR \
    mkdir $JULIA_PKGDIR && \
    chown $NB_USER $JULIA_PKGDIR && \
fix-permissions $JULIA_PKGDIR

USER $NB_UID
# # Install IJulia as jovyan and then move the kernelspec out
# to the system share location. Avoids problems with runtime UID change not
# taking effect properly on the .local folder in the jovyan home dir.
RUN julia -e 'Pkg.init()' && \
    julia -e 'Pkg.update()' && \
    (test $TEST_ONLY_BUILD || julia -e 'Pkg.add("HDF5")') && \
    julia -e 'Pkg.add("Gadfly")' && \
    julia -e 'Pkg.add("RDatasets")' && \
    julia -e 'Pkg.add("IJulia")' && \
    # Precompile Julia packages \
    julia -e 'using IJulia' && \
    # move kernelspec out of home \
    mv $HOME/.local/share/jupyter/kernels/julia* $CONDA_DIR/share/jupyter/kernels/ && \
    chmod -R go+rx $CONDA_DIR/share/jupyter && \
    rm -rf $HOME/.local && \
fix-permissions $JULIA_PKGDIR $CONDA_DIR/share/jupyter

USER root

# Change jupyter_notebook_config.py
COPY jupyter_notebook_config.py /etc/jupyter/jupyter_notebook_config.py

