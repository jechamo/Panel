import json
from typing import Any

import httpx

from app.models.node import MicroserviceNodeConfig, NodeRunResult


class MicroserviceExecutionError(Exception):
    pass


def run_microservice(config: MicroserviceNodeConfig) -> NodeRunResult:
    payload = _parse_payload(config.payload)
    headers = {header.key: header.value for header in config.headers if header.key}

    response = httpx.request(
        config.method,
        config.endpoint,
        headers=headers or None,
        json=payload,
        timeout=20.0,
    )
    response.raise_for_status()

    try:
        body: Any = response.json()
    except json.JSONDecodeError as error:
        raise MicroserviceExecutionError('Microservice response is not valid JSON.') from error

    return NodeRunResult(output=body, status_code=response.status_code)


def _parse_payload(raw_payload: str) -> Any:
    cleaned = raw_payload.strip()
    if not cleaned:
        return None

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise MicroserviceExecutionError(
            'Payload must be valid JSON before executing the node.',
        ) from error