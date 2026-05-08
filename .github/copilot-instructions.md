# Copilot Instructions

- Usa AGENTS.md como fuente de verdad de stack, convenciones y flujo de trabajo.
- Antes de tocar codigo, lee PLAN.md y trabaja solo en la fase pendiente actual.
- Frontend con TypeScript estricto.
- Backend con type hints completos y modelos Pydantic.
- Los componentes React deben ser funcionales y basados en hooks; no usar clases.
- Nombrado: kebab-case para archivos, PascalCase para componentes y tipos, snake_case en Python.
- No introducir dependencias nuevas sin justificarlo en el commit.
- Cada fase que anada logica de backend debe incluir tests minimos con pytest.