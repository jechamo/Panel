# Despliegue en entornos bancarios

Esta guía cubre las decisiones específicas para desplegar Panel en una
entidad financiera con una red protegida y un catálogo de herramientas
restringido.

## Matriz de proveedores LLM

| Provider | Egress | Auth | Cuándo elegirlo |
|---|---|---|---|
| `copilot_models` | `models.github.ai` (vía proxy si aplica) | `gh auth token` (CLI ya autorizada) | Defecto si la entidad ya tiene Copilot CLI aprobado y autenticado |
| `azure_openai` | `<resource>.openai.azure.com` interno | API key Azure | Si el banco tiene Azure OpenAI contratado (data residency, compliance) |
| `openai_compat` | el endpoint que configures | API key del gateway | Para Ollama/vLLM/LiteLLM internos, o un gateway corporativo OpenAI-compat |
| `cli_subprocess` | ninguno (subprocess local) | la del CLI configurado | Si tienen aprobado un CLI distinto (Claude Code, copilot agent, …) sin endpoint HTTP |
| `github_models` | `models.github.ai` | PAT pegado en Settings | Igual que copilot_models pero sin gh CLI; requiere generar un PAT con scope `models:read` |
| `anthropic` | `api.anthropic.com` | API key | Solo si la entidad permite egress a `api.anthropic.com` |
| `openai` | `api.openai.com` (o tu base_url) | API key | Solo si hay egress a OpenAI público o si pones un `base_url` interno |
| `gemini` | `generativelanguage.googleapis.com` | API key | Solo si la entidad permite egress a Google |

### Recomendación por defecto

1. **Copilot CLI** (`copilot_models`) — el banco ya tiene `gh` autorizado,
   reusa esa auth, no hay que pegar API keys nuevas.
2. **Azure OpenAI** (`azure_openai`) si hay contrato corporativo.
3. **OpenAI-compatible** apuntando a un LiteLLM o vLLM **interno** si
   queréis aislar todo el tráfico LLM dentro del datacenter.
4. **CLI subprocess** como plan B si solo está aprobado un binario sin
   API HTTP.

## Restricción de proveedores

Si quieres que la UI **solo** ofrezca los proveedores autorizados, edita
`backend/config/models.json` y quita las entradas que no quieres:

```json
{
  "providers": {
    "copilot_models": { ... },
    "azure_openai": { ... },
    "openai_compat": { ... },
    "cli_subprocess": { ... }
  }
}
```

`/api/settings/providers` se recarga en cada llamada, así que solo hay
que reiniciar el frontend (o recargar el navegador) para que el cambio
se vea.

## Flujo recomendado para approval

1. **Audit del catálogo de modelos** — sube `backend/config/models.json`
   con la lista exacta de modelos aprobados. Sin nombres "claude-3-..."
   en código fuente.
2. **Sin secretos en repo** — `.env` y `backend/data/` están en
   `.gitignore`. Las API keys solo viven cifradas (Fernet) en
   `panel.db`. El `.master_key` está fuera del repo.
3. **Logs auditables** — la tabla `node_runs` registra input/output/error
   por nodo. Endpoint de retención:

   ```bash
   curl -X DELETE 'http://localhost:8000/api/runs?older_than_days=30'
   ```

4. **Sin egress no autorizado** — ver tabla "Lista de dependencias
   externas que llegan a la red" en `OFFLINE_INSTALL.md`.

## Configuración de proxies

En la máquina donde corre el backend:

```bash
export HTTPS_PROXY=http://proxy.interno:3128
export HTTP_PROXY=http://proxy.interno:3128
export NO_PROXY=127.0.0.1,localhost,.interno

# CA corporativo
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/corp-ca.pem
export SSL_CERT_FILE=/etc/ssl/certs/corp-ca.pem
```

Los SDK oficiales (`anthropic`, `openai`, `google-genai`) y `httpx`
honran estas variables sin más cambios.

## Mensajes a recursos humanos / seguridad

> Panel es una webapp local que se ejecuta en `localhost:5173` y
> `localhost:8000`. No abre puertos públicos, no envía telemetría, no
> requiere conexión a internet salvo para llamar al/los proveedor(es)
> LLM seleccionados, que se pueden restringir a gateways internos.
> Los datos sensibles (API keys) se cifran con Fernet (AES-128 + HMAC)
> antes de persistirse. Los flujos y logs viven en SQLite local. Toda
> la auditoría queda en `backend/data/panel.db`.

## Troubleshooting bancario

### "ImportError: cannot import name 'Anthropic'"

El `pip download` de la máquina puente no era para tu plataforma. Repite
con flags explícitos:

```bash
pip download --dest vendor \
    --platform manylinux2014_x86_64 \
    --python-version 3.11 \
    --abi cp311 \
    --only-binary=:all: \
    -e .[dev]
```

### TLS handshake fallando con el provider público

Tu CA corporativo no está en el bundle por defecto. Exporta:

```bash
export SSL_CERT_FILE=/etc/ssl/certs/corp-ca.pem
```

(Los SDK Anthropic/OpenAI/Google usan `httpx` y respetan esto.)

### Copilot CLI provider falla con "gh auth token timed out"

Comprueba que `gh auth status` funciona desde el shell que arranca
uvicorn. El backend hereda el entorno del shell. Si no:

```bash
gh auth refresh -h github.com
```

### El gateway interno no acepta `response_format=json_schema`

Es un caso conocido — la versión de OpenAI API que se proxiea puede ser
antigua. El cliente cae automáticamente a `{"type": "json_object"}` y
si tampoco lo soporta, al modo prompt con validación post (Pydantic).
No requiere acción.

### Las API keys aparecen como "no configurado" tras un reinicio

Probablemente borraste `backend/data/.master_key`. Las keys cifradas con
la antigua master key no se pueden descifrar. Solución: re-introducirlas
desde Settings.
