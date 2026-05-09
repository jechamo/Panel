import { useEffect, useState } from "react";
import { api, type FlowSummary } from "../api/client";
import { useFlowStore, type AppNode } from "../store/flow";

export default function Toolbar({
  onOpenSettings,
  onRunAll,
  running,
}: {
  onOpenSettings: () => void;
  onRunAll: () => void;
  running: boolean;
}) {
  const [flows, setFlows] = useState<FlowSummary[]>([]);
  const { flowId, flowName, nodes, edges, setFlow, setFlowName } = useFlowStore();

  const refresh = () => api.listFlows().then(setFlows).catch(() => {});
  useEffect(() => {
    refresh();
  }, []);

  const save = async () => {
    const graph = { nodes, edges };
    if (flowId == null) {
      const name = prompt("Flow name", flowName) || flowName;
      const created = await api.createFlow(name, graph);
      setFlow(created.id, created.name, nodes, edges);
    } else {
      await api.updateFlow(flowId, { name: flowName, graph });
    }
    await refresh();
  };

  const load = async (id: number) => {
    if (Number.isNaN(id)) return;
    const flow = await api.getFlow(id);
    setFlow(
      flow.id,
      flow.name,
      (flow.graph?.nodes || []) as AppNode[],
      flow.graph?.edges || []
    );
  };

  const newFlow = () => {
    if (!confirm("Discard current flow?")) return;
    setFlow(null, "Untitled flow", [], []);
  };

  return (
    <header className="toolbar">
      <h1>● Panel</h1>
      <input
        style={{ width: 220 }}
        value={flowName}
        onChange={(e) => setFlowName(e.target.value)}
      />
      <select
        value={flowId ?? ""}
        onChange={(e) => load(Number(e.target.value))}
      >
        <option value="">— Load flow —</option>
        {flows.map((f) => (
          <option key={f.id} value={f.id}>
            {f.name}
          </option>
        ))}
      </select>
      <button onClick={newFlow}>New</button>
      <button onClick={save}>Save</button>
      <div className="spacer" />
      <button onClick={onOpenSettings}>⚙️ Settings</button>
      <button className="primary" onClick={onRunAll} disabled={running}>
        {running ? "Running…" : "▶ Run all"}
      </button>
    </header>
  );
}
