import asyncio
import json
import math

import aiohttp
from kafka import KafkaProducer
from settings import settings

producer = KafkaProducer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


async def process_bill_list(bills):
    """Split retrieved bills and push to kafka topic."""
    for bill in bills:
        producer.send(settings.kafka_bill_raw_topic, bill)


async def congress_api_bill_processing(session, url, param_offset, param_limit):
    """Composes request url, sends get, pushes bills to kafka."""

    full_url = f"{url}?offset={param_offset}&limit={param_limit}"

    async with session.get(full_url) as resp:
        if resp.ok:
            data = await resp.json()
            await process_bill_list(data.get("bills"))
            return data
        else:
            # TODO handle error
            print("error")


async def partition_bills(congress):
    """Partition given Congress' bills; initiate retrieval and processing."""

    async with aiohttp.ClientSession(
        headers={"x-api-key": settings.api_key}
    ) as session:
        # Make initial requets to retrieve total number of bills
        data = await congress_api_bill_processing(
            session, f"{settings.url_base}{congress}", 0, settings.url_param_bill_limit
        )

        # Determine how many requests will be needed to retreive all bills
        remaining_reqs = math.floor(
            data.get("pagination").get("count") / settings.url_param_bill_limit
        )

        # Make parallel requests to endpoint for each partition of bills
        async with asyncio.TaskGroup() as tg:
            for offset in range(1, remaining_reqs + 1):
                tg.create_task(
                    congress_api_bill_processing(
                        session,
                        f"{settings.url_base}{congress}",
                        offset * settings.url_param_bill_limit,
                        settings.url_param_bill_limit,
                    )
                )


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(partition_bills(settings.url_congress))


if __name__ == "__main__":
    main()
    producer.close()
