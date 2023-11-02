import json
import logging.config
import pathlib
import asyncio

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from neo4j import AsyncGraphDatabase, Record
from neo4j.exceptions import ClientError
from settings import settings

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger("sentiment-aggregator")

db_driver = AsyncGraphDatabase.driver(
    settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_user_password)
)

consumer = KafkaConsumer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_deserializer=lambda v: json.loads(v),
)
consumer.subscribe(topics=["bill.raw", "bill.processed"])


async def initialize_database() -> None:
    """ Set initial conditions for Labels including required/unique fields """
    async with db_driver.session() as session:
        try:
            await session.run(
                "CREATE CONSTRAINT FOR (bill:Bill) REQUIRE (bill.number, bill.type) IS UNIQUE;"
            )
            await session.run(
                "CREATE CONSTRAINT FOR (congress:Congress) REQUIRE congress.number IS UNIQUE;"
            )
        except ClientError as e:
            log.error(
                f"Error on startup, potentially attempted repeated initializations: {e}"
            )


async def create_or_update_node_bill(bill_data: dict) -> Record:
    """ Create a new Bill node or update existing node as appropriate. """
    async def managed_tx(tx, bill_data: dict) -> Record:
        query = """
                MERGE (bill:Bill {number: $bill_data.number, type: $bill_data.type})
                ON CREATE
                  SET bill = $bill_data
                ON MATCH
                  SET bill += $bill_data
                RETURN bill;
                """
        result = await tx.run(query, bill_data=bill_data)
        record = await result.single()
        return record

    async with db_driver.session() as session:
        try:
            record = await session.execute_write(managed_tx, bill_data)
            return record
        except ClientError as e:
            log.error(e)


async def create_node_congress(congress_data: dict) -> Record:
    """ Create a new Congress node. """
    async def managed_tx(tx, congress_data: dict) -> Record:
        query = """
                MERGE (congress:Congress {number: $congress_data.number})
                ON CREATE
                  SET congress = $congress_data
                RETURN congress;
                """
        result = await tx.run(query, congress_data=congress_data)
        record = await result.single()
        return record

    async with db_driver.session() as session:
        try:
            record = await session.execute_write(managed_tx, congress_data)
            return record
        except ClientError as e:
            log.error(e)


async def create_relationship_congress_bill(congress_data: dict, bill_data: dict) -> Record:
    """ Create relationship between a Congress node and a Bill node. """
    async def managed_tx(tx, congress_data: dict, bill_data: dict) -> Record:
        query = """
                MATCH (congress:Congress), (bill:Bill)
                WHERE congress.number = $congress_data.number AND
                      bill.number = $bill_data.number AND
                      bill.type = $bill_data.type
                CREATE (congress)-[:PASSED]->(bill)
                RETURN congress, bill;
                """
        result = await tx.run(query, congress_data=congress_data, bill_data=bill_data)
        record = await result.single()
        return record

    async with db_driver.session() as session:
        try:
            record = await session.execute_write(managed_tx, congress_data, bill_data)
            return record
        except ClientError as e:
            log.error(e)


async def handle_bill_raw(bill_record: ConsumerRecord) -> None:
    """ Process messages from the bill.raw topic """
    bill = bill_record.value
    _bill = await create_or_update_node_bill(bill)
    _congress = await create_node_congress({"number": bill.get("congress")})
    _relationship = await create_relationship_congress_bill(
        {"number": bill.get("congress")}, bill
    )
    log.info(f"PROCESSED {_bill} {_congress} {_relationship}")


async def handle_bill_processed(bill_record: ConsumerRecord) -> None:
    """ Process messages from the bill.processed topic """
    bill = bill_record.value
    _bill = await create_or_update_node_bill(bill)
    log.info(f"PROCESSED {_bill}")


TOPIC_HANDLER_MAPPING = {
    settings.kafka_bill_raw_topic: handle_bill_raw,
    settings.kafka_bill_processed_topic: handle_bill_processed,
}


async def consume_bills() -> None:
    """ Read messages from subscribed Kafka topic(s) and call appropriate handling function. """
    for bill_record in consumer:
        log.info(f"Processing {bill_record.topic}: {bill_record.value}")
        try:
            await TOPIC_HANDLER_MAPPING.get(bill_record.topic)(bill_record)
        except TypeError as e:
            log.critical(f"Unexpected topic message received: {bill_record}")


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_bills())
    loop.close()


if __name__ == "__main__":
    main()
