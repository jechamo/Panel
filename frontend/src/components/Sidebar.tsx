export default function Sidebar() {
  const onDragStart = (e: React.DragEvent, type: string) => {
    e.dataTransfer.setData("application/panel-node-type", type);
    e.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside className="sidebar">
      <h3>Drag to canvas</h3>
      <div
        className="palette-item"
        draggable
        onDragStart={(e) => onDragStart(e, "agent")}
      >
        🤖 Agent
      </div>
      <div
        className="palette-item microservice"
        draggable
        onDragStart={(e) => onDragStart(e, "microservice")}
      >
        🔌 Microservice
      </div>
      <h3 style={{ marginTop: 24 }}>Tips</h3>
      <p style={{ fontSize: 12, color: "var(--muted)", lineHeight: 1.5 }}>
        Connect nodes by dragging from the right handle to the left handle of
        another node. Reference upstream output in any text field with{" "}
        <code>{"{{node_id.field}}"}</code>.
      </p>
    </aside>
  );
}
