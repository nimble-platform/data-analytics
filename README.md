# Data Analytics Stack with


The ELK stack was adapted from [deviantony](https://github.com/deviantony/docker-elk)'s ELK-Stack version: 
[![Elastic Stack version](https://img.shields.io/badge/ELK-5.6.3-blue.svg?style=flat)](https://github.com/deviantony/docker-elk/issues/182).

Run the latest version of the ELK (Elasticsearch, Logstash, Kibana) stack with Docker and Docker Compose.

It will give you the ability to analyse data on the kafka message bus by using the searching/aggregation capabilities of Elasticsearch
and the visualization power of Kibana.

Based on the official Docker images:
* [elasticsearch](https://github.com/elastic/elasticsearch-docker)
* [logstash](https://github.com/elastic/logstash-docker)
* [kibana](https://github.com/elastic/kibana-docker)

Plus the Kafka Adapter based on the components:
* Kafka Client [librdkafka](https://github.com/geeknam/docker-confluent-python) version **0.11.1**
* python kafka module [confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python) version **0.9.1.2**


**Note**: Other branches of the forged project are available:
* ELK 5 with X-Pack support: https://github.com/deviantony/docker-elk/tree/x-pack
* ELK 5 in Vagrant: https://github.com/deviantony/docker-elk/tree/vagrant
* ELK 5 with Search Guard: https://github.com/deviantony/docker-elk/tree/searchguard


## Contents

1. [Requirements](#requirements)
   * [Host setup](#host-setup)
   * [SELinux](#selinux)
2. [Getting started](#getting-started)
   * [Bringing up the stack](#bringing-up-the-stack)
   * [Initial setup](#initial-setup)
3. [Configuration](#configuration)
   * [How can I tune the Kibana configuration?](#how-can-i-tune-the-kibana-configuration)
   * [How can I tune the Logstash configuration?](#how-can-i-tune-the-logstash-configuration)
   * [How can I tune the Elasticsearch configuration?](#how-can-i-tune-the-elasticsearch-configuration)
   * [How can I scale out the Elasticsearch cluster?](#how-can-i-scale-up-the-elasticsearch-cluster)
4. [Storage](#storage)
   * [How can I persist Elasticsearch data?](#how-can-i-persist-elasticsearch-data)
5. [Extensibility](#extensibility)
   * [How can I add plugins?](#how-can-i-add-plugins)
   * [How can I enable the provided extensions?](#how-can-i-enable-the-provided-extensions)
6. [JVM tuning](#jvm-tuning)
   * [How can I specify the amount of memory used by a service?](#how-can-i-specify-the-amount-of-memory-used-by-a-service)
   * [How can I enable a remote JMX connection to a service?](#how-can-i-enable-a-remote-jmx-connection-to-a-service)
7. [Trouble-Shooting](#Trouble-shooting)

## Requirements

### Host setup

1. Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
3. Clone this repository
4. Set permissions to make the content writable by the user


### SELinux

On distributions which have SELinux enabled out-of-the-box you will need to either re-context the files or set SELinux
into Permissive mode in order for docker-elk to start properly. For example on Redhat and CentOS, the following will
apply the proper context:

```bash
$ chcon -R system_u:object_r:admin_home_t:s0 docker-elk/
```

## Usage

### Bringing up the stack

Before running in a deployed mode, it is recommended change the the mounted data-directory in `docker-compose.yml` to a directory outside this folder to the Elasticsearch/data, because this git-repo should remain static and lightweigthed. See [here](#how-can-i-persist-elasticsearch-data) for more infos on how to persist data.


Start the ELK stack using `docker-compose`:

```bash
cd elk
docker-compose up --build -d

cd ../kafka-logstash-adapter
docker-compose up --build -d

cd ../zeppelin
docker-compose up --build -d

```

The flag `-d` stands for running it in background (detached mode):

Watch the logs with:

```bash
docker-compose logs -f
```


Give Kibana about 2 minutes to initialize, then access the Kibana web UI by hitting
[http://localhost:5601](http://localhost:5601) with a web browser.
tra
By default, the stack exposes the following ports:
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana
* 3030: Kafka-ELK HTTP
* 8080: Zeppelin GUI

**WARNING**: If you're using `boot2docker`, you must access it via the `boot2docker` IP address instead of `localhost`.

**WARNING**: If you're using *Docker Toolbox*, you must access it via the `docker-machine` IP address instead of
`localhost`.

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

The data stored in Elasticsearch will be persisted due to the following volume mountage:

In order to persist Elasticsearch data even after removing the Elasticsearch container, you'll have to mount a volume on
your Docker host. Update the `elasticsearch` service declaration to:

```yml
elasticsearch:

  volumes:
    - /path/to/storage:/usr/share/elasticsearch/data
```

This will store Elasticsearch data inside `/path/to/storage`.

**NOTE:** beware of these OS-specific considerations:
* **Linux:** the [unprivileged `elasticsearch` user][esuser] is used within the Elasticsearch image, therefore the mounted data directory must be owned by the uid `1000`.

Alternatively, setting the permissions of the directory `/path/to/storage` to the user is an easy workaround.

```sudo chown -R USER:USER /path/to/storage```


* **macOS:** the default Docker for Mac configuration allows mounting files from `/Users/`, `/Volumes/`, `/private/`,
  and `/tmp` exclusively. Follow the instructions from the [documentation][macmounts] to add more locations.

[esuser]: https://github.com/elastic/elasticsearch-docker/blob/016bcc9db1dd97ecd0ff60c1290e7fa9142f8ddd/templates/Dockerfile.j2#L22
[macmounts]: https://docs.docker.com/docker-for-mac/osxfs/


For demonstration purposes, example data is shared in the default`data`.




## trouble-shooting

### Can't apt-get update in Dockerfile:

Restart the service

```sudo service docker restart```

or add the file `/etc/docker/daemon.json` with the content:
```
{
    "dns": [your_dns, "8.8.8.8"]
}
```
where `your_dns` can be found with the command:

```bash
nmcli device show <interfacename> | grep IP4.DNS
```

### Traceback of non zero code 4 or 128:

Restart service with
```sudo service docker restart```

or add your dns address as described above


### Elasticsearch crashes instantly:

Check permission of `data-analytics` and **datasink**-directory:

```bash
sudo chown -r USER:USER .
sudo chmod -R 777 .
```

In case this doesn't help, you may have to remove redundant docker installations or reinstall it



### Error starting userland proxy: listen tcp 0.0.0.0:3030: bind: address already in use

Bring down other services, or change the hosts port number in docker-compose.yml. 

Find all running services by:
```bash
sudo docker ps
```


### errors while removing docker containers:

Remove redundant docker installations


### "entire heap max virtual memory areas vm.max_map_count [...] likely too low, increase to at least [262144]"
    
Run on host machine:

```bash
sudo sysctl -w vm.max_map_count=262144
```

### Redis warning: vm.overcommit_memory
Run on host:
```
sysctl vm.overcommit_memory=1

```

### Redis warning: "WARNING you have Transparent Huge Pages (THP) support enabled in your kernel."

Just ignore this





