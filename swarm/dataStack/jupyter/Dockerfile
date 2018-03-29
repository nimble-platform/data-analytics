# Copyright (c) Salzburg Research

FROM jupyter/all-spark-notebook

LABEL maintainer="Christoph Schranz <iotlab@salzburgresarch.at>"

USER root

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git wget python-pip unzip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*


ENV PYSPARK_PYTHON /opt/conda/bin/python


## installing es-hadoop
RUN apt-get update \
 && curl -sL http://central.maven.org/maven2/org/elasticsearch/elasticsearch-hadoop/6.2.1/elasticsearch-hadoop-6.2.1.jar


#RUN pip install --no-cache-dir && \
#    elasticsearch==6.1.1 && \
#    rm -rf /home/$NB_USER/.local && \
#    fix-permissions $CONDA_DIR && \
#    fix-permissions /home/$NB_USER

#USER jovyan

RUN apt-get remove r-base-core \
 && gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9 \
 && gpg -a --export E084DAB9 | sudo apt-key add -

RUN set -ex \
 && buildDeps=' \
    elasticsearch==6.1.1 \
    rpy2==2.9.2 \
 ' \
 && apt-get update \
 && apt-get -y upgrade \
 && apt-get -y install r-base \
 && pip install --no-cache-dir $buildDeps \
 && rm -rf /home/$NB_USER/.local \
 && fix-permissions $CONDA_DIR \
 && fix-permissions /home/$NB_USER



# Change jupyter_notebook_config.py
COPY jupyter_notebook_config.py /etc/jupyter/jupyter_notebook_config.py

# not copy this folder, because we are using the samba share now
#COPY work/ /home/jovyan/work/


# these 2 commands where uncommented. it seems that it is also possible without it
#RUN chmod -R 755 /home/jovyan
#RUN chown -R jovyan:users /home/jovyan


