import re
from dataclasses import dataclass


TOPIC_PATTERN = re.compile(
    r"^iot/v1/sensors/(?P<sensor_id>\d+)/"
    r"(?P<kind>telemetry|alerts|state)$"
)


@dataclass(frozen=True)
class ParsedTopic:
    sensor_id: int
    kind: str


def parse_topic(topic: str) -> ParsedTopic:
    match = TOPIC_PATTERN.fullmatch(topic)

    if not match:
        raise ValueError(f"Invalid MQTT topic: {topic}")

    return ParsedTopic(
        sensor_id=int(match.group("sensor_id")),
        kind=match.group("kind"),
    )