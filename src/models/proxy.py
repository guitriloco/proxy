from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class Protocol(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class ProxyStatus(Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    DEAD = "dead"

@dataclass
class Proxy:
    ip: str
    port: int
    protocol: Protocol = Protocol.HTTP
    status: ProxyStatus = ProxyStatus.UNKNOWN
    latency: Optional[float] = None
    last_check: Optional[datetime] = None
    
    @property
    def address(self) -> str:
        return f"{self.ip}:{self.port}"
    
    def __str__(self) -> str:
        return self.address
    
    def __hash__(self) -> int:
        return hash((self.ip, self.port, self.protocol.value))
