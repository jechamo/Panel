from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from app.llm.anthropic import build_structured_output_tool, get_anthropic_client
from app.models.node import AgentNodeConfig, NodeRunResult, OutputFieldItem


class AgentExecutionError(Exception):
    pass


def run_agent(config: AgentNodeConfig) -> NodeRunResult:
    if not config.model.strip():
        raise AgentExecutionError('Agent model is required before executing the node.')

    if not config.userPrompt.strip():
        raise AgentExecutionError('User prompt is required before executing the node.')

    if not config.outputFields:
        raise AgentExecutionError(
            'At least one output field is required before executing the agent.',
        )

    try:
        client = get_anthropic_client()
    except ValueError as error:
        raise AgentExecutionError(str(error)) from error

    schema_model = build_output_schema_model(config.outputFields)
    output_tool = build_structured_output_tool(schema_model.model_json_schema(by_alias=True))

    response = client.messages.create(
        model=config.model,
        max_tokens=1024,
        system=config.systemPrompt or None,
        messages=[
            {
                'role': 'user',
                'content': config.userPrompt,
            }
        ],
        tool_choice={'type': 'tool', 'name': output_tool['name']},
        tools=[output_tool],
    )

    tool_input = extract_tool_input(response.content, output_tool['name'])

    try:
        parsed_output = schema_model.model_validate(tool_input)
    except ValidationError as error:
        raise AgentExecutionError(
            'Anthropic structured output did not match the declared schema.',
        ) from error

    return NodeRunResult(
        output=parsed_output.model_dump(mode='json', by_alias=True),
        status_code=200,
    )


def build_output_schema_model(output_fields: list[OutputFieldItem]) -> type[BaseModel]:
    field_definitions: dict[str, tuple[Any, Any]] = {}

    for index, output_field in enumerate(output_fields):
        field_name = output_field.name.strip()
        field_description = output_field.description.strip()

        if not field_name:
            raise AgentExecutionError('Each output field must include a name.')

        if not field_description:
            raise AgentExecutionError(f'Output field "{field_name}" must include a description.')

        internal_name = f'field_{index}'
        field_definitions[internal_name] = (
            str,
            Field(..., alias=field_name, description=field_description),
        )

    return create_model(
        'AgentStructuredOutput',
        __config__=ConfigDict(extra='forbid', populate_by_name=False),
        **field_definitions,
    )


def extract_tool_input(content_blocks: list[Any], tool_name: str) -> dict[str, Any]:
    for block in content_blocks:
        if getattr(block, 'type', None) == 'tool_use' and getattr(block, 'name', None) == tool_name:
            return getattr(block, 'input', {})

    raise AgentExecutionError(
        'Anthropic response did not include the structured output tool payload.',
    )