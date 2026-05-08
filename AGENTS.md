# AGENTS

## Resumen del producto

Webapp local tipo mini-n8n para construir flujos visuales con nodos arrastrables y conectables.
Los nodos iniciales son Agente LLM y Microservicio HTTP.
Cada nodo expone entradas y salidas reutilizables dentro del grafo.
La ejecucion puede ser global o por nodo respetando dependencias previas.
La UX objetivo es visual, limpia y oscura por defecto, con zoom, pan y paneles laterales.

## Stack tecnico

- Frontend: Vite + React + TypeScript + React Flow (@xyflow/react) + Tailwind CSS + Zustand.
- Backend: Python 3.11+ + FastAPI + Uvicorn + Pydantic v2.
- LLMs: clientes oficiales anthropic, openai, google-genai. No usar Copilot CLI como runtime.
- Parseo de adjuntos: python-docx, openpyxl, pypdf.
- Persistencia inicial: ficheros JSON en backend/storage/flows/.
- Gestor de paquetes: pnpm para frontend, uv o pip + requirements.txt para backend.
- Arranque local previsto: scripts/run.sh y scripts/run.ps1 levantando backend en :8000 y frontend en :5173 en paralelo.

## Convenciones del proyecto

- Antes de tocar codigo, leer PLAN.md y trabajar solo en la fase pendiente actual.
- Variables permitidas: {{archivos.<nombre_archivo_sin_extension>}}, {{input.<campo>}}, {{env.<KEY>}}.
- La resolucion de variables ocurre en backend justo antes de ejecutar un nodo.
- La salida estructurada de agentes siempre usa el modo nativo del proveedor: tool use, json_schema o response_schema.
- Los IDs de nodo son UUID v4 generados en frontend al crear nodos.
- El formato del flujo guardado es { "id", "name", "nodes": [...], "edges": [...], "version": 1 }.
- Las respuestas de backend siguen siempre { "ok": bool, "data": ..., "error": { "code", "message" } }.
- Los modelos por proveedor viven en backend/config/models.yaml y no se hardcodean en codigo.
- Si no se conocen identificadores oficiales con certeza, models.yaml debe quedar vacio con comentario para que el usuario lo rellene.
- Cada ejecucion de nodo se guarda en backend/storage/runs/<run_id>.json con input, output, timestamps y errores.

## Estructura de carpetas

- .github/: instrucciones del repositorio para Copilot.
- .vscode/: configuracion de editor, extensiones recomendadas y debug local.
- backend/app/api/: routers de flows, nodes, runs, settings y files.
- backend/app/core/: configuracion y logging compartido.
- backend/app/executors/: ejecucion de nodos de agente, microservicio y del grafo.
- backend/app/llm/: integraciones por proveedor y abstracciones base.
- backend/app/parsers/: parseo de docx, xlsx y pdf.
- backend/app/models/: esquemas Pydantic del dominio y contratos API.
- backend/app/templating/: resolucion de placeholders {{...}}.
- backend/config/: configuracion editable del proyecto, incluido models.yaml.
- backend/storage/: persistencia local de flows, runs y uploads.
- backend/tests/: tests de backend con pytest.
- frontend/src/components/canvas/: canvas y nodos visuales.
- frontend/src/components/panels/: paneles laterales de configuracion y settings.
- frontend/src/components/ui/: primitives reutilizables de interfaz.
- frontend/src/stores/: estado global con Zustand.
- frontend/src/lib/: cliente API y tipos compartidos del frontend.
- frontend/src/pages/: paginas y shells de interfaz.
- frontend/public/: assets estaticos.
- scripts/: scripts de arranque local para Unix y Windows.

## Comandos clave

- `pwsh ./scripts/run.ps1`: arranque local previsto en Windows.
- `bash ./scripts/run.sh`: arranque local previsto en Unix.
- `cd backend && pytest`: tests de backend.
- `cd frontend && pnpm lint`: lint del frontend.

## Como anadir un nuevo tipo de nodo

1. Definir el schema del nodo y su configuracion en backend/app/models/ y en los tipos del frontend.
2. Crear el ejecutor correspondiente en backend/app/executors/ y sus endpoints si aplica.
3. Anadir el render del nodo y su formulario en frontend/src/components/canvas/ y frontend/src/components/panels/.
4. Extender el store de Zustand para persistir configuracion, output y estado visual.
5. Actualizar la serializacion del flujo y cubrir el comportamiento con tests de backend y checks de UI de la fase correspondiente.

## Como anadir un nuevo proveedor LLM

1. Crear el adaptador del proveedor en backend/app/llm/ siguiendo la interfaz comun.
2. Registrar configuracion y modelos disponibles en backend/config/models.yaml sin hardcodear identificadores en codigo.
3. Integrar el proveedor en el ejecutor de agente respetando salida estructurada nativa.
4. Exponer el proveedor en Settings y en el selector de modelo del nodo Agente.
5. Anadir tests del camino feliz y de errores de configuracion o respuesta invalida.