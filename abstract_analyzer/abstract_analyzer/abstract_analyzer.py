import asyncio
import json
import logging
from abc import ABC, abstractmethod

from kafka import KafkaConsumer, KafkaProducer

from abstract_analyzer.settings import settings

log = logging.getLogger("abstract_analyzer")


class SentimentAnalyzer(ABC):
    """
    Abstract class to provide skeleton for various sentiment analyzers.
    Subclasses need to only define "calculate_sentiment()".
    Calling functions can use "start()" if synchronous or call "process_bills()"
        directly if asynchronous.
    """

    def __init__(self, consumer_group_id: str):
        self.consumer = KafkaConsumer(
            settings.kafka_bill_raw_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=consumer_group_id,
        )
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def produce_processed_bill(self, raw_bill: dict, sentiment: dict) -> dict:
        """Combine the original bill with sentiment and forward on Kafka topic."""
        processed_bill = {
            "congress": raw_bill.get("congress"),
            "number": raw_bill.get("number"),
            **sentiment,
        }
        log.debug(
            f"Producing on {settings.kafka_bill_processed_topic}: {processed_bill}"
        )
        self.producer.send(settings.kafka_bill_processed_topic, processed_bill)

    @abstractmethod
    async def calculate_sentiment(self, raw_bill: dict) -> dict:
        """"""

    async def process_bills(self) -> None:
        """
        Coordinates processing of bills starting with reading messages from Kafka topic,
            forwarding to sentiment analyzer, and then handing sentiment data to
            Kafka producer.
        """
        for bill in self.consumer:
            raw_bill = json.loads(bill.value)
            sentiment = await self.calculate_sentiment(raw_bill)
            await self.produce_processed_bill(raw_bill, sentiment)

    def start(self) -> None:
        """Run the analyzer from a synchronous calling function."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_bills())
