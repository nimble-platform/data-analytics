import os
import sys
import time
import json
import logging
from multiprocessing import Process
from flask import Flask
from redis import Redis

# pip install python-logstash
from logstash import TCPLogstashHandler
# curl -L https://github.com/edenhill/librdkafka/archive/v0.9.2-RC1.tar.gz | tar xzf -
# cd librdkafka-0.9.2-RC1/
# ./configure --prefix=/usr
# make -j
# sudo make install
# pip install confluent-kafka
from confluent_kafka import Consumer, KafkaError

__date__ = "20 Juli 2017"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
# 2 Sending multiple topics

# topics should be of the form: "topic1,topic2,..."
KAFKA_TOPICS = "SensorData"
bootstrap_servers = 'il061,il062'
group_id = "db-adapter"
conf = {'bootstrap.servers': 'il061,il062', 'group.id': group_id,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}}


host = 'logstash'
STATUS_FILE = "status.log"
STATUS = {"application": "db-adapter",
          "status": "loading"}
with open(STATUS_FILE, "w") as f:
    f.write(json.dumps(STATUS))

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def db_adapter_status():
    try:
        with open(STATUS_FILE) as f:
            STATUS = json.loads(f.read())
    except FileNotFoundError:
        STATUS = {"application": "db-adapter",
                  "status": "initial"}
    return json.dumps(STATUS)



def stream_kafka():
    logging.basicConfig(level='WARNING')
    kafka_topics = os.getenv('KAFKA_TOPICS', KAFKA_TOPICS)
    kafka_topics = [topic.strip() for topic in kafka_topics.split(",") if len(topic) > 0]

    # setup logging
    logger = logging.getLogger(str(kafka_topics))
    logger.setLevel(logging.INFO)
    logstash_handler = TCPLogstashHandler(host=os.getenv('LOGSTASH_HOST', host),
                                          port=int(os.getenv('LOGSTASH_PORT', 5000)),
                                          version=1)

    logger.addHandler(logstash_handler)

    consumer = Consumer(**conf)
    consumer.subscribe(kafka_topics)
    logger.info('Checking topics: {}'.format(str(kafka_topics)))

    running = True
    STATUS["status"] = "running"
    with open(STATUS_FILE, "w") as f:
        f.write(json.dumps(STATUS))

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
        STATUS["status"] = "error"
        with open(STATUS_FILE, "w") as f:
            f.write(json.dumps(STATUS))
    finally:
        consumer.close()


if __name__ == '__main__':
    # start kafka 2 logstash streaming in a subprocess
    kafka_streaming = Process(target=stream_kafka, args=())
    kafka_streaming.start()

    app.run(host="0.0.0.0", debug=True, port=3000)
