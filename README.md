# Panel

Mini-n8n local para encadenar agentes LLM y microservicios HTTP mediante un canvas visual de nodos conectables.

## Requisitos previos

- Python 3.11+
- Node.js 20+
- pnpm
- pip

## Arranque local

La Fase 2 deja operativo el backend y el scaffold visual del frontend.

1. Instala dependencias del backend desde [backend/pyproject.toml](backend/pyproject.toml).
2. Instala dependencias del frontend con `cd frontend && corepack pnpm install`.
3. Ejecuta [scripts/run.sh](scripts/run.sh) en Unix o [scripts/run.ps1](scripts/run.ps1) en Windows.
4. Comprueba `GET http://127.0.0.1:8000/health` y abre `http://127.0.0.1:5173`.
5. Verifica que la cabecera del frontend muestra el estado de conexion con el backend en verde o rojo.
6. Haz click en un nodo del canvas para abrir el panel lateral y editar su configuracion en memoria.
7. Usa los botones Guardar y Cargar para persistir flujos en `backend/storage/flows/`.
8. En un nodo Microservicio, pulsa `Run` para ejecutar la request y revisar su salida JSON en el panel.
9. Para nodos Agente, define `ANTHROPIC_API_KEY` en `backend/.env`, escribe un model id valido en el nodo y pulsa `Run` para ver la salida textual.
10. Para subir adjuntos en un nodo Agente, guarda antes el flujo y luego arrastra o selecciona `.docx`, `.xlsx` o `.pdf`; el backend los guarda en `backend/storage/uploads/<flow_id>/<file_id>/`.
11. Tanto el nodo Agente como el nodo Microservicio resuelven plantillas backend como `{{env.KEY}}`, `{{input.campo}}` y `{{archivos.nombre}}` justo antes de ejecutarse.
12. Si un nodo tiene un predecesor conectado y usas `{{input.*}}`, el backend tomara el output cacheado del nodo anterior desde el flujo guardado; ejecuta primero el nodo predecesor al menos una vez.
13. El boton `Run All` guarda el flujo actual, ejecuta los nodos en orden topologico y recarga en la UI los estados y outputs devueltos por backend.
14. La Fase 13 anade un panel de Settings para cargar claves de Anthropic, OpenAI y Gemini; en esta version se guardan en `backend/.env` por simplicidad operativa local, y el selector del nodo Agente se alimenta desde `backend/config/models.yaml`.

## Referencias

- [PLAN.md](PLAN.md)
- [AGENTS.md](AGENTS.md)