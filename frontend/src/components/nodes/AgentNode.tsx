import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import type { AppNodeData } from "../../store/flow";

type AgentN = Node<AppNodeData, "agent">;

export default function AgentNode({ data, selected }: NodeProps<AgentN>) {
  const d = data;
  const cfg = d.config as { provider: string; model: string; user_prompt: string };
  return (
    <div className={`node-card agent ${selected ? "selected" : ""}`}>
      <Handle type="target" position={Position.Left} />
      <div className="head">
        <span>🤖</span>
        <span>{d.label || "Agent"}</span>
      </div>
      <div className="body">
        <div>{cfg.provider} · {cfg.model}</div>
        <div style={{ marginTop: 4, opacity: 0.8 }}>
          {(cfg.user_prompt || "(no prompt)").slice(0, 80)}
          {(cfg.user_prompt || "").length > 80 ? "…" : ""}
        </div>
      </div>
      {d.status !== "idle" && (
        <div className={`status ${d.status}`}>
          <span>{d.status.toUpperCase()}</span>
          {d.duration_ms != null && <span>{d.duration_ms} ms</span>}
        </div>
      )}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
