import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.collectors.unified import collect_all
from src.validators.health_checker import check_proxies
from src.models.proxy import Proxy, ProxyStatus

PROXIES_VIVOS = []
scheduler = AsyncIOScheduler()

async def coletar_e_validar():
    global PROXIES_VIVOS
    print("[*] Coletando proxies...")
    proxies = await collect_all()
    print(f"[*] {len(proxies)} coletados, validando...")
    vivos = await check_proxies(proxies, max_concurrent=100)
    PROXIES_VIVOS = [p for p in vivos if p.status == ProxyStatus.ALIVE]
    print(f"[✓] {len(PROXIES_VIVOS)} proxies vivos")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await coletar_e_validar()
    scheduler.add_job(coletar_e_validar, 'interval', minutes=20)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Proxy Aggregator API", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="api/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("api/templates/dashboard.html", "r") as f:
        return f.read()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/proxies")
async def get_proxies(protocol: str = None, limit: int = 100):
    proxies = PROXIES_VIVOS
    if protocol:
        proxies = [p for p in proxies if p.protocol.value == protocol]
    proxies = proxies[:limit]
    return {"total": len(proxies), "proxies": [{"ip": p.ip, "port": p.port, "protocol": p.protocol.value, "latency": p.latency} for p in proxies]}

@app.get("/api/v1/proxies/random")
async def get_random_proxy(protocol: str = None):
    import random
    proxies = PROXIES_VIVOS
    if protocol:
        proxies = [p for p in proxies if p.protocol.value == protocol]
    if not proxies:
        return {"error": "No proxies available"}
    p = random.choice(proxies)
    return {"ip": p.ip, "port": p.port, "protocol": p.protocol.value, "latency": p.latency}

@app.get("/api/v1/stats")
async def get_stats():
    total = len(PROXIES_VIVOS)
    by_protocol = {}
    for p in PROXIES_VIVOS:
        proto = p.protocol.value
        by_protocol[proto] = by_protocol.get(proto, 0) + 1
    return {"total_alive": total, "by_protocol": by_protocol}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
