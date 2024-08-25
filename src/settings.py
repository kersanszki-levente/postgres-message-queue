import os
from dataclasses import dataclass

@dataclass
class ConnectionParameters:
    host: str = os.environ.get("POSTGRES_HOST", "postgres")
    user: str = os.environ.get("POSTGRES_USER", "postgres")
    password: str = os.environ.get("POSTGRES_PASSWORD", "secret")
    dbname: str = "scheduling"
