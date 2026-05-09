# Instalación offline / aire-gap

Pasos para instalar Panel en una máquina sin acceso a internet (típico
en entornos bancarios). La idea: descargas todas las dependencias en una
máquina con red, las llevas a la máquina aislada, y haces la instalación
**sin tocar PyPI ni npmjs.org**.

## Backend (Python)

### En la máquina con red (puente)

```bash
cd Panel/backend
python3 -m pip download \
    --dest vendor \
    -e .[dev]
```

Esto deja en `Panel/backend/vendor/` todos los wheels de las dependencias
(fastapi, uvicorn, anthropic, openai, google-genai, pypdf, etc.) más los
de pytest. Nota: añade el flag `--platform`, `--python-version` y
`--abi` si la máquina destino tiene una arquitectura/versión de Python
distinta a la de la máquina puente.

### En la máquina aislada

```bash
cd Panel/backend
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --no-index --find-links=./vendor -e .[dev]
```

`--no-index` desactiva PyPI; `--find-links` apunta al directorio local.

### Alternativa: mirror interno

Si vuestro Artifactory / Nexus tiene un repo PyPI proxy:

```bash
pip config set global.index-url https://artifactory.interno/api/pypi/pypi-virtual/simple
pip install -e .[dev]
```

## Frontend (Node)

### En la máquina con red

```bash
cd Panel/frontend
npm ci                      # genera node_modules y respeta package-lock.json
tar czf node_modules.tgz node_modules
```

O usando el caché de npm:

```bash
npm ci --cache ./.npm-cache
tar czf npm-cache.tgz .npm-cache
```

### En la máquina aislada

Opción A — copiar `node_modules` directamente:

```bash
tar xzf node_modules.tgz
npm run build              # vite build, no requiere red
```

Opción B — instalar offline desde caché:

```bash
tar xzf npm-cache.tgz
npm ci --offline --cache ./.npm-cache
npm run build
```

Opción C — mirror interno (preferida):

```bash
npm config set registry https://artifactory.interno/api/npm/npm-virtual/
npm ci
```

## Proxies HTTP corporativos

Tanto pip como npm como los SDK de los proveedores LLM respetan
`HTTPS_PROXY` / `HTTP_PROXY` / `NO_PROXY`:

```bash
export HTTPS_PROXY=http://proxy.interno:3128
export HTTP_PROXY=http://proxy.interno:3128
export NO_PROXY=127.0.0.1,localhost,.interno
```

Para Windows PowerShell:

```powershell
$env:HTTPS_PROXY="http://proxy.interno:3128"
$env:HTTP_PROXY="http://proxy.interno:3128"
$env:NO_PROXY="127.0.0.1,localhost,.interno"
```

## CA corporativo / TLS interceptado

Si vuestro proxy intercepta TLS con un CA propio, tendréis que decirle a
las librerías HTTP que confíen en él:

```bash
# Para httpx (microservicio node) y requests
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/corporate-ca.pem
export SSL_CERT_FILE=/etc/ssl/certs/corporate-ca.pem

# Para npm install
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/corporate-ca.pem

# Para pip
pip config set global.cert /etc/ssl/certs/corporate-ca.pem
```

Los SDK oficiales de Anthropic / OpenAI / Google usan `httpx` por debajo,
así que `SSL_CERT_FILE` y `REQUESTS_CA_BUNDLE` los cubren.

## Verificación post-instalación

```bash
# Backend
cd backend && source .venv/bin/activate
pytest                                     # debe pasar 19/19 sin red
uvicorn app.main:app --port 8000 &
curl http://localhost:8000/api/health      # {"ok": true}
curl http://localhost:8000/api/settings/providers  # lista de 8 providers

# Frontend
cd ../frontend
npm run build                              # Vite build sin tocar red
```

## Persistencia y datos sensibles

Toda la persistencia local vive en `backend/data/`:

- `panel.db` — SQLite con flujos, settings y logs.
- `.master_key` — clave Fernet con la que se cifran las API keys.
- `uploads/` — adjuntos subidos a los nodos Agent.

Para backups:

```bash
tar czf panel-backup.tgz backend/data
```

**Importante**: si pierdes `.master_key` no podrás descifrar las API keys
guardadas — habrá que reintroducirlas. Inclúyelo en el backup.

## Lista de dependencias externas que llegan a la red

Cuando funcionando, Panel solo hace egress en estos casos:

| Disparador | Destino | Cuándo se evita |
|---|---|---|
| Provider Anthropic | `api.anthropic.com` | Si usas otro provider |
| Provider OpenAI (sin base_url) | `api.openai.com` | Configura `openai__base_url` a un gateway interno |
| Provider Gemini | `generativelanguage.googleapis.com` | Si usas otro provider |
| Provider GitHub Models / Copilot CLI | `models.github.ai` | Si usas otro provider |
| Provider OpenAI-compat | el `base_url` que configures | — |
| Provider Azure OpenAI | el `endpoint` que configures | — |
| Provider CLI subprocess | ninguno (subprocess local) | — |
| Microservicio HTTP | el endpoint del nodo | controlado por el flujo |

Recomendación bancaria: desactiva en `models.json` los proveedores que
**no** vayas a usar (deja solo los aprobados por seguridad) eliminando
sus entradas o vaciando sus `models: []`. Ver `BANKING_DEPLOYMENT.md`.
