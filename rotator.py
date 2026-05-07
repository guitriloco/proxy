"""
Gateway Rotator
Proxy rotativo que distribui tráfego entre proxies vivos.
"""
import asyncio
import random
from dataclasses import dataclass


@dataclass
class RotationConfig:
    """Configuração do gateway"""
    listen_host: str = "0.0.0.0"
    listen_port: int = 8080
    sticky_sessions: bool = True


class ProxyRotator:
    """Rotador de proxies com sticky sessions"""
    
    def __init__(self, proxies: list, config: RotationConfig = None):
        self.proxies = proxies
        self.config = config or RotationConfig()
        self._sessions = {}  # client_id -> proxy
    
    def get_proxy_for_client(self, client_id: str) -> str:
        """Retorna proxy para o cliente (sticky session)"""
        if self.config.sticky_sessions and client_id in self._sessions:
            return self._sessions[client_id]
        
        proxy = random.choice(self.proxies)
        if self.config.sticky_sessions:
            self._sessions[client_id] = proxy
        return proxy
    
    async def handle_client(self, reader, writer):
        """Encaminha tráfego para um proxy"""
        client_id = f"{writer.get_extra_info('peername')}"
        proxy = self.get_proxy_for_client(client_id)
        
        try:
            # Aqui seria a implementação do túnel TCP
            # Por enquanto apenas log
            print(f"[→] {client_id} -> {proxy}")
        except Exception as e:
            print(f"[✗] Erro: {e}")
        finally:
            writer.close()


async def start_gateway(proxies: list, host: str = "0.0.0.0", port: int = 8080):
    """Inicia o gateway"""
    config = RotationConfig(listen_host=host, listen_port=port)
    rotator = ProxyRotator(proxies)
    
    server = await asyncio.start_server(
        rotator.handle_client,
        host,
        port
    )
    
    print(f"[✓] Gateway ativo em {host}:{port}")
    
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    # Exemplo de uso
    test_proxies = ["192.168.1.1:8080", "10.0.0.1:3128"]
    asyncio.run(start_gateway(test_proxies))
