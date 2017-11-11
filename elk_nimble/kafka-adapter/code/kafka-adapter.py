import os
import sys
import time
import json
import logging
from multiprocessing import Process
from flask import Flask, jsonify
from redis import Redis
from logstash import TCPLogstashHandler

# confluent_kafka is based on librdkafka, details in requirements.txt
from confluent_kafka import Consumer, KafkaError


__date__ = "10 November 2017"
__version__ = "1.2"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = "This program forwards consumed messages from the kafka bus to the logstash instance of the ELK stack."

# kafka parameters
# topics and servers should be of the form: "topic1,topic2,..."
KAFKA_TOPICS = "SensorData"
BOOTSTRAP_SERVERS_default = 'il061,il062'
GROUP_ID = "db-adapter"


# logstash parameters
HOST_default = 'logstash'
PORT_default = 5000
STATUS_FILE = "status.log"

# webservice setup
app = Flask(__name__)
redis = Redis(host='redis', port=6379)


def init_adapter():
    """
    This functions sets up a kafka consumer for incoming messages and a logstash handler wrapped into a logger
    instance. Finally, meta information is gathered and stored into the variable adapter_status.
    :return: adapter_status, consumer, logger
    """

    # Init kafka consumer
    kafka_topics_str = os.getenv('KAFKA_TOPICS', KAFKA_TOPICS)
    kafka_topics = [topic.strip() for topic in kafka_topics_str.split(",") if len(topic) > 0]

    # Init logstash logging
    logging.basicConfig(level='WARNING')
    logger = logging.getLogger(str(kafka_topics))
    logger.setLevel(logging.INFO)

    # get environment variable or use defaultS
    host = os.getenv('LOGSTASH_HOST', HOST_default)
    port = int(os.getenv('LOGSTASH_PORT', PORT_default))

    # get bootstrap_servers from environment variable or use defaults
    bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS', BOOTSTRAP_SERVERS_default)
    conf = {'bootstrap.servers': bootstrap_servers, 'group.id': GROUP_ID,
            'session.timeout.ms': 6000,
            'default.topic.config': {'auto.offset.reset': 'smallest'}}
    consumer = Consumer(**conf)
    consumer.subscribe(kafka_topics)

    logstash_handler = TCPLogstashHandler(host=host,
                                          port=port,
                                          version=1)

    logger.addHandler(logstash_handler)
    logger.info('Checking topics: {}'.format(str(kafka_topics)))

    adapter_status = {
        "application": "db-adapter",
        "doc": __desc__,
        "status": "loading",
        "kafka input": {
            "configuration": conf,
            "subscribed topics": kafka_topics_str
        },
        "logstash output": {
            "host": host,
            "port": port
        },
        "version": {
            "number": __version__,
            "build_date": __date__
        }
    }

    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(adapter_status))

    return adapter_status, consumer, logger


@app.route('/')
def db_adapter_status():
    """
    This function is called by a sebserver request and prints the current meta information.
    :return:
    """
    try:
        with open(STATUS_FILE) as f:
            STATUS = json.loads(f.read())
    except FileNotFoundError:
        STATUS = {"application": "db-adapter",
                  "status": "initial"}
    return jsonify(STATUS)


def stream_kafka(adapter_status, consumer, logger):
    """
    This function forwards consumed kafka messages to the ELK's logstash instance via TCP.
    :param adapter_status: meta information of this program.
    :param consumer: the kafka client's consumer instance
    :param logger: logging instance with inherent logstash handler
    :return:
    """
    time.sleep(30)  # wait 30 seconds for logstash init
    running = True
    adapter_status["status"] = "running"
    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(adapter_status))

    try:
        while running:
            msg = consumer.poll()
            if not msg.error():
                data = json.loads(msg.value().decode('utf-8'))
                logger.info('', extra=data)
            elif msg.error().code() != KafkaError._PARTITION_EOF:
                print(msg.error())
                # running = False
            time.sleep(0)
    except:
        adapter_status["status"] = "error"
        with open(STATUS_FILE, "w") as f:
            f.write(json.dumps(adapter_status))
    finally:
        consumer.close()


if __name__ == '__main__':
    adapter_status, consumer, logger = init_adapter()

    # start kafka to logstash streaming in a subprocess
    kafka_streaming = Process(target=stream_kafka, args=(adapter_status, consumer, logger,))
    kafka_streaming.start()

    app.run(host="0.0.0.0", debug=True, port=3000)
