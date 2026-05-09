# Arranque local de Panel

Guía paso a paso para levantar el proyecto desde cero en tu máquina.

## Requisitos previos

- **Python 3.10+** (probado en 3.11)
- **Node.js 18+** (probado en 22) y npm
- **git**
- (Opcional) Una API key de al menos un proveedor: Anthropic, OpenAI, Google Gemini o un GitHub PAT con acceso a Models

Verifica las versiones:

```bash
python3 --version
node --version
npm --version
```

## 1. Clonar el repo y situarte en la rama

```bash
git clone <url-del-repo> Panel
cd Panel
git checkout claude/draggable-boxes-panel-XPlTZ
```

## 2. Levantar el backend

En una terminal, desde la raíz del proyecto:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Cuando veas `Uvicorn running on http://127.0.0.1:8000` el backend está listo.

Pruebas rápidas (en otra terminal):

```bash
curl http://localhost:8000/api/health
# {"ok":true}

curl http://localhost:8000/api/settings/providers
# Lista de proveedores LLM disponibles
```

La documentación interactiva queda en http://localhost:8000/docs.

## 3. Levantar el frontend

En otra terminal, desde la raíz:

```bash
cd frontend
npm install
npm run dev
```

Cuando veas `Local: http://localhost:5173/` abre esa URL en el navegador.

El frontend hace proxy de `/api` al backend en el puerto 8000 (configurado en `vite.config.ts`). Si cambias el puerto del backend, ajusta también el proxy.

## 4. Atajo: ambos servicios a la vez

Si prefieres un solo comando, desde la raíz del repo:

```bash
./start.sh
```

Lanza backend y frontend en paralelo y los corta a la vez con `Ctrl+C`.

## 5. Configurar al menos un proveedor

1. En la UI, pulsa **⚙️ Settings** arriba a la derecha.
2. Pega tu key en uno de los campos:
   - **Anthropic API Key** (`sk-ant-...`) → modelos `claude-sonnet-4-6`, etc.
   - **OpenAI API Key** (`sk-...`) → `gpt-4o`, etc.
   - **Gemini API Key** (`AIza...`) → `gemini-2.0-flash`, etc.
   - **GitHub Token** (`ghp_...`) con scope `models:read` → modelos vía GitHub Models.
3. **Save**. La key se cifra con Fernet antes de guardarse en `backend/data/panel.db`.

> Las keys nunca viajan al frontend después de guardarlas; la UI solo ve un booleano "configurado / no configurado".

## 6. Tu primer flujo

1. **Arrastra** una caja "🤖 Agent" desde la paleta izquierda al canvas.
2. **Configúrala** en el panel derecho:
   - System prompt: `Eres un asistente que extrae información estructurada.`
   - User prompt: `Dame el nombre de un país europeo y su capital.`
   - Output JSON fields: añade `pais` (descripción: "nombre del país") y `capital`.
3. Pulsa **▶ Run this node** en el panel derecho.
4. Verás el JSON `{ "pais": "...", "capital": "..." }` debajo del configurador.
5. Arrastra una caja "🔌 Microservice", conéctala desde el agente.
6. Configura URL `https://restcountries.com/v3.1/capital/{{<id_del_agente>.capital}}` y método `GET`. El `id_del_agente` aparece en el nodo (algo como `agent-xxxx-1`).
7. **▶ Run all** en la barra superior: ejecuta en orden topológico, cada nodo recibe los outputs de sus padres como contexto para los `{{...}}`.

## 7. Guardar y recargar flujos

- **Save**: la primera vez te pide nombre; después actualiza el flujo activo.
- Selector **— Load flow —** en la barra superior: lista los flujos guardados.
- **New**: limpia el canvas para empezar otro (te pedirá confirmación).

Los flujos viven en SQLite (`backend/data/panel.db`). Para reiniciar todo, borra el archivo y reinicia el backend.

## 8. Adjuntos en agentes

Dentro de un nodo Agent, sección **Attachments**, puedes subir:
- PDF (`.pdf`)
- Word (`.doc`, `.docx`)
- Excel (`.xlsx`, `.xls`)
- Texto plano (`.txt`, `.md`, `.csv`, `.json`)

El backend extrae el texto y lo concatena al user prompt antes de llamar al modelo. Los archivos quedan en `backend/data/uploads/` con un nombre aleatorio.

## 9. Ejecución

