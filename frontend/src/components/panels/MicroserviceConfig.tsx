import { useFlowStore, type MicroserviceConfig as MC } from "../../store/flow";
import RunLogs from "./RunLogs";
import VariablesPicker, { trackFocus } from "./VariablesPicker";

const METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"] as const;

export default function MicroserviceConfigPanel({ nodeId }: { nodeId: string }) {
  const node = useFlowStore((s) => s.nodes.find((n) => n.id === nodeId));
  const update = useFlowStore((s) => s.updateNodeConfig);
  const updateData = useFlowStore((s) => s.updateNodeData);
  const removeNode = useFlowStore((s) => s.removeNode);
  if (!node) return null;
  const cfg = node.data.config as MC;

  return (
    <div>
      <h2>🔌 Microservice</h2>

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
        <div className="field" style={{ flex: 0, minWidth: 100 }}>
          <label>Method</label>
          <select
            value={cfg.method}
            onChange={(e) => update(nodeId, { method: e.target.value })}
          >
            {METHODS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div className="field" style={{ flex: 1 }}>
          <label>URL</label>
          <input
            value={cfg.url}
            onFocus={(e) => trackFocus(e.currentTarget)}
            onChange={(e) => update(nodeId, { url: e.target.value })}
            placeholder="https://api.example.com/v1/items"
          />
        </div>
      </div>

      <VariablesPicker nodeId={nodeId} />

      <div className="field headers">
        <label>Headers</label>
        {cfg.headers.map((h, i) => (
          <div key={i} className="h-row">
            <input
              placeholder="Header"
              value={h.key}
              onChange={(e) => {
                const next = [...cfg.headers];
                next[i] = { ...next[i], key: e.target.value };
                update(nodeId, { headers: next });
              }}
            />
            <input
              placeholder="Value"
              value={h.value}
              onChange={(e) => {
                const next = [...cfg.headers];
                next[i] = { ...next[i], value: e.target.value };
                update(nodeId, { headers: next });
              }}
            />
            <button
              className="danger"
              onClick={() =>
                update(nodeId, {
                  headers: cfg.headers.filter((_, j) => j !== i),
                })
              }
            >
              ✕
            </button>
          </div>
        ))}
        <button
          onClick={() =>
            update(nodeId, { headers: [...cfg.headers, { key: "", value: "" }] })
          }
        >
          + Add header
        </button>
      </div>

      {cfg.method !== "GET" && cfg.method !== "DELETE" && (
        <div className="field">
          <label>Body</label>
          <textarea
            rows={6}
            value={cfg.body}
            onFocus={(e) => trackFocus(e.currentTarget)}
            onChange={(e) => update(nodeId, { body: e.target.value })}
            placeholder='{"key": "{{upstream.value}}"}'
          />
        </div>
      )}

      <div className="field">
        <label>Timeout (s)</label>
        <input
          type="number"
          value={cfg.timeout_seconds}
          onChange={(e) =>
            update(nodeId, { timeout_seconds: Number(e.target.value) || 30 })
          }
        />
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
