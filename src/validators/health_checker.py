import asyncio
import time
from datetime import datetime
import aiohttp
from src.models.proxy import Proxy, ProxyStatus

TEST_URL = "http://gstatic.com/generate_204"
TIMEOUT = 5

async def check_proxy(session, proxy):
    start = time.time()
    proxy_url = f"{proxy.protocol.value}://{proxy.address}"
    try:
        async with session.get(TEST_URL, proxy=proxy_url, timeout=aiohttp.ClientTimeout(total=TIMEOUT), ssl=False) as resp:
            proxy.latency = round((time.time() - start) * 1000, 2)
            proxy.status = ProxyStatus.ALIVE if resp.status == 204 else ProxyStatus.DEAD
    except:
        proxy.status = ProxyStatus.DEAD
    proxy.last_check = datetime.now()
    return proxy

async def check_proxies(proxies, max_concurrent=100):
    semaphore = asyncio.Semaphore(max_concurrent)
    async def bounded_check(session, proxy):
        async with semaphore:
            return await check_proxy(session, proxy)
    async with aiohttp.ClientSession() as session:
        tasks = [bounded_check(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)
    return results

async def filter_alive(proxies, max_concurrent=100):
    checked = await check_proxies(proxies, max_concurrent)
    return [p for p in checked if p.status == ProxyStatus.ALIVE]
