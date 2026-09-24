import asyncio
import logging
import time

import paho.mqtt.client as mqtt
from sqlalchemy import select
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

from core.config import Settings
from database.session import SessionLocal
from mqtt.schemas import AlertMessage, StateMessage
from mqtt.topics import parse_topic
from services.alerts import process_alert
from models import Sensor
from core.telegram import send_message
from sqlalchemy.orm import selectinload
from models import TelegramAccount, Sensor


logger = logging.getLogger(__name__)


class MQTTConsumer:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.loop: asyncio.AbstractEventLoop | None = None
        self.queue: asyncio.Queue = asyncio.Queue()

        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=settings.MQTT_CLIENT_ID,
            protocol=mqtt.MQTTv5,
            transport="websockets",
            manual_ack=True,
        )

        self.client.username_pw_set(
            username=settings.MQTT_USERNAME,
            password=settings.MQTT_PASSWORD,
        )

        #self.client.tls_set()

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        logger.info(
            "MQTT connected: %s",
            reason_code,
        )

        subscriptions = [
            (
                "iot/v1/sensors/+/telemetry",
                1,
            ),
            (
                "iot/v1/sensors/+/alerts",
                1,
            ),
            (
                "iot/v1/sensors/+/state",
                1,
            ),
        ]

        result, mid = client.subscribe(
            subscriptions
        )

        logger.info(
            "MQTT subscribe result=%s mid=%s",
            result,
            mid,
        )

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties,) -> None:
        logger.warning(
            "MQTT disconnected: %s",
            reason_code,
        )

    def _on_message(self, client, userdata, message) -> None:
        if self.loop is None:
            logger.error(
                "Async event loop not initialized"
            )
            return

        item = (message.topic, bytes(message.payload), message.mid, message.qos)

        self.loop.call_soon_threadsafe(
            self.queue.put_nowait,
            item,
        )

    async def _process_message(
        self,
        topic: str,
        payload: bytes,
    ) -> None:

        parsed = parse_topic(topic)

        if parsed.kind == "alerts":
            data = AlertMessage.model_validate_json(payload)

            created = await process_alert(
                session_factory=SessionLocal,
                sensor_id=parsed.sensor_id,
                message=data,
            )

            if created:
                chats = []
                async with SessionLocal() as session:
                    result = await session.execute(
                        select(Sensor)
                        .options(selectinload(Sensor.telegram_accounts))
                        .where(Sensor.id == parsed.sensor_id)
                    )
                    sensor = result.scalar_one_or_none()

                    if sensor is None:
                        raise ValueError(
                            f"Unknown sensor: "
                            f"{parsed.sensor_id}"
                        )

                    telegram_accounts = [account for account in sensor.telegram_accounts if account.chat_id is not None]
                    chats.extend(telegram_accounts)

                message = "🚨 ALERTA DE EMERGÊNCIA! 🚨\n\n"
                message += f"⚠️ TOMBAMENTO DETECTADO NO {sensor.name}!\n\n"
                message += f"🕒 Horário: {data.occurred_at}\n"
                message += "📍 Localização: Raspberry Pi - TumbleGuard\n\n"
                message += f"Leituras: X= {data.x}, Y= {data.y}, Z= {data.z}, inclination: {data.inclination}\n\n"
                message += "Por favor, verifique imediatamente!"

                for chat in chats:
                    await send_message(chat.chat_id, message)

                logger.info(
                    "New alert from sensor=%s",
                    parsed.sensor_id,
                )

            return

        if parsed.kind == "state":
            data = StateMessage.model_validate_json(
                payload
            )

            async with SessionLocal() as session:
                sensor = await session.get(
                    Sensor,
                    parsed.sensor_id,
                )

                if sensor is None:
                    raise ValueError(
                        f"Unknown sensor: "
                        f"{parsed.sensor_id}"
                    )

                sensor.last_state = data.state
                sensor.last_seen_at = data.occurred_at

                await session.commit()

            return

        raise ValueError(
            f"Unsupported topic: {topic}"
        )

    async def _worker(self) -> None:

        while True:

            topic, payload, mid, qos = (
                await self.queue.get()
            )

            try:
                await self._process_message(
                    topic,
                    payload,
                )

            except ValueError as exc:
                # Erros permanentes:
                # JSON inválido, tópico inválido,
                # sensor inexistente etc.
                logger.error(
                    "Permanent MQTT message error: %s",
                    exc,
                )

                if qos > 0:
                    self.client.ack(mid, qos)

            except Exception:
                logger.exception(
                    "Error processing MQTT message"
                )

                # Não enviar ACK.
                #
                # Derrubamos a conexão para provocar
                # reconexão e reentrega de mensagens
                # QoS 1 que ainda não foram ACKadas.
                self.client.disconnect()

            else:
                if qos > 0:
                    self.client.ack(mid, qos)

            finally:
                self.queue.task_done()

    async def run(self) -> None:

        self.loop = asyncio.get_running_loop()

        properties = Properties(
            PacketTypes.CONNECT
        )

        properties.SessionExpiryInterval = (
            self.settings.MQTT_SESSION_EXPIRY
        )

        self.client.connect(
            self.settings.MQTT_HOST,
            self.settings.MQTT_PORT,
            self.settings.MQTT_KEEPALIVE,
            clean_start=False,
            properties=properties,
        )

        self.client.loop_start()

        logger.info(
            "MQTT worker started"
        )

        try:
            await self._worker()

        finally:
            self.client.disconnect()
            self.client.loop_stop()
