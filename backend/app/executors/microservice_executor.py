import json
from typing import Any

import httpx

from app.models.node import MicroserviceNodeConfig, NodeExecutionContext, NodeRunResult
from app.templating.resolver import TemplateResolutionError, resolve_template_value


class MicroserviceExecutionError(Exception):
    pass


def run_microservice(config: MicroserviceNodeConfig) -> NodeRunResult:
    return run_microservice_with_context(config, NodeExecutionContext())


def run_microservice_with_context(
    config: MicroserviceNodeConfig,
    context: NodeExecutionContext,
) -> NodeRunResult:
    try:
        resolved_endpoint = _resolve_string(config.endpoint, context)
        resolved_payload = resolve_template_value(
            config.payload,
            flow_id=context.flowId,
            input_data=context.input,
        )
        headers = {
            _resolve_string(header.key, context): _resolve_string(header.value, context)
            for header in config.headers
            if header.key
        }
    except TemplateResolutionError as error:
        raise MicroserviceExecutionError(str(error)) from error

    payload = _parse_payload(resolved_payload)

    response = httpx.request(
        config.method,
        resolved_endpoint,
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


def _parse_payload(raw_payload: Any) -> Any:
    if raw_payload is None:
        return None

    if not isinstance(raw_payload, str):
        return raw_payload

    cleaned = raw_payload.strip()
    if not cleaned:
        return None

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise MicroserviceExecutionError(
            'Payload must be valid JSON before executing the node.',
        ) from error


def _resolve_string(raw_value: str, context: NodeExecutionContext) -> str:
    resolved_value = resolve_template_value(
        raw_value,
        flow_id=context.flowId,
        input_data=context.input,
    )

    if isinstance(resolved_value, str):
        return resolved_value

    return json.dumps(resolved_value, ensure_ascii=False)