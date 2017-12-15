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




## Getting Started

### Local with Docker Compose

For testing purposes we suggest to build the containers locally with `docker-compose`.
The full instructions are provided in `./compose_datastore`.


### Cloud with Docker Swarms

If you already have a docker swarm cluster, all components can be deployed from `./swarm_datastore`.
In the other case, [this instruction](https://www.youtube.com/watch?v=KC4Ad1DS8xU&t=191s)
helps to set up a Swarm from Ubuntu servers.

