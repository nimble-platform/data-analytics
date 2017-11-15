FROM python:3.5

# test internet connection and dns settings. If apt-get update fails, restart 
# docker service or check dns settings in /etc/default/docker
RUN apt-get update 

# install librdkafka client
ENV LIBRDKAFKA_VERSION 0.11.1
# ENV LIBRDKAFKA_VERSION 0.9.2-RC1
# ENV LIBRDKAFKA_VERSION 0.9.2

RUN apt-get update && \
    git clone https://github.com/edenhill/librdkafka && cd librdkafka && \
    git checkout v${LIBRDKAFKA_VERSION} && \
    ./configure && make && make install && ldconfig


RUN pip install confluent-kafka==0.9.1.2

RUN mkdir /home/code
ADD code/requirements.txt /home/code
ADD code/kafka-adapter.py /home/code

WORKDIR /home/code
RUN pip install -r /home/code/requirements.txt


# run kafka-apdater
ENTRYPOINT ["python"]
CMD ["/home/code/kafka-adapter.py"]