| Botón | Qué hace |
|---|---|
| **▶ Run all** (barra superior) | Orden topológico. Cada nodo recibe `{ <padre_id>: <output_padre> }`. Si un padre falla, los hijos quedan `skipped`. |
| **▶ Run this node** (panel derecho) | Solo ese nodo, usando los outputs cacheados de sus padres (los que ya ejecutaste antes). Útil para iterar sobre el último nodo sin re-ejecutar todo. |

## Encadenar y mapear outputs entre nodos

Cualquier output (sea agente o microservicio) puede alimentar a cualquier
otro nodo a través de placeholders en cualquier campo de texto:

- En el panel del nodo destino, abre **Variables disponibles** (sección
  arriba del prompt o de la URL).
- Verás los nodos predecesores y sus campos. Click en uno → se inserta
  `{{nodo.campo}}` en el último textarea/input que tuvieras enfocado.
- Las variables vienen de:
  - **cached**: shape real del último output del nodo padre (las más
    fiables — ya las has visto ejecutar).
  - **schema**: nombres declarados en `output_fields` de un agente
    aguas arriba (aunque aún no se haya ejecutado).
  - **node**: solo el ID, si aún no hay nada para inferir.
- Combinaciones soportadas: agent→agent, agent→api, api→agent, api→api,
  multi-padre (un nodo recibe outputs de varios padres).

Sintaxis manual también disponible: `{{node-id.path.to.field}}` con
profundidad arbitraria; `{{node-id.tags.0}}` para listas.

## Entornos restringidos / banca

Si tu entorno tiene la red filtrada, no permite instalar paquetes
externos, o requiere proxies/CAs corporativos:

- Lee [`OFFLINE_INSTALL.md`](OFFLINE_INSTALL.md) para la instalación
  aire-gap (vendor de wheels, npm offline cache, mirrors internos).
- Lee [`BANKING_DEPLOYMENT.md`](BANKING_DEPLOYMENT.md) para la matriz
  de proveedores LLM, cómo elegir entre Copilot CLI, Azure OpenAI,
  gateways internos, y cómo restringir el catálogo en `models.json`.

Resumen: si tu banco tiene `gh` autorizado, el provider más rápido de
configurar es **Copilot CLI** (no requiere pegar API keys, reusa la
auth de la CLI). Para Azure OpenAI corporativo, configura los 4 campos
del provider `Azure OpenAI` en Settings.

## Solución de problemas

**El frontend no recibe respuestas / errores CORS**
Asegúrate de que el backend está en `:8000` y el frontend en `:5173`. Si cambias puertos, edita el `allow_origins` en `backend/app/main.py` y el `proxy` en `frontend/vite.config.ts`.

**`Missing credential 'xxx_api_key'`**
No has guardado la key correspondiente al proveedor del nodo. Abre Settings y pégala.

**`Model did not return valid JSON`**
El modelo respondió pero no en formato JSON parseable. Suele pasar con prompts ambiguos o modelos pequeños. Refina el system prompt o usa un modelo más capaz.

**Puerto 8000 ocupado**
```bash
uvicorn app.main:app --reload --port 8001
# y cambia el proxy en frontend/vite.config.ts
```

**Borrar todo el estado local**
```bash
rm -rf backend/data
# Próximo arranque regenera la DB y la master key
```

**El frontend muestra TS errors después de un pull**
```bash
cd frontend && rm -rf node_modules && npm install
```

## Estructura del proyecto

```
Panel/
├── backend/
│   ├── pyproject.toml
│   ├── data/                    (creado en runtime: DB, uploads, master key)
│   └── app/
│       ├── main.py              FastAPI entry point
│       ├── db.py / models.py    SQLite + ORM
│       ├── crypto.py            Cifrado Fernet
│       ├── api/                 Rutas HTTP
│       ├── llm/                 Clientes LLM
│       ├── parsers/             PDF, DOCX, XLSX
│       └── runners/             Motor de grafo
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── components/          Canvas, paleta, nodos, paneles
│       ├── store/flow.ts        Zustand
│       └── api/client.ts
├── start.sh                     Lanzador conjunto
└── README.md
```

## Endpoints principales

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/health` | Liveness |
| GET | `/api/flows` | Lista flujos |
| POST | `/api/flows` | Crear flujo |
| GET / PUT / DELETE | `/api/flows/{id}` | CRUD individual |
| GET / PUT | `/api/settings` | Ver/guardar credenciales (cifradas) |
| GET | `/api/settings/providers` | Lista de proveedores y modelos |
| POST | `/api/files/upload` | Subir adjunto |
| POST | `/api/run` | Ejecutar grafo (cascada o un solo nodo) |
