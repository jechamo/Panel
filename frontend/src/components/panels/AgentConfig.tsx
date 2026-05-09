import { useEffect, useRef, useState } from "react";
import { api, type ProviderSpec, type Variable } from "../../api/client";
import { useFlowStore, type AgentConfig as AC } from "../../store/flow";
import RunLogs from "./RunLogs";
import VariablesPicker, {
  buildInsertedValue,
  insertPlaceholder,
  loadVariablesForNode,
  trackFocus,
} from "./VariablesPicker";

export default function AgentConfigPanel({ nodeId }: { nodeId: string }) {
  const node = useFlowStore((s) => s.nodes.find((n) => n.id === nodeId));
  const update = useFlowStore((s) => s.updateNodeConfig);
  const updateData = useFlowStore((s) => s.updateNodeData);
  const removeNode = useFlowStore((s) => s.removeNode);
  const [providers, setProviders] = useState<Record<string, ProviderSpec>>({});
  const [variables, setVariables] = useState<Variable[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [promptSuggestions, setPromptSuggestions] = useState<Variable[]>([]);
  const [activePromptSuggestion, setActivePromptSuggestion] = useState(0);
  const userPromptRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    api.getProviders().then(setProviders).catch(() => {});
  }, []);

  useEffect(() => {
    refreshVariables(nodeId, setVariables);
  }, [nodeId]);

  if (!node) return null;
  const cfg = node.data.config as AC;
  const providerModels = providers[cfg.provider]?.models || [];
  const selectedModel = providerModels.includes(cfg.model)
    ? cfg.model
    : providerModels[0] || cfg.model;

  const handleFile = async (file: File) => {
    const meta = await api.uploadFile(file);
    update(nodeId, {
      attachments: [...cfg.attachments, { name: meta.name, path: meta.path }],
    });
  };

  const setProvider = (provider: string) => {
    const spec = providers[provider];
    update(nodeId, {
      provider,
      model: spec?.default_model || cfg.model,
    });
  };

  const suggestions = variables.slice(0, 8);

  const syncPromptSuggestions = (value: string, caret: number, source = variables) => {
    const nextSuggestions = getPromptSuggestions(value, caret, source);
    setPromptSuggestions(nextSuggestions);
    setActivePromptSuggestion(0);
  };

  const applyPromptSuggestion = (placeholder: string) => {
    const el = userPromptRef.current;
    if (!el) return;
    const { nextValue, nextCaret } = applyPromptPlaceholder(el.value, el.selectionStart, placeholder);
    update(nodeId, { user_prompt: nextValue });
    setPromptSuggestions([]);
    queueMicrotask(() => {
      el.focus();
      el.selectionStart = el.selectionEnd = nextCaret;
    });
  };

  return (
    <div>
      <h2>🤖 Agent</h2>

      <div className="field">
        <label style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Name</span>
          <button
            type="button"
            style={{ padding: "1px 8px", fontSize: 10 }}
            onClick={() => navigator.clipboard?.writeText(nodeId)}
            title={`Copy node id: ${nodeId}`}
          >
            Copy id ({nodeId})
          </button>
        </label>
        <input
          value={node.data.label}
          onChange={(e) => updateData(nodeId, { label: e.target.value })}
        />
      </div>

      <div className="row">
        <div className="field">
          <label>Provider</label>
          <select value={cfg.provider} onChange={(e) => setProvider(e.target.value)}>
            {Object.entries(providers).map(([k, v]) => (
              <option key={k} value={k}>
                {v.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Model</label>
          <select value={selectedModel} onChange={(e) => update(nodeId, { model: e.target.value })}>
            {providerModels.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </div>

      <VariablesPicker nodeId={nodeId} />

      {suggestions.length > 0 && (
        <div className="field">
          <label style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
            <span>Sugerencias de entradas previas</span>
            <button
              type="button"
              style={{ padding: "1px 8px", fontSize: 10 }}
              onClick={() => setShowSuggestions((value) => !value)}
            >
              {showSuggestions ? "Ocultar" : "Mostrar"}
            </button>
          </label>
          {showSuggestions && (
            <>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {suggestions.map((v) => (
                  <button
                    key={v.placeholder}
                    type="button"
                    title={v.sample || v.source}
                    onClick={() => insertPlaceholder(v.placeholder)}
                    style={{
                      padding: "4px 8px",
                      fontSize: 11,
                      borderRadius: 999,
                      border: "1px solid var(--border)",
                      background: "transparent",
                      color: "var(--text)",
                      cursor: "pointer",
                    }}
                  >
                    {v.placeholder}
                    {v.sample ? ` · ${v.sample}` : ""}
                  </button>
                ))}
              </div>
              <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 6 }}>
                Pulsa una sugerencia para insertarla en el campo con foco. Si un API previo devolvio
                {" "}
                <code>{'{"fact":"...","length":61}'}</code>, aqui veras placeholders como
                {" "}
                <code>{"{{api-node.fact}}"}</code>
                {" "}y
                {" "}
                <code>{"{{api-node.length}}"}</code>.
              </div>
            </>
          )}
        </div>
      )}

      <div className="field">
        <label>System prompt</label>
        <textarea
          value={cfg.system_prompt}
          onFocus={(e) =>
            trackFocus(e.currentTarget, (text, el) => {
              const { nextValue, nextCaret } = buildInsertedValue(el, text);
              update(nodeId, { system_prompt: nextValue });
              queueMicrotask(() => {
                el.focus();
                el.selectionStart = el.selectionEnd = nextCaret;
              });
            })
          }
          onChange={(e) => update(nodeId, { system_prompt: e.target.value })}
        />
      </div>

      <div className="field">
        <label>User prompt</label>
        <textarea
          ref={userPromptRef}
          rows={6}
          value={cfg.user_prompt}
          onFocus={(e) => {
            trackFocus(e.currentTarget, (text, el) => {
              const { nextValue, nextCaret } = buildInsertedValue(el, text);
              update(nodeId, { user_prompt: nextValue });
              queueMicrotask(() => {
                el.focus();
                el.selectionStart = el.selectionEnd = nextCaret;
              });
            });
            refreshVariables(nodeId, setVariables)
              .then((vars) =>
                syncPromptSuggestions(
                  e.currentTarget.value,
                  e.currentTarget.selectionStart ?? e.currentTarget.value.length,
                  vars
                )
              )
              .catch(() => {});
          }}
          onClick={(e) =>
            syncPromptSuggestions(
              e.currentTarget.value,
              e.currentTarget.selectionStart ?? e.currentTarget.value.length
            )
          }
          onKeyDown={(e) => {
            if (promptSuggestions.length === 0) return;
            if (e.key === "ArrowDown") {
              e.preventDefault();
              setActivePromptSuggestion((index) => (index + 1) % promptSuggestions.length);
              return;
            }
            if (e.key === "ArrowUp") {
              e.preventDefault();
              setActivePromptSuggestion(
                (index) => (index - 1 + promptSuggestions.length) % promptSuggestions.length
              );
              return;
            }
            if (e.key === "Enter" || e.key === "Tab") {
              e.preventDefault();
              applyPromptSuggestion(promptSuggestions[activePromptSuggestion].placeholder);
              return;
            }
            if (e.key === "Escape") {
              setPromptSuggestions([]);
            }
          }}
          onChange={(e) => {
            update(nodeId, { user_prompt: e.target.value });
            syncPromptSuggestions(
              e.target.value,
              e.target.selectionStart ?? e.target.value.length
            );
          }}
          placeholder="Reference upstream nodes with {{nodeId.fieldName}}"
        />
        {promptSuggestions.length > 0 && (
          <div
            className="json-view"
            style={{ marginTop: 8, maxHeight: 220, overflowY: "auto" }}
          >
            {promptSuggestions.map((v, index) => (
              <button
                key={v.placeholder}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => applyPromptSuggestion(v.placeholder)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "6px 8px",
                  border: "0",
                  borderRadius: 4,
                  background:
                    index === activePromptSuggestion ? "var(--border)" : "transparent",
                  color: "var(--text)",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 8,
                }}
                title={v.sample || v.source}
              >
                <span>{v.placeholder}</span>
                <span style={{ color: "var(--muted)", fontSize: 10 }}>
                  {v.source}
                  {v.sample ? ` · ${v.sample}` : ""}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="field attachments">
        <label>Attachments (PDF / DOCX / XLSX / TXT)</label>
        {cfg.attachments.map((a, i) => (
          <div key={i} className="att-row">
            <span>📎 {a.name}</span>
            <button
              className="danger"
              onClick={() =>
                update(nodeId, {
                  attachments: cfg.attachments.filter((_, j) => j !== i),
                })
              }
            >
              Remove
            </button>
          </div>
        ))}
        <input
          type="file"
          accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.md,.csv,.json"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
            e.target.value = "";
          }}
        />
      </div>

      <div className="field output-fields">
        <label>Output JSON fields</label>
        {cfg.output_fields.map((f, i) => (
          <div key={i} className="of-row">
            <input
              placeholder="name"
              value={f.name}
              onChange={(e) => {
                const next = [...cfg.output_fields];
                next[i] = { ...next[i], name: e.target.value };
                update(nodeId, { output_fields: next });
              }}
            />
            <input
              placeholder="description"
              value={f.description}
              onChange={(e) => {
                const next = [...cfg.output_fields];
                next[i] = { ...next[i], description: e.target.value };
                update(nodeId, { output_fields: next });
              }}
            />
            <button
              className="danger"
              onClick={() =>
                update(nodeId, {
                  output_fields: cfg.output_fields.filter((_, j) => j !== i),
                })
              }
            >
              ✕
            </button>
          </div>
        ))}
        <button
          onClick={() =>
            update(nodeId, {
              output_fields: [...cfg.output_fields, { name: "", description: "" }],
            })
          }
        >
          + Add field
        </button>
      </div>

      <NodeOutput nodeId={nodeId} />

      <RunLogs nodeId={nodeId} />

      <div style={{ marginTop: 16 }}>
        <button className="danger" onClick={() => removeNode(nodeId)}>
          Delete node
        </button>
      </div>
    </div>
  );
}

function NodeOutput({ nodeId }: { nodeId: string }) {
  const node = useFlowStore((s) => s.nodes.find((n) => n.id === nodeId));
  if (!node || node.data.status === "idle") return null;
  return (
    <div className="field">
      <label>Last result · {node.data.status}</label>
      {node.data.error && (
        <div style={{ color: "var(--err)", fontSize: 12 }}>{node.data.error}</div>
      )}
      {node.data.output !== undefined && (
        <pre className="json-view">{JSON.stringify(node.data.output, null, 2)}</pre>
      )}
    </div>
  );
}

async function refreshVariables(
  nodeId: string,
  setVariables: (vars: Variable[]) => void
): Promise<Variable[]> {
  try {
    const vars = await loadVariablesForNode(nodeId);
    setVariables(vars);
    return vars;
  } catch {
    setVariables([]);
    return [];
  }
}

function getPromptSuggestions(value: string, caret: number, variables: Variable[]) {
  const match = getPromptAutocompleteMatch(value, caret);
  if (!match) return [];
  const query = match.query.toLowerCase();
  return variables
    .filter((item) => {
      if (!query) return true;
      const placeholderText = item.placeholder.slice(2, -2).toLowerCase();
      return placeholderText.includes(query) || item.path.toLowerCase().includes(query);
    })
    .slice(0, 8);
}

function applyPromptPlaceholder(value: string, caret: number | null, placeholder: string) {
  const safeCaret = caret ?? value.length;
  const match = getPromptAutocompleteMatch(value, safeCaret);
  if (!match) {
    return {
      nextValue: value + placeholder,
      nextCaret: value.length + placeholder.length,
    };
  }
  return {
    nextValue: value.slice(0, match.start) + placeholder + value.slice(match.end),
    nextCaret: match.start + placeholder.length,
  };
}

function getPromptAutocompleteMatch(value: string, caret: number) {
  const beforeCaret = value.slice(0, caret);
  const start = beforeCaret.lastIndexOf("{{");
  if (start === -1) return null;
  const close = beforeCaret.lastIndexOf("}}");
  if (close > start) return null;
  const query = value.slice(start + 2, caret);
  if (/\{|\}|\n|\r/.test(query)) return null;

  let end = caret;
  while (end < value.length && !/[\s{}]/.test(value[end])) end += 1;
  if (value.slice(end, end + 2) === "}}") end += 2;

  return { start, end, query };
}
