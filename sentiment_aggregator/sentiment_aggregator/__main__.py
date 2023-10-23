import json
import logging.config
import pathlib

from kafka import KafkaConsumer
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

from sentiment_aggregator.settings import settings

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger("sentiment-aggregator")

db_driver = GraphDatabase.driver(settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_user_password))

consumer = KafkaConsumer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
)
consumer.subscribe(topics=[settings.kafka_bill_raw_topic, settings.kafka_bill_processed_topic])

def initialize_database() -> None:
    with db_driver.session() as session:
        try:
            session.run("CREATE CONSTRAINT FOR (bill:Bill) REQUIRE (bill.number, bill.type) IS UNIQUE;")
            session.run("CREATE CONSTRAINT FOR (congress:Congress) REQUIRE congress.number IS UNIQUE;")
        except ClientError as e:
            log.error(f"Error on startup, potentially attempted repeated initializations: {e}")

def create_or_update_bill(bill_data: dict) -> None:
    query = """
            MERGE (bill:Bill {number: $bill_data.number, type: $bill_data.type})
            ON CREATE
              SET bill = $bill_data
            ON MATCH
              SET bill += $bill_data;
            """
    with db_driver.session() as session:
        try:
            session.run(query, bill_data=bill_data)
        except ClientError as e:
            log.error(e)

def create_congress(congress_data: dict) -> None:
    query = """
            MERGE (bill:Bill { number: $congress_data.number })
            ON CREATE
              SET bill = $congress_data;
            """
    with db_driver.session() as session:
        try:
            session.run(query, congress_data=congress_data)
        except ClientError as e:
            log.error(e)



def consume_processed_bills() -> None:
    for bill in consumer:
        bills.update(json.loads(bill.value))
        log.info(f"{bills}")

if __name__ == "__main__":
    # consume_processed_bills()
    pass
