import os
import sys
import time
import json
import logging
from multiprocessing import Process
import requests
from flask import Flask, jsonify
from redis import Redis
from logstash import TCPLogstashHandler

# confluent_kafka is based on librdkafka, details in requirements.txt
from confluent_kafka import Consumer, KafkaError


__date__ = "22 November 2017"
__version__ = "1.5"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = "This program forwards consumed messages from the kafka bus to the logstash instance of the ELK stack."


# kafka parameters
# topics and servers should be of the form: "topic1,topic2,..."
KAFKA_TOPICS = "SensorData"
BOOTSTRAP_SERVERS_default = 'il061,il062'
KAFKA_GROUP_ID = "db-adapter"

# logstash parameters
HOST_default = 'logstash'
PORT_default = 5000
STATUS_FILE = "status.log"

# webservice setup
app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def print_adapter_status():
    """
    This function is called by a sebserver request and prints the current meta information.
    :return:
    """
    adapter_status = {"application": "db-adapter"}
    try:
        with open(STATUS_FILE) as f:
            adapter_status = json.loads(f.read())
    except FileNotFoundError:
        adapter_status = {"application": "db-adapter",
                          "status": "initialisation"}
    return jsonify(adapter_status)


def stream_kafka(enable_kafka_adapter):
    """
    This function configures a kafka consumer and a logstash logger instance and forwards consumed kafka messages
    to the ELK's logstash instance via TCP.
    :return:
    """

    # Init kafka consumer
    kafka_topics_str = os.getenv('KAFKA_TOPICS', KAFKA_TOPICS)
    kafka_topics = [topic.strip() for topic in kafka_topics_str.split(",") if len(topic) > 0]
    kafka_group_id = os.getenv('KAFKA_GROUP_ID', KAFKA_GROUP_ID)
    print(kafka_topics)

    # Init logstash logging
    logging.basicConfig(level='WARNING')
    logger = logging.getLogger(str(kafka_topics))
    logger.setLevel(logging.INFO)

    # get bootstrap_servers from environment variable or use defaults and configure Consumer
    bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS', BOOTSTRAP_SERVERS_default)
    conf = {'bootstrap.servers': bootstrap_servers, 'group.id': kafka_group_id,
            'session.timeout.ms': 6000,
            'default.topic.config': {'auto.offset.reset': 'smallest'}}

    # Create Consumer if allowed:
    if enable_kafka_adapter:
        consumer = Consumer(**conf)
        consumer.subscribe(kafka_topics)

    #  use default and init Logstash Handler
    logstash_handler = TCPLogstashHandler(host=HOST_default,
                                          port=PORT_default,
                                          version=1)
    logger.addHandler(logstash_handler)

    # Set status and write to shared file
    adapter_status = {
        "application": "db-adapter",
        "doc": __desc__,
        "status": "waiting for Elasticsearch",
        "kafka input": {
            "configuration": conf,
            "subscribed topics": kafka_topics_str,
            "enabled kafka adapter": enable_kafka_adapter
        },
        "logstash output": {
            "host": HOST_default,
            "port": PORT_default
        },
        "version": {
            "number": __version__,
            "build_date": __date__,
            "repository": "https://github.com/nimble-platform/data-analytics"
        }
    }
    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(adapter_status))

    # time for logstash init
    elastic_reachable = False
    while not elastic_reachable:
        try:
            # use localhost if running local
            r = requests.get("http://elasticsearch:9200")
            status_code = r.status_code
            if status_code in [200]:
                elastic_reachable = True
        except:
            continue
        finally:
            time.sleep(1)

    # Elasticsearch ready
    adapter_status["status"] = "waiting for Logstash"
    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(adapter_status))
    print("Adapter Status:", str(adapter_status))
    logger.info('Elasticsearch reachable')

    # Wait for Logstash
    time.sleep(40)

    # ready to stream flag
    adapter_status["status"] = "running"
    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(adapter_status))
    print("Adapter Status:", str(adapter_status))
    logger.info('Logstash reachable')

    # Kafka 2 Logstash streaming
    if enable_kafka_adapter:
        running = True
        try:
            while running:
                msg = consumer.poll()
                if not msg.error():
                    data = json.loads(msg.value().decode('utf-8'))
                    logger.info('', extra=data)
                elif msg.error().code() != KafkaError._PARTITION_EOF:
                    print(msg.error())
                    logger.warning('Exception in Kafka-Logstash Streaming', extra=str(msg))
                time.sleep(0)

        except Exception as error:
            logger.error("Error in Kafka-Logstash Streaming: {}".format(error))
            adapter_status["status"] = "error"
            logger.warning(adapter_status)
            with open(STATUS_FILE, "w") as f:
                f.write(json.dumps(adapter_status))
        finally:
            consumer.close()


if __name__ == '__main__':
    # Load variable set by docker-compose, enable kafka by default
    enable_kafka_adapter = True
    if os.getenv('enable_kafka_adapter', "true") in ["false", "False", 0]:
        enable_kafka_adapter = False

    # start kafka to logstash streaming in a subprocess
    kafka_streaming = Process(target=stream_kafka, args=(enable_kafka_adapter,))
    kafka_streaming.start()

    app.run(host="0.0.0.0", debug=False, port=3030)
