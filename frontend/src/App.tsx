import { useState } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { api, type RunResult } from "./api/client";
import Canvas from "./components/Canvas";
import Sidebar from "./components/Sidebar";
import Toolbar from "./components/Toolbar";
import RightPanel from "./components/panels/RightPanel";
import SettingsModal from "./components/panels/Settings";
import { useFlowStore } from "./store/flow";

export default function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [running, setRunning] = useState(false);

  const applyResults = (results: RunResult[]) => {
    const update = useFlowStore.getState().updateNodeData;
    for (const r of results) {
      update(r.node_id, {
        status: r.status,
        output: r.output,
        error: r.error,
        duration_ms: r.duration_ms,
      });
    }
  };

  const buildGraphPayload = () => {
    const { nodes, edges } = useFlowStore.getState();
    const last_outputs: Record<string, any> = {};
    for (const n of nodes) {
      if (n.data.status === "ok" && n.data.output !== undefined) {
        last_outputs[n.id] = n.data.output;
      }
    }
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        data: { config: n.data.config },
      })),
      edges: edges.map((e) => ({ source: e.source, target: e.target })),
      last_outputs,
    };
  };

  const runAll = async () => {
    setRunning(true);
    try {
      const { nodes } = useFlowStore.getState();
      nodes.forEach((n) =>
        useFlowStore.getState().updateNodeData(n.id, { status: "running" })
      );
      const { results } = await api.run(buildGraphPayload());
      applyResults(results);
    } catch (e: any) {
      alert("Run failed: " + e.message);
    } finally {
      setRunning(false);
    }
  };

  const runNode = async (nodeId: string) => {
    setRunning(true);
    try {
      useFlowStore.getState().updateNodeData(nodeId, { status: "running" });
      const { results } = await api.run(buildGraphPayload(), nodeId);
      applyResults(results);
    } catch (e: any) {
      alert("Run failed: " + e.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <ReactFlowProvider>
      <div className="app">
        <Toolbar
          onOpenSettings={() => setSettingsOpen(true)}
          onRunAll={runAll}
          running={running}
        />
        <Sidebar />
        <Canvas />
        <RightPanel onRunNode={runNode} />
        {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} />}
      </div>
    </ReactFlowProvider>
  );
}
