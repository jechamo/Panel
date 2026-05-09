import { useEffect, useState } from "react";
import { api, type Variable } from "../../api/client";
import { useFlowStore } from "../../store/flow";

/**
 * Tracks the last textarea/input the user focused inside this panel,
 * so click-to-insert knows where to insert the placeholder.
 */
let lastFocused: HTMLTextAreaElement | HTMLInputElement | null = null;
let lastInsertHandler:
  | ((text: string, el: HTMLTextAreaElement | HTMLInputElement) => void)
  | null = null;

export function buildInsertedValue(
  el: HTMLTextAreaElement | HTMLInputElement,
  text: string
) {
  const start = el.selectionStart ?? el.value.length;
  const end = el.selectionEnd ?? el.value.length;
  return {
    nextValue: el.value.slice(0, start) + text + el.value.slice(end),
    nextCaret: start + text.length,
  };
}

export function trackFocus(
  el: HTMLTextAreaElement | HTMLInputElement,
  onInsert?: (text: string, el: HTMLTextAreaElement | HTMLInputElement) => void
) {
  lastFocused = el;
  lastInsertHandler = onInsert ?? null;
}

export function insertPlaceholder(text: string) {
  const el = lastFocused;
  if (!el) {
    navigator.clipboard?.writeText(text).catch(() => {});
    return;
  }
  if (lastInsertHandler) {
    lastInsertHandler(text, el);
    return;
  }
  const { nextValue, nextCaret } = buildInsertedValue(el, text);
  el.value = nextValue;
  el.selectionStart = el.selectionEnd = nextCaret;
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.focus();
}

export async function loadVariablesForNode(nodeId: string): Promise<Variable[]> {
  const { nodes, edges } = useFlowStore.getState();
  const last_outputs: Record<string, any> = {};
  for (const n of nodes) {
    if (n.data.output !== undefined) last_outputs[n.id] = n.data.output;
  }
  const slimNodes = nodes.map((n) => ({
    id: n.id,
    type: n.type,
    data: { config: n.data.config },
  }));
  const slimEdges = edges.map((e) => ({ source: e.source, target: e.target }));
  const { variables } = await api.variables(slimNodes, slimEdges, last_outputs, nodeId);
  return variables;
}

export default function VariablesPicker({ nodeId }: { nodeId: string }) {
  const [vars, setVars] = useState<Variable[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      setVars(await loadVariablesForNode(nodeId));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) refresh();
  }, [open, nodeId]);

  const groups = vars.reduce<Record<string, Variable[]>>((acc, v) => {
    const root = v.path.split(".")[0];
    (acc[root] ??= []).push(v);
    return acc;
  }, {});

  return (
    <div className="field">
      <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
        Variables disponibles
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
        <div className="json-view" style={{ maxHeight: 220 }}>
          {loading && <div style={{ color: "var(--muted)" }}>Cargando…</div>}
          {!loading && vars.length === 0 && (
            <div style={{ color: "var(--muted)" }}>
              Sin predecesores. Conecta este nodo a otro y vuelve a abrir.
            </div>
          )}
          {Object.entries(groups).map(([root, items]) => (
            <div key={root} style={{ marginBottom: 8 }}>
              <div style={{ color: "var(--accent)", marginBottom: 4 }}>{root}</div>
              {items.map((v) => (
                <div
                  key={v.path}
                  onClick={() => insertPlaceholder(v.placeholder)}
                  title={v.sample || `source: ${v.source}`}
                  style={{
                    cursor: "pointer",
                    padding: "2px 4px",
                    borderRadius: 3,
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 8,
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = "var(--border)")
                  }
                  onMouseLeave={(e) => (e.currentTarget.style.background = "")}
                >
                  <span>{v.placeholder}</span>
                  <span style={{ color: "var(--muted)", fontSize: 10 }}>
                    {v.source}
                    {v.sample ? ` · ${v.sample}` : ""}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
