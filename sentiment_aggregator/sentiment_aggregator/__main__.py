import json
import logging.config
import pathlib

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from neo4j import GraphDatabase, Record
from neo4j.exceptions import ClientError
from settings import settings

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger("sentiment-aggregator")

db_driver = GraphDatabase.driver(
    settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_user_password)
)

consumer = KafkaConsumer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_deserializer=lambda v: json.loads(v),
)
consumer.subscribe(topics=["bill.raw", "bill.processed"])


def initialize_database() -> None:
    """ Set initial conditions for Labels including required/unique fields """
    with db_driver.session() as session:
        try:
            session.run(
                "CREATE CONSTRAINT FOR (bill:Bill) REQUIRE (bill.number, bill.type) IS UNIQUE;"
            )
            session.run(
                "CREATE CONSTRAINT FOR (congress:Congress) REQUIRE congress.number IS UNIQUE;"
            )
        except ClientError as e:
            log.error(
                f"Error on startup, potentially attempted repeated initializations: {e}"
            )


def create_or_update_node_bill(bill_data: dict) -> Record:
    """ Create a new Bill node or update existing node as appropriate. """
    def managed_tx(tx, bill_data: dict) -> Record:
        query = """
                MERGE (bill:Bill {number: $bill_data.number, type: $bill_data.type})
                ON CREATE
                  SET bill = $bill_data
                ON MATCH
                  SET bill += $bill_data
                RETURN bill;
                """
        result = tx.run(query, bill_data=bill_data)
        record = result.single()
        return record

    with db_driver.session() as session:
        try:
            record = session.execute_write(managed_tx, bill_data)
            return record
        except ClientError as e:
            log.error(e)


def create_node_congress(congress_data: dict) -> Record:
    """ Create a new Congress node. """
    def managed_tx(tx, congress_data: dict) -> Record:
        query = """
                MERGE (congress:Congress {number: $congress_data.number})
                ON CREATE
                  SET congress = $congress_data
                RETURN congress;
                """
        result = tx.run(query, congress_data=congress_data)
        record = result.single()
        return record

    with db_driver.session() as session:
        try:
            record = session.execute_write(managed_tx, congress_data)
            return record
        except ClientError as e:
            log.error(e)


def create_relationship_congress_bill(congress_data: dict, bill_data: dict) -> Record:
    """ Create relationship between a Congress node and a Bill node. """
    def managed_tx(tx, congress_data: dict, bill_data: dict) -> Record:
        query = """
                MATCH (congress:Congress), (bill:Bill)
                WHERE congress.number = $congress_data.number AND
                      bill.number = $bill_data.number AND
                      bill.type = $bill_data.type
                CREATE (congress)-[:PASSED]->(bill)
                RETURN congress, bill;
                """
        result = tx.run(query, congress_data=congress_data, bill_data=bill_data)
        record = result.single()
        return record

    with db_driver.session() as session:
        try:
            record = session.execute_write(managed_tx, congress_data, bill_data)
            return record
        except ClientError as e:
            log.error(e)


def handle_bill_raw(bill_record: ConsumerRecord) -> None:
    """ Process messages from the bill.raw topic """
    bill = bill_record.value
    _bill = create_or_update_node_bill(bill)
    _congress = create_node_congress({"number": bill.get("congress")})
    _relationship = create_relationship_congress_bill(
        {"number": bill.get("congress")}, bill
    )
    log.info(f"PROCESSED {_bill} {_congress} {_relationship}")


def handle_bill_processed(bill_record: ConsumerRecord) -> None:
    """ Process messages from the bill.processed topic """
    bill = bill_record.value
    _bill = create_or_update_node_bill(bill)
    log.info(f"PROCESSED {_bill}")


TOPIC_HANDLER_MAPPING = {
    settings.kafka_bill_raw_topic: handle_bill_raw,
    settings.kafka_bill_processed_topic: handle_bill_processed,
}


def consume_bills() -> None:
    """ Read messages from subscribed Kafka topic(s) and call appropriate handling function. """
    for bill_record in consumer:
        log.info(f"Processing {bill_record.topic}: {bill_record.value}")
        try:
            TOPIC_HANDLER_MAPPING.get(bill_record.topic)(bill_record)
        except TypeError:
            log.critical(f"Unexpected topic message received: {bill_record}")


if __name__ == "__main__":
    consume_bills()
    pass
