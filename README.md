# Panel

Mini-n8n local para encadenar agentes LLM y microservicios HTTP mediante un canvas visual de nodos conectables.

## Requisitos previos

- Python 3.11+
- Node.js 20+
- pnpm
- pip

## Arranque local

La Fase 1 deja operativo el backend. El frontend todavia no esta implementado.

1. Instala dependencias del backend desde [backend/pyproject.toml](backend/pyproject.toml).
2. Ejecuta [scripts/run.sh](scripts/run.sh) en Unix o [scripts/run.ps1](scripts/run.ps1) en Windows.
3. Comprueba `GET http://127.0.0.1:8000/health`.

## Referencias

- [PLAN.md](PLAN.md)
- [AGENTS.md](AGENTS.md)