# Docker ELK stack with integrated Adapter for Kafka Messages

Run the latest version of the ELK (Elasticsearch, Logstash, Kibana) and Zeppelin (along Spark, Anaconda) stack with Docker and Docker Compose.

It will give you the ability to analyze any data set by using the searching/aggregation capabilities of Elasticsearch
and the visualization power of Kibana.

Based on the official Docker images:

* [elasticsearch](https://github.com/elastic/elasticsearch-docker)
* [logstash](https://github.com/elastic/logstash-docker)
* [kibana](https://github.com/elastic/kibana-docker)

Plus the Kafka Adapter:
* based on the Kafka Client [librdkafka](https://github.com/geeknam/docker-confluent-python) version **0.11.1**
* python kafka module [confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python) version **0.9.1.2**


**Note**: Other branches in this project are available:

* ELK 5 with X-Pack support: https://github.com/deviantony/docker-elk/tree/x-pack
* ELK 5 in Vagrant: https://github.com/deviantony/docker-elk/tree/vagrant
* ELK 5 with Search Guard: https://github.com/deviantony/docker-elk/tree/searchguard


## Requirements

### Host setup

1. Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
3. Clone this repository

## Usage

### Bringing up the stack

Start the ELK stack using `docker-compose`:

```bash
docker-compose build
```

You can also choose to run it in background (detached mode):

```bash
docker-compose up
```

Give Kibana about 2 minutes to initialize, then access the Kibana web UI by hitting
[http://localhost:5601](http://localhost:5601) with a web browser.

By default, the stack exposes the following ports:
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana
* 3000: Kafka-Adapter HTTP
* 8080: Zeppelin Notebook

**WARNING**: If you're using `boot2docker`, you must access it via the `boot2docker` IP address instead of `localhost`.

**WARNING**: If you're using *Docker Toolbox*, you must access it via the `docker-machine` IP address instead of
`localhost`.

The Kafka-Adapter should now automatically fetch data from the kafka message bus on topic **SensorData**. However, the selected topics can be specified in `kafka-adapter/Dockerfile` by setting the environment
variables of logstash. KAFKA_TOPICS should be of the form "topic1,topic2,topic3,..."

To test the ELK Stack itself, inject example log entries via TCP by:

```bash
$ nc localhost 5000 < /path/to/logfile.log
```
After reloading Kibana an index can be created from the test data.



