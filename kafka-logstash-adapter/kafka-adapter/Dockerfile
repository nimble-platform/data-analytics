FROM python:3.5.4

ARG LIBRDKAFKA_VERSION
ARG CONFLUENT_KAFKA_VERSION

# test internet connection and dns settings. If apt-get update fails, restart 
# docker service, check internet connection and dns settings in /etc/docker/daemon.json
RUN apt-get update 

# install librdkafka client
# ENV LIBRDKAFKA_VERSION 0.11.1
RUN apt-get update && \
    git clone https://github.com/edenhill/librdkafka && cd librdkafka && \
    git checkout v${LIBRDKAFKA_VERSION} && \
    ./configure && make && make install && ldconfig


# install confluent-kafka-client
# ENV CONFLUENT_KAFKA_VERSION 0.9.1.2
RUN pip install confluent-kafka==${CONFLUENT_KAFKA_VERSION}

RUN mkdir /home/src
COPY src /home/src

WORKDIR /home/code
RUN pip install -r /home/src/requirements.txt


# call db-apdater in yml


