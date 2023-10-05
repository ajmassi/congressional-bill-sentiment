import json
import logging.config
import pathlib

from kafka import KafkaConsumer
from settings import settings

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger("sentiment-aggregator")

bills = {}

consumer = KafkaConsumer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
)
consumer.subscribe(topics=[settings.kafka_bill_raw_topic, settings.kafka_bill_processed_topic])

def consume_processed_bills() -> None:
    for bill in consumer:
        bills.update(json.loads(bill.value))
        log.info(f"{bills}")

if __name__ == "__main__":
    consume_processed_bills()
