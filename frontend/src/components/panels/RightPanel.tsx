import { useFlowStore } from "../../store/flow";
import AgentConfigPanel from "./AgentConfig";
import MicroserviceConfigPanel from "./MicroserviceConfig";

export default function RightPanel({ onRunNode }: { onRunNode: (id: string) => void }) {
  const selectedId = useFlowStore((s) => s.selectedNodeId);
  const node = useFlowStore((s) => s.nodes.find((n) => n.id === selectedId));

  if (!node) {
    return (
      <aside className="right-panel">
        <p style={{ color: "var(--muted)", fontSize: 13 }}>
          Select a node to configure it. Drag from the left palette to add new
          nodes.
        </p>
      </aside>
    );
  }

  return (
    <aside className="right-panel">
      <button
        className="primary"
        style={{ width: "100%", marginBottom: 16 }}
        onClick={() => onRunNode(node.id)}
      >
        ▶ Run this node
      </button>
      {node.type === "agent" ? (
        <AgentConfigPanel nodeId={node.id} />
      ) : (
        <MicroserviceConfigPanel nodeId={node.id} />
      )}
    </aside>
  );
}
