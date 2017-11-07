FROM python:3.5

# test internet connection and dns settings. If apt-get update fails, restart 
# docker service or check dns settings in /etc/default/docker
RUN apt-get update 


# install librdkafka client
ENV LIBRDKAFKA_VERSION 0.11.1
RUN wget --quiet https://github.com/edenhill/librdkafka/archive/v${LIBRDKAFKA_VERSION}.tar.gz -O /root/librdkafka-v${LIBRDKAFKA_VERSION}.tar.gz

RUN tar -xzf /root/librdkafka-v${LIBRDKAFKA_VERSION}.tar.gz -C /root
RUN cd /root/librdkafka-${LIBRDKAFKA_VERSION} && \
    ./configure && make && make install && make clean && ./configure --clean

ENV CPLUS_INCLUDE_PATH /usr/local/include
ENV LIBRARY_PATH /usr/local/lib
ENV LD_LIBRARY_PATH /usr/local/lib


# install pip packages
RUN pip install confluent-kafka==0.9.1.2

RUN mkdir /home/code
ADD code/requirements.txt /home/code
ADD code/kafka-adapter.py /home/code

WORKDIR /home/code
RUN pip install -r /home/code/requirements.txt


# set environment variables for logstash communication
ENV LOGSTASH_HOST logstash
ENV LOGSTASH_PORT 5000
# seperate topics with ","
ENV KAFKA_TOPICS "SensorData"

# run kafka-apdater
ENTRYPOINT ["python"]
CMD ["/home/code/kafka-adapter.py"]
