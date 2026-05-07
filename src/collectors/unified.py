import re
import time
import asyncio
import aiohttp
from src.sources.registry import ALL_SOURCES
from src.models.proxy import Proxy, Protocol

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REGEX_IP_PORT = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b')

def parse_proxy(line: str):
    line = line.strip()
    if not line or ":" not in line or line.startswith("#"):
        return None
    match = REGEX_IP_PORT.match(line)
    if match:
        ip, port = line.split(":")
        return Proxy(ip=ip, port=int(port))
    return None

async def fetch_source(session, url):
    proxies = []
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                text = await resp.text()
                for line in text.splitlines():
                    proxy = parse_proxy(line)
                    if proxy:
                        proxies.append(proxy)
    except:
        pass
    return proxies

async def collect_all():
    all_proxies = set()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in ALL_SOURCES]
        results = await asyncio.gather(*tasks)
        for proxies in results:
            all_proxies.update(proxies)
    return list(all_proxies)

if __name__ == "__main__":
    print(f"[+] Coletando de {len(ALL_SOURCES)} fontes...")
    start = time.time()
    proxies = asyncio.run(collect_all())
    print(f"[✓] {len(proxies)} proxies coletados em {time.time() - start:.2f}s")
