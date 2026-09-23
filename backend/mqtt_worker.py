import asyncio
import logging

from core.config import get_settings
from .mqtt.consumer import MQTTConsumer

logging.basicConfig(
    level=logging.INFO,
)

async def main() -> None:
    settings = get_settings()

    consumer = MQTTConsumer(
        settings
    )

    await consumer.run()

if __name__ == "__main__":
    asyncio.run(main())