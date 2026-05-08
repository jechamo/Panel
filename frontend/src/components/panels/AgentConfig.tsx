import { useEffect, useState } from "react";
import { api, type ProviderSpec } from "../../api/client";
import { useFlowStore, type AgentConfig as AC } from "../../store/flow";

export default function AgentConfigPanel({ nodeId }: { nodeId: string }) {
  const node = useFlowStore((s) => s.nodes.find((n) => n.id === nodeId));
  const update = useFlowStore((s) => s.updateNodeConfig);
  const updateData = useFlowStore((s) => s.updateNodeData);
  const removeNode = useFlowStore((s) => s.removeNode);
  const [providers, setProviders] = useState<Record<string, ProviderSpec>>({});

  useEffect(() => {
    api.getProviders().then(setProviders).catch(() => {});
  }, []);

  if (!node) return null;
  const cfg = node.data.config as AC;

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

  return (
    <div>
      <h2>🤖 Agent</h2>

      <div className="field">
        <label>Name</label>
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
          <select
            value={cfg.model}
            onChange={(e) => update(nodeId, { model: e.target.value })}
          >
            {(providers[cfg.provider]?.models || [cfg.model]).map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field">
        <label>System prompt</label>
        <textarea
          value={cfg.system_prompt}
          onChange={(e) => update(nodeId, { system_prompt: e.target.value })}
        />
      </div>

      <div className="field">
        <label>User prompt</label>
        <textarea
          rows={6}
          value={cfg.user_prompt}
          onChange={(e) => update(nodeId, { user_prompt: e.target.value })}
          placeholder="Reference upstream nodes with {{nodeId.fieldName}}"
        />
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
