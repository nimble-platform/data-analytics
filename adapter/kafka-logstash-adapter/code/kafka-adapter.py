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


__date__ = "28 November 2017"
__version__ = "1.6"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = """This program forwards consumed messages from the kafka bus semantically interpreted by sensorthings 
to the logstash instance of the ELK stack."""


# kafka parameters
# topics and servers should be of the form: "topic1,topic2,..."
KAFKA_TOPICS = "SensorData"
BOOTSTRAP_SERVERS_default = 'il061,il062'
KAFKA_GROUP_ID = "db-adapter"

# logstash parameters
HOST_default = 'logstash'  # important to set
PORT_default = 5000
STATUS_FILE = "status.log"

# Sensorthings parameters
ST_SERVER = "http://il060:8082/v1.0/"

# webservice setup
app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def print_adapter_status():
    """
    This function is called by a sebserver request and prints the current meta information.
    :return:
    """
    try:
        with open(STATUS_FILE) as f:
            adapter_status = json.loads(f.read())
    except FileNotFoundError:
        adapter_status = {"application": "db-adapter",
                          "status": "initialisation"}
    return jsonify(adapter_status)


class KafkaStAdapter:
    def __init__(self, enable_kafka_adapter, enable_sensorthings):
        self.enable_kafka_adapter = enable_kafka_adapter
        self.enable_sensorthings = enable_sensorthings
        if self.enable_sensorthings:
            self.id_mapping = self.full_st_id_map()

    def full_st_id_map(self):
        datastreams = requests.get(ST_SERVER + "Datastreams").json()
        id_mapping = dict()
        id_mapping["@iot.nextLink"] = datastreams["@iot.nextLink"]
        id_mapping["value"] = dict()
        for stream in datastreams["value"]:
            stream_id = str(stream["@iot.id"])
            id_mapping["value"][stream_id] = {"name": stream["name"],
                                              "description": stream["description"]}
        return id_mapping

    def one_st_id_map(self, idn):
        stream = requests.get(ST_SERVER + "Datastreams(" + str(idn) + ")").json()
        stream_id = str(stream["@iot.id"])
        self.id_mapping["value"][stream_id] = {"name": stream["name"],
                                               "description": stream["description"]}

    def stream_kafka(self):
        """
        This function configures a kafka consumer and a logstash logger instance.
        :return
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
        if self.enable_kafka_adapter:
            consumer = Consumer(**conf)
            consumer.subscribe(kafka_topics)
        else:
            consumer = None

        #  use default and init Logstash Handler
        logstash_handler = TCPLogstashHandler(host=HOST_default,
                                              port=PORT_default,
                                              version=1)
        logger.addHandler(logstash_handler)

        # Check if Sensorthings server is reachable
        if self.enable_sensorthings:
            st_reachable = True
        else:
            st_reachable = False

        # Set status and write to shared file
        adapter_status = {
            "application": "db-adapter",
            "doc": __desc__,
            "status": "waiting for Elasticsearch",
            "kafka input": {
                "configuration": conf,
                "subscribed topics": kafka_topics_str,
                "enabled kafka adapter": self.enable_kafka_adapter
            },
            "logstash output": {
                "host": HOST_default,
                "port": PORT_default
            },
            "sensorthings mapping": {
                "enabled sensorthings": self.enable_sensorthings,
                "host": ST_SERVER,
                "reachable": st_reachable
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
        time.sleep(20)

        # ready to stream flag
        adapter_status["status"] = "running"
        with open(STATUS_FILE, "w") as f:
            f.write(json.dumps(adapter_status))
        print("Adapter Status:", str(adapter_status))
        logger.info('Logstash reachable')

        # Kafka 2 Logstash streaming
        if self.enable_kafka_adapter:
            running = True
            try:
                while running:
                    msg = consumer.poll()
                    if not msg.error():
                        data = json.loads(msg.value().decode('utf-8'))
                        if self.enable_sensorthings:
                            data_id = str(data['Datastream']['@iot.id'])
                            if data_id not in list(self.id_mapping['value'].keys()):
                                self.one_st_id_map(data_id)
                            data['Datastream']['name'] = self.id_mapping['value'][data_id]['name']
                            data['Datastream']['URI'] = ST_SERVER + "Datastreams(" + data_id + ")"
                            # print(data['Datastream']['name'])
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
    # Load variables set by docker-compose, enable kafka as data input and sensorthings mapping by default
    enable_kafka_adapter = True
    if os.getenv('enable_kafka_adapter', "true") in ["false", "False", 0]:
        enable_kafka_adapter = False

    enable_sensorthings = True
    if os.getenv('enable_sensorthings', "true") in ["false", "False", 0]:
        enable_sensorthings = False

    # Create an kafka to logstash instance
    adapter_instance = KafkaStAdapter(enable_kafka_adapter, enable_sensorthings)

    # start kafka to logstash streaming in a subprocess
    kafka_streaming = Process(target=adapter_instance.stream_kafka, args=())
    kafka_streaming.start()

    app.run(host="0.0.0.0", debug=False, port=3030)
