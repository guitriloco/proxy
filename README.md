# Proxy Aggregator

Sistema de proxy aggregator que **coleta**, **valida** e **serve** proxies de múltiplas fontes em tempo real.

## 🎯 O que faz

1. **Coleta** proxies de 70+ fontes (GitHub, APIs, sites especializados)
2. **Valida** se estão ativos com health check automático
3. **Serve** via API REST com atualização automática a cada 20 minutos
4. **Categoriza** por protocolo (SOCKS5, HTTP, HTTPS, SOCKS4)

## 📦 Instalar

```bash
pip install -r requirements.txt
```

## 🚀 Usar

### Rodar a API:
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Endpoints:

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/` | Status da API |
| GET | `/health` | Health check |
| GET | `/api/v1/proxies` | Lista todos os proxies vivos |
| GET | `/api/v1/proxies?protocol=socks5` | Filtra por protocolo |
| GET | `/api/v1/proxies?limit=50` | Limita quantidade |
| GET | `/api/v1/proxies/random` | Proxy aleatório |
| GET | `/api/v1/stats` | Estatísticas |

### Exemplo de resposta:
```json
{
  "total": 150,
  "proxies": [
    {"ip": "192.168.1.1", "port": 8080, "protocol": "socks5", "latency": 120.5},
    {"ip": "10.0.0.1", "port": 3128, "protocol": "http", "latency": 85.3}
  ]
}
```

## 🔧 Scripts

### Extrair proxies manualmente:
```bash
python -m src.collectors.unified
```

### Validar proxies:
```bash
python -m src.validators.health_checker
```

## 📂 Estrutura

```
src/
├── sources/registry.py     # Fontes de proxies
├── models/proxy.py         # Modelos de dados
├── collectors/unified.py  # Coletor assíncrono
└── validators/health_checker.py  # Health checker

api/
└── main.py                # API FastAPI

gateway/
└── rotator.py             # Proxy rotativo (em desenvolvimento)
```

## ⚙️ Configuração

- **Intervalo de atualização:** 20 minutos (configurável em `api/main.py`)
- **Timeout de health check:** 5 segundos
- **Max concurrent checks:** 100

## 📝 Fontes inclusas

- GitHub (TheSpeedX, monosans, jetkai, etc.)
- proxyscrape.com
- proxy-list.download
- spys.me
- proxyspace.pro
- E mais 60+ fontes...
