import asyncio
import math

import aiohttp
from settings import settings

bill_list = []
bill_list_lock = asyncio.Lock()


async def all_congress_bills(congress):
    """Retrieves all bills from provided congress."""

    async with aiohttp.ClientSession(
        headers={"x-api-key": settings.api_key}
    ) as session:
        # Make initial requets to retrieve total number of bills
        data = await send_request(
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
                    send_request(
                        session,
                        f"{settings.url_base}{congress}",
                        offset * settings.url_param_bill_limit,
                        settings.url_param_bill_limit,
                    )
                )


async def send_request(session, url, param_offset, param_limit):
    """Composes request url, sends get, awaits response."""

    full_url = f"{url}?offset={param_offset}&limit={param_limit}"

    async with session.get(full_url) as resp:
        if resp.ok:
            data = await resp.json()
            async with bill_list_lock:
                bill_list.append(data)
                return data
        else:
            # TODO handle error
            print("error")


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(all_congress_bills(settings.url_congress))


if __name__ == "__main__":
    main()
