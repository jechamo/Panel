import { useEffect, useState } from "react";
import { api, type NodeRunLog } from "../../api/client";

export default function RunLogs({ nodeId }: { nodeId: string }) {
  const [open, setOpen] = useState(false);
  const [runs, setRuns] = useState<NodeRunLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      setRuns(await api.listRuns(nodeId, 10));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) refresh();
  }, [open, nodeId]);

  return (
    <div className="field">
      <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
        Run history
        <button
          type="button"
          style={{ padding: "2px 8px", fontSize: 11 }}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "Ocultar" : "Mostrar"}
        </button>
        {open && (
          <button
            type="button"
            style={{ padding: "2px 8px", fontSize: 11 }}
            onClick={refresh}
          >
            ↻
          </button>
        )}
      </label>
      {open && (
        <div className="json-view" style={{ maxHeight: 280 }}>
          {loading && <div style={{ color: "var(--muted)" }}>Cargando…</div>}
          {!loading && runs.length === 0 && (
            <div style={{ color: "var(--muted)" }}>
              Sin ejecuciones registradas todavía.
            </div>
          )}
          {runs.map((r) => (
            <div
              key={r.id}
              style={{
                marginBottom: 6,
                paddingBottom: 4,
                borderBottom: "1px solid var(--border)",
              }}
            >
              <div
                onClick={() => setExpandedId(expandedId === r.id ? null : r.id)}
                style={{
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 8,
                }}
              >
                <span
                  className={
                    r.status === "ok"
                      ? "status ok"
                      : r.status === "error"
                      ? "status error"
                      : "status skipped"
                  }
                  style={{ padding: 0, border: 0 }}
                >
                  {r.status.toUpperCase()}
                </span>
                <span style={{ color: "var(--muted)", fontSize: 10 }}>
                  {new Date(r.started_at).toLocaleString()} · {r.duration_ms} ms
                </span>
              </div>
              {expandedId === r.id && (
                <div style={{ marginTop: 4 }}>
                  {r.error && (
                    <div style={{ color: "var(--err)", fontSize: 11 }}>
                      {r.error}
                    </div>
                  )}
                  {r.input !== undefined && r.input !== null && (
                    <details style={{ marginTop: 4 }}>
                      <summary>input</summary>
                      <pre style={{ margin: 0, fontSize: 10 }}>
                        {JSON.stringify(r.input, null, 2)}
                      </pre>
                    </details>
                  )}
                  {r.output !== undefined && r.output !== null && (
                    <details style={{ marginTop: 4 }}>
                      <summary>output</summary>
                      <pre style={{ margin: 0, fontSize: 10 }}>
                        {JSON.stringify(r.output, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
