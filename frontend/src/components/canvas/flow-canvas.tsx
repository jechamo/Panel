import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  type NodeTypes,
} from '@xyflow/react';

import { useFlowStore } from '../../stores/flow-store';
import { WorkflowNode } from './workflow-node';

const nodeTypes: NodeTypes = {
  workflow: WorkflowNode,
};

export function FlowCanvas() {
  const { addNode, edges, nodes, onConnect, onEdgesChange, onNodesChange, selectNode } = useFlowStore();

  return (
    <div className="relative h-full min-h-[720px] overflow-hidden rounded-[36px]">
      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-center justify-between px-6 py-5">
        <div className="pointer-events-auto rounded-3xl border border-white/10 bg-black/25 px-4 py-3 backdrop-blur">
          <p className="text-xs uppercase tracking-[0.3em] text-mist/45">Canvas</p>
          <p className="mt-1 text-sm text-mist/70">
            Arrastra, conecta y haz click en un nodo para abrir su panel lateral.
          </p>
        </div>

        <div className="pointer-events-auto flex flex-wrap items-center gap-3">
          <button
            className="rounded-full border border-tide/35 bg-tide/18 px-5 py-3 text-sm font-medium text-white transition hover:bg-tide/28"
            onClick={() => addNode('agent')}
            type="button"
          >
            Anadir Agente
          </button>
          <button
            className="rounded-full border border-ember/35 bg-ember/18 px-5 py-3 text-sm font-medium text-white transition hover:bg-ember/28"
            onClick={() => addNode('microservice')}
            type="button"
          >
            Anadir Microservicio
          </button>
        </div>
      </div>

      <ReactFlow
        defaultEdgeOptions={{ animated: true }}
        edges={edges}
        fitView
        maxZoom={1.8}
        minZoom={0.3}
        nodeTypes={nodeTypes}
        nodes={nodes}
        onConnect={onConnect}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => selectNode(node.id)}
        onNodesChange={onNodesChange}
        onPaneClick={() => selectNode(null)}
        proOptions={{ hideAttribution: true }}
      >
        <MiniMap maskColor="rgba(9, 13, 19, 0.65)" nodeColor="#58c4dd" pannable zoomable />
        <Controls position="bottom-right" showInteractive={false} />
        <Background color="rgba(216, 224, 238, 0.12)" gap={28} size={1.2} variant={BackgroundVariant.Dots} />
      </ReactFlow>
    </div>
  );
}