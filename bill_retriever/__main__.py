# import requests
from settings import settings
import asyncio
import aiohttp
import time

bill_list = []
bill_list_lock = asyncio.Lock()

# data = session.get(f"https://api.congress.gov/v3/bill/{settings.url_param_congress}")
# print(data.json())

async def ex_single_threaded(request_limit):
    async with aiohttp.ClientSession(headers={"x-api-key": settings.api_key}) as session:
        for i in range(request_limit):
            await send_request(session, f"{settings.url_base}asdf{settings.url_congress}?offset={10+i}&limit={settings.url_param_bill_limit}")

async def ex_asyncio(request_limit):
    async with aiohttp.ClientSession(headers={"x-api-key": settings.api_key}) as session:
        async with asyncio.TaskGroup() as tg: 
            for i in range(request_limit):
                tg.create_task(send_request(session, f"{settings.url_base}{settings.url_congress}?offset={20+i}&limit={settings.url_param_bill_limit}"))

async def send_request(session, url):
    async with session.get(url) as resp:
        if resp.ok:
            data = await resp.json()
            async with bill_list_lock:
                bill_list.append(data)
        else:
            # TODO handle error
            print("error")

def main():
    loop = asyncio.get_event_loop()
    request_limit = 1
    t_start = time.time()
    # asyncio.run(ex_single_threaded(request_limit))
    loop.run_until_complete(ex_asyncio(request_limit))

    print(bill_list)
    t_stop = time.time()

    print(f"Wall Time: {t_stop-t_start}")

if __name__ == "__main__":
    main()
