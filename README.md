# Proxy Aggregator

Sistema que **coleta**, **valida** e **serve** proxies de múltiplas fontes automaticamente.

## O que faz

1. **Coleta** proxies de ~40 fontes (GitHub, APIs, sites)
2. **Valida** se estão ativos com health check automático
3. **Serve** via API REST com atualização a cada 20 min
4. **Categoriza** por protocolo (SOCKS5, HTTP, SOCKS4)

## Instalar

```bash
pip install -r requirements.txt
```

## Usar

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

| URL | Descrição |
|-----|-----------|
| `GET /` | Status da API |
| `GET /health` | Health check |
| `GET /api/v1/proxies` | Lista proxies vivos |
| `GET /api/v1/proxies?protocol=socks5` | Filtra por protocolo |
| `GET /api/v1/proxies?limit=50` | Limita quantidade |
| `GET /api/v1/proxies/random` | Proxy aleatório |
| `GET /api/v1/stats` | Estatísticas |

## Estrutura

```
src/
├── sources/registry.py     # Fontes de proxies
├── models/proxy.py         # Modelos de dados
├── collectors/unified.py  # Coletor assíncrono
└── validators/health_checker.py  # Health checker
api/
└── main.py                # API FastAPI
```

## Exemplo de resposta

```json
{
  "total": 150,
  "proxies": [
    {"ip": "192.168.1.1", "port": 8080, "protocol": "socks5", "latency": 120.5}
  ]
}
```
