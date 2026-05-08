from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from app.llm.anthropic import run_anthropic_structured_output
from app.llm.catalog import get_model_provider
from app.llm.gemini import run_gemini_structured_output
from app.llm.openai import run_openai_structured_output
from app.models.node import AgentNodeConfig, NodeExecutionContext, NodeRunResult, OutputFieldItem
from app.templating.resolver import TemplateResolutionError, resolve_template_value


class AgentExecutionError(Exception):
    pass


def run_agent(config: AgentNodeConfig) -> NodeRunResult:
    return run_agent_with_context(config, NodeExecutionContext())


def run_agent_with_context(
    config: AgentNodeConfig,
    context: NodeExecutionContext,
) -> NodeRunResult:
    if not config.model.strip():
        raise AgentExecutionError('Agent model is required before executing the node.')

    try:
        resolved_system_prompt = _resolve_prompt(config.systemPrompt, context)
        resolved_user_prompt = _resolve_prompt(config.userPrompt, context)
    except TemplateResolutionError as error:
        raise AgentExecutionError(str(error)) from error

    if not resolved_user_prompt.strip():
        raise AgentExecutionError('User prompt is required before executing the node.')

    if not config.outputFields:
        raise AgentExecutionError(
            'At least one output field is required before executing the agent.',
        )

    try:
        provider = get_model_provider(config.model)
    except ValueError as error:
        raise AgentExecutionError(str(error)) from error

    schema_model = build_output_schema_model(config.outputFields)
    input_schema = schema_model.model_json_schema(by_alias=True)

    try:
        tool_input = _run_structured_output_request(
            provider=provider,
            model=config.model,
            system_prompt=resolved_system_prompt,
            user_prompt=resolved_user_prompt,
            input_schema=input_schema,
        )
    except ValueError as error:
        raise AgentExecutionError(str(error)) from error

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


def _resolve_prompt(raw_prompt: str, context: NodeExecutionContext) -> str:
    resolved_prompt = resolve_template_value(
        raw_prompt,
        flow_id=context.flowId,
        input_data=context.input,
    )

    if isinstance(resolved_prompt, str):
        return resolved_prompt

    return str(resolved_prompt)


def _run_structured_output_request(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_schema: dict[str, Any],
) -> dict[str, Any]:
    if provider == 'anthropic':
        return run_anthropic_structured_output(model, system_prompt, user_prompt, input_schema)

    if provider == 'openai':
        return run_openai_structured_output(model, system_prompt, user_prompt, input_schema)

    if provider == 'gemini':
        return run_gemini_structured_output(model, system_prompt, user_prompt, input_schema)

    raise AgentExecutionError(f'Unsupported model provider "{provider}".')