import { useCallback } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type NodeChange,
} from "@xyflow/react";
import {
  defaultAgentConfig,
  defaultMicroserviceConfig,
  useFlowStore,
  type AppNode,
} from "../store/flow";
import AgentNode from "./nodes/AgentNode";
import MicroserviceNode from "./nodes/MicroserviceNode";

const nodeTypes = { agent: AgentNode, microservice: MicroserviceNode };

let idCounter = 1;
const newId = (type: string) => `${type}-${Date.now().toString(36)}-${idCounter++}`;

export default function Canvas() {
  const { nodes, edges, setNodes, setEdges, selectNode, addNode } = useFlowStore();

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes(applyNodeChanges(changes, nodes) as AppNode[]),
    [nodes, setNodes]
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges(applyEdgeChanges(changes, edges) as Edge[]),
    [edges, setEdges]
  );
  const onConnect = useCallback(
    (c: Connection) => setEdges(addEdge({ ...c, animated: true }, edges)),
    [edges, setEdges]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const type = e.dataTransfer.getData("application/panel-node-type") as
      | "agent"
      | "microservice";
    if (!type) return;
    const bounds = (e.target as HTMLElement).getBoundingClientRect();
    const position = { x: e.clientX - bounds.left - 100, y: e.clientY - bounds.top - 30 };
    const id = newId(type);
    const node: AppNode = {
      id,
      type,
      position,
      data: {
        label: type === "agent" ? "Agent" : "Microservice",
        config: type === "agent" ? defaultAgentConfig() : defaultMicroserviceConfig(),
        status: "idle",
      },
    };
    addNode(node);
    selectNode(id);
  };

  return (
    <div
      className="canvas"
      onDrop={onDrop}
      onDragOver={(e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, n) => selectNode(n.id)}
        onPaneClick={() => selectNode(null)}
        fitView
      >
        <Background gap={16} />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
