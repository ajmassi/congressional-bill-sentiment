import asyncio
import json
import logging.config
import math
import pathlib

import aiohttp
from kafka import KafkaProducer
from settings import settings

config_directory = pathlib.Path(__file__).parent.resolve()
with open(config_directory.joinpath("logger.conf")) as logger_conf:
    logging.config.dictConfig(json.load(logger_conf))

log = logging.getLogger(__name__)


producer = KafkaProducer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def flatten_dict(dd, separator="_", prefix=""):
    return (
        {
            prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
        }
        if isinstance(dd, dict)
        else {prefix: dd}
    )


async def process_bill_list(bills):
    """Split retrieved bills and push to kafka topic."""
    for bill in bills:
        producer.send(settings.kafka_bill_raw_topic, flatten_dict(bill))


async def congress_api_bill_processing(session, url, param_offset, param_limit):
    """Composes request url, sends get, pushes bills to kafka."""

    full_url = f"{url}?offset={param_offset}&limit={param_limit}"

    async with session.get(full_url) as resp:
        if resp.ok:
            data = await resp.json()
            await process_bill_list(data.get("bills"))
            log.info(f"Received successful response from {full_url!r}")
            return data
        else:
            log.error(f"URL {resp.url!r} resulted in error: {resp.reason}")


async def partition_bills(congress):
    """Partition given Congress' bills; initiate retrieval and processing."""

    async with aiohttp.ClientSession(
        headers={"x-api-key": settings.api_key}
    ) as session:
        # Make initial requets to retrieve total number of bills
        data = await congress_api_bill_processing(
            session, f"{settings.url_base}{congress}", 0, settings.url_param_bill_limit
        )

        if not data:
            return

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
    log.info("Bill Retrieval Complete")
    producer.close()
