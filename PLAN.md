# PLAN

## [x] Fase 0 - Bootstrap

**Descripcion**

Esta es la Fase A. Crear la documentacion base del repo, la estructura de carpetas, los stubs iniciales y el commit de bootstrap.

**Hecho cuando**

- Existen AGENTS.md, .github/copilot-instructions.md, PLAN.md y README.md con el contenido base solicitado.
- Existe el arbol de carpetas completo con .gitkeep donde corresponde.
- Existen .gitignore, .editorconfig, LICENSE y .gitattributes.
- El repo conserva git y tiene un commit `chore: bootstrap project structure and plan`.ok
- No se implementa todavia logica funcional de fases posteriores.

**Archivos que tocara**

- AGENTS.md
- .github/copilot-instructions.md
- PLAN.md
- README.md
- .gitignore
- .editorconfig
- LICENSE
- .gitattributes
- .vscode/settings.json
- .vscode/extensions.json
- .vscode/launch.json
- backend/**
- frontend/**
- scripts/**

**Fecha completada**

- 2026-05-08

## [x] Fase 1 - Backend scaffold

**Descripcion**

FastAPI minimo corriendo. Endpoint GET /health -> { "ok": true }. Configuracion via .env + Pydantic Settings. Ruff y pytest configurados. Test del health.

**Hecho cuando**

- Arranca una app FastAPI minima en localhost:8000.
- GET /health devuelve { "ok": true } con el contrato base del backend.
- Existe configuracion via .env y Settings de Pydantic.
- Ruff y pytest quedan configurados y pasan al menos para el health check.

**Archivos que tocara**

- backend/app/main.py
- backend/app/core/*
- backend/app/models/*
- backend/tests/*
- backend/pyproject.toml o backend/requirements.txt
- scripts/run.sh
- scripts/run.ps1
- README.md

Nota futura: la persistencia de flujos sigue prevista en Fase 5 con almacenamiento JSON en `backend/storage/flows/`.

**Fecha completada**

- 2026-05-08

## [x] Fase 2 - Frontend scaffold

**Descripcion**

Vite + React + TS + Tailwind + React Flow. Canvas vacio con un boton flotante "Anadir Agente" / "Anadir Microservicio" que crea nodos dummy de cada tipo, arrastrables y conectables. Sin paneles aun.

**Hecho cuando**

- Arranca el frontend en localhost:5173.
- Existe un canvas con zoom, pan, nodos dummy arrastrables y conexiones.
- Hay acciones para crear nodos Agente y Microservicio.
- Aun no existen paneles funcionales de configuracion.

**Archivos que tocara**

- frontend/package.json
- frontend/tsconfig.json
- frontend/vite.config.ts
- frontend/tailwind.config.ts
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/components/canvas/*
- frontend/src/lib/*
- frontend/src/stores/*
- scripts/run.sh
- scripts/run.ps1
- README.md

**Fecha completada**

- 2026-05-08

## [x] Fase 3 - Conexion front-back

**Descripcion**

CORS configurado en backend. Cliente API en frontend (lib/api.ts). Indicador de conexion en la UI (verde/rojo) llamando a /health.

**Hecho cuando**

- Backend acepta el origen del frontend con CORS.
- El frontend tiene cliente API tipado para consultar /health.
- La UI muestra el estado de conexion de forma visible.

**Archivos que tocara**

- backend/app/main.py
- backend/app/core/*
- frontend/src/lib/api.ts
- frontend/src/App.tsx
- frontend/src/components/ui/*
- README.md

**Fecha completada**

- 2026-05-08

## [x] Fase 4 - Paneles de configuracion

**Descripcion**

Click en nodo -> abre panel lateral. Formulario completo para Agente y para Microservicio (incluyendo lista dinamica de campos de salida y lista dinamica de headers). Datos guardados en el store de Zustand. Aun no se ejecuta nada.

**Hecho cuando**

- Hacer click en un nodo abre su panel lateral.
- El nodo Agente permite editar prompts, modelo, adjuntos y campos de salida.
- El nodo Microservicio permite editar endpoint, metodo, headers y payload.
- Toda la configuracion persiste en Zustand.

**Archivos que tocara**

- frontend/src/components/panels/*
- frontend/src/components/ui/*
- frontend/src/components/canvas/*
- frontend/src/stores/*
- frontend/src/lib/types*

**Fecha completada**

- 2026-05-08

## [x] Fase 5 - Persistencia de flujos

**Descripcion**

Endpoints POST /flows, GET /flows, GET /flows/{id}, PUT /flows/{id}, DELETE /flows/{id}. Almacenamiento en backend/storage/flows/<id>.json. UI: botones "Guardar" y "Cargar" con lista.

**Hecho cuando**

- Existen los endpoints CRUD de flows.
- Los flujos se guardan como JSON versionado en backend/storage/flows/.
- La UI puede guardar y cargar flujos desde una lista.
- Hay al menos un test feliz por endpoint nuevo o por ruta critica del CRUD.

**Archivos que tocara**

- backend/app/api/*
- backend/app/models/*
- backend/app/core/*
- backend/storage/flows/*
- backend/tests/*
- frontend/src/lib/*
- frontend/src/components/ui/*
- frontend/src/App.tsx

**Fecha completada**

- 2026-05-08

## [x] Fase 6 - Ejecutor de Microservicio

**Descripcion**

Endpoint POST /nodes/{id}/run para nodo de tipo microservicio. Hace la llamada HTTP con httpx. Devuelve respuesta. Frontend muestra output con un viewer JSON expandible.

**Hecho cuando**

- Existe la ruta POST /nodes/{id}/run para microservicios.
- El backend ejecuta la llamada HTTP con httpx respetando configuracion del nodo.
- La respuesta se devuelve con el contrato estandar del backend.
- El frontend muestra el JSON de salida del nodo microservicio.

**Archivos que tocara**

- backend/app/api/*
- backend/app/executors/microservice_executor.py
- backend/app/models/*
- backend/tests/*
- frontend/src/components/panels/*
- frontend/src/components/ui/*
- frontend/src/lib/*

**Fecha completada**

- 2026-05-08

## [x] Fase 7 - Ejecutor de Agente (proveedor unico: Anthropic)

**Descripcion**

Cliente anthropic configurado. Llamada con system + user prompt. Sin schema estructurado todavia. Devuelve texto crudo. UI muestra el texto.

**Hecho cuando**

- Existe un cliente Anthropic funcional en backend.
- El nodo Agente ejecuta system + user prompt.
- La respuesta del modelo se devuelve como texto crudo.
- La UI muestra el output textual del nodo.

**Archivos que tocara**

- backend/app/llm/anthropic.py
- backend/app/executors/agent_executor.py
- backend/app/api/*
- backend/app/models/*
- backend/tests/*
- frontend/src/components/panels/*
- frontend/src/lib/*

**Fecha completada**

- 2026-05-08

## [x] Fase 8 - Salida estructurada

**Descripcion**

Generar JSON schema desde la lista de campos del nodo. Pasar al SDK como tools (Anthropic) / response_format (OpenAI) / response_schema (Gemini). Validar la respuesta con Pydantic.

**Hecho cuando**

- El schema JSON se genera desde los campos de salida del nodo.
- El proveedor recibe el schema mediante su mecanismo nativo.
- La respuesta queda validada con Pydantic.
- El output final del nodo coincide exactamente con los campos definidos.

**Archivos que tocara**

- backend/app/executors/agent_executor.py
- backend/app/llm/*
- backend/app/models/*
- backend/tests/*
- frontend/src/components/panels/*

**Fecha completada**

- 2026-05-08

## [x] Fase 9 - Adjuntos: upload y parseo

**Descripcion**

Endpoint POST /files/upload. Parsers para docx/xlsx/pdf que devuelven texto. Almacenar en backend/storage/uploads/<flow_id>/<file_id>. UI: zona de drop en el panel del agente.

**Hecho cuando**

- Existe POST /files/upload.
- El backend parsea docx, xlsx y pdf a texto.
- Los archivos se guardan en backend/storage/uploads/.
- La UI permite arrastrar o seleccionar adjuntos en el nodo Agente.

**Archivos que tocara**

- backend/app/api/*
- backend/app/parsers/*
- backend/app/models/*
- backend/tests/*
- backend/storage/uploads/*
- frontend/src/components/panels/*
- frontend/src/lib/*

**Fecha completada**

- 2026-05-08

## [x] Fase 10 - Templating de variables

**Descripcion**

Modulo templating/ que resuelve {{archivos.x}}, {{input.y}}, {{env.Z}}. Integrado en el ejecutor de agente y de microservicio. Tests unitarios.

**Hecho cuando**

- Existe un modulo de templating reusable.
- Resuelve correctamente archivos, input y env.
- Esta integrado en ejecutores de agente y microservicio.
- Hay tests unitarios del modulo y de integracion minima.

**Archivos que tocara**

- backend/app/templating/*
- backend/app/executors/*
- backend/app/models/*
- backend/tests/*

**Fecha completada**

- 2026-05-08

## [x] Fase 11 - Encadenamiento

**Descripcion**

Cuando un nodo se ejecuta, su output queda disponible para el siguiente conectado. Resolver {{input.x}} usa el output del nodo predecesor por la edge.

**Hecho cuando**

- La salida de un nodo se cachea para ejecuciones posteriores del flujo.
- El backend resuelve el predecesor conectado por la edge correspondiente.
- {{input.x}} funciona contra el output del nodo anterior.
- Existen tests del camino feliz de encadenamiento.

**Archivos que tocara**

- backend/app/executors/*
- backend/app/models/*
- backend/app/api/*
- backend/tests/*
- frontend/src/lib/*

**Fecha completada**

- 2026-05-08

## [x] Fase 12 - Run global y Run de nodo

**Descripcion**

Endpoint POST /flows/{id}/run con topological sort de los nodos. Boton "Run All" en la UI. Boton "Run" por nodo (asume que predecesores ya tienen output cacheado de la ultima ejecucion; si no, error claro). Indicadores visuales de estado por nodo.

**Hecho cuando**

- Existe POST /flows/{id}/run con orden topologico.
- La UI ofrece Run All y Run por nodo.
- Cada nodo expone estado visual idle, running, success o error.
- Los errores por dependencias faltantes son claros y consistentes.

**Archivos que tocara**

- backend/app/executors/graph_runner.py
- backend/app/api/*
- backend/app/models/*
- backend/tests/*
- frontend/src/components/canvas/*
- frontend/src/components/ui/*
- frontend/src/stores/*

**Fecha completada**

- 2026-05-08

## [x] Fase 13 - Multi-proveedor + Settings

**Descripcion**

Soporte OpenAI y Gemini. Panel de Settings en la UI para meter API keys (guardadas cifradas en backend/storage/settings.json con clave de maquina, o simplemente en .env si lo prefieres y lo justificas). Selector de modelo en el nodo de agente lee de config/models.yaml.

**Hecho cuando**

- El backend soporta Anthropic, OpenAI y Gemini.
- Existe un panel de Settings para gestionar credenciales.
- El selector de modelo del nodo Agente lee backend/config/models.yaml.
- La estrategia elegida para persistir API keys queda documentada y justificada.

**Archivos que tocara**

- backend/app/llm/*
- backend/app/api/*
- backend/app/models/*
- backend/config/models.yaml
- backend/storage/settings.json o .env
- backend/tests/*
- frontend/src/components/panels/*
- frontend/src/stores/*
- README.md

**Fecha completada**

- 2026-05-08

## [x] Fase 14 - Viewer de salida

**Descripcion**

Componente que renderiza el JSON de salida con campos colapsables, copia al clipboard, y formato bonito (no <pre> crudo).

**Hecho cuando**

- Existe un viewer JSON reutilizable.
- Los campos pueden expandirse y colapsarse.
- El usuario puede copiar la salida al portapapeles.
- El render no usa un <pre> crudo como solucion final.

**Archivos que tocara**

- frontend/src/components/ui/*
- frontend/src/components/panels/*
- frontend/src/App.tsx

**Fecha completada**

- 2026-05-09

## [ ] Fase 15 - Polish

**Descripcion**

Manejo robusto de errores en UI (toasts), panel de logs por nodo (input + output + timestamp + errores), README completo con screenshots/gif, instrucciones de despliegue local, troubleshooting.

**Hecho cuando**

- La UI muestra errores de forma robusta y clara.
- Existe panel de logs por nodo con input, output, timestamp y errores.
- README queda completo con arranque, uso, troubleshooting y material visual.
- El flujo local queda suficientemente documentado para uso recurrente.

**Archivos que tocara**

- frontend/src/components/ui/*
- frontend/src/components/panels/*
- frontend/src/stores/*
- backend/storage/runs/*
- README.md

## Notas

- El arbol base se creo en la Fase 0 con stubs no funcionales para evitar mezclar bootstrap con implementacion.