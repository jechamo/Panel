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

## Referencias

- [PLAN.md](PLAN.md)
- [AGENTS.md](AGENTS.md)