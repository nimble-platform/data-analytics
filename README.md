# Data Analytics Stack with ELK Stack, Zeppelin, Spark and DB-adapter to stream data from a kafka broker


Based on the official Docker images: (based on [deviantony's stack](https://github.com/deviantony/docker-elk))
* [Elasticsearch 6.0](https://github.com/elastic/elasticsearch-docker)
* [Logstash 6.0](https://github.com/elastic/logstash-docker)
* [Kibana 6.0](https://github.com/elastic/kibana-docker)

Zeppelin Notebook based on Hadoop, Spark and Anaconda:
* [Spark 2.1.1](http://spark.apache.org/docs/2.1.1)
* [Hadoop 2.7.3](http://hadoop.apache.org/docs/r2.7.3)
* [PySpark](http://spark.apache.org/docs/2.1.1/api/python)
* [Anaconda3-5](https://www.anaconda.com/distribution/)

Plus the Kafka Adapter based on the components:
* Kafka Client [librdkafka](https://github.com/geeknam/docker-confluent-python) version **0.11.1**
* python kafka module [confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python) version **0.9.1.2**


## Contents

1. [Requirements](#requirements)
2. [Getting started](#getting-started)
3. [Storage](#storage)
   * [How can I persist Elasticsearch data?](#how-can-i-persist-elasticsearch-data)


## Requirements

1. Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
3. Clone this repository


## Getting Started

Start the ELK stack using `docker` on a manager node:


```bash
docker service create --name registry --publish published=5001,target5000 registry:2
docker service ls
-> service registry should be listed
curl 127.0.0.1:5001/v2
->{}


cd ./elk
docker stack deploy --compose-file docker-compose.yml elk


cd ../db-adapter
docker-compose up --build -d
-> should work properly
docker-compose down --volume
docker-compose push
docker stack deploy --compose-file docker-compose.yml db-adapter


cd ../zeppelin-spark
docker-compose up --build -d
-> should work properly
docker-compose down --volume
docker-compose push
docker stack deploy --compose-file docker-compose.yml db-adapter

```

The flag `-d` stands for running it in background (detached mode).
The docker-compose containers have to be shut down with the `--volume` flag.


Watch the logs with:

```bash
docker service logs -f <container-id>
```


Give Kibana about 2 minutes to initialize, then access the Kibana web UI by hitting
[http://localhost:5601](http://localhost:5601) with a web browser.
tra
By default, the stack exposes the following ports:
* 8080: Swarm Visalizer
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana
* 3030: Kafka-ELK HTTP
* 8088: Zeppelin GUI


The Kafka-Adapter should now automatically fetch data from the kafka message bus on topic **SensorData**. However, the selected topics can be specified in `kafka-adapter/Dockerfile` by setting the environment
variables of logstash. KAFKA_TOPICS should be of the form "topic1,topic2,topic3,..."

To test the ELK Stack itself (without the kafka adapter), inject example log entries via TCP by:

```bash
$ nc localhost 5000 < /path/to/logfile.log
```


## Initial setup

### Default Kibana index pattern creation

When Kibana launches for the first time, it is not configured with any index pattern. If you are using the Kafka Adapter and consume data, just follow the instructions in `Via the Kibana web UI` and your configuration will be saved in the mounted directory `elasticsearch/data/`.

#### Via the Kibana web UI

**NOTE**: You need to inject data into Logstash before being able to configure a Logstash index pattern via the Kibana web
UI. Then all you have to do is hit the *Create* button.

Refer to [Connect Kibana with
Elasticsearch](https://www.elastic.co/guide/en/kibana/current/connect-to-elasticsearch.html) for detailed instructions
about the index pattern configuration.

#### On the command line

Run this command to create a customized Logstash index pattern:

```bash
$ curl -XPUT -D- 'http://localhost:9200/.kibana/index-pattern/logstash-*' \
    -H 'Content-Type: application/json' \
    -d '{"title" : "logstash-*", "timeFieldName": "@timestamp", "notExpandable": true}'
```

This command will mark the Logstash index pattern as the default index pattern:

```bash
$ curl -XPUT -D- 'http://localhost:9200/.kibana/config/5.6.2' \
    -H 'Content-Type: application/json' \
    -d '{"defaultIndex": "logstash-*"}'
```



## Storage

### How can I persist Elasticsearch data?

The data stored in Elasticsearch over swarms will be distributed over the cluster.
To capture the data, creating snapshots is needed. This [tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-snapshots.html) explains how to do that:

