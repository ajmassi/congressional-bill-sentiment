import asyncio
import json
from abc import ABC, abstractmethod

from kafka import KafkaConsumer, KafkaProducer
from settings import settings


class SentimentAnalyzer(ABC):
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.kafka_bill_raw_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
        )
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def produce_processed_bill(self, raw_bill: dict, sentiment: dict) -> dict:
        processed_bill = dict(raw_bill, **sentiment)
        self.producer.send(settings.kafka_bill_processed_topic, processed_bill)

    @abstractmethod
    async def calculate_sentiment(self, raw_bill: dict) -> dict:
        """"""

    async def consume_raw_bills(self) -> None:
        for bill in self.consumer:
            raw_bill = json.loads(bill.value)
            sentiment = await self.calculate_sentiment(raw_bill)
            await self.produce_processed_bill(raw_bill, sentiment)

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.consume_raw_bills())
