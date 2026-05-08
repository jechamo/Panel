import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AppNodeData } from "../../store/flow";

export default function MicroserviceNode({
  data,
  selected,
}: NodeProps<{ data: AppNodeData }>) {
  const d = data as unknown as AppNodeData;
  const cfg = d.config as { method: string; url: string };
  return (
    <div className={`node-card microservice ${selected ? "selected" : ""}`}>
      <Handle type="target" position={Position.Left} />
      <div className="head">
        <span>🔌</span>
        <span>{d.label || "Microservice"}</span>
      </div>
      <div className="body">
        <div>{cfg.method}</div>
        <div style={{ marginTop: 4, opacity: 0.8 }}>
          {(cfg.url || "(no url)").slice(0, 60)}
          {(cfg.url || "").length > 60 ? "…" : ""}
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
