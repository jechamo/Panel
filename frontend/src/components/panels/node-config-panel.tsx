import { AgentConfigForm } from './agent-config-form';
import { MicroserviceConfigForm } from './microservice-config-form';
import { useFlowStore } from '../../stores/flow-store';

export function NodeConfigPanel() {
  const { nodes, selectedNodeId, selectNode, updateNodeData } = useFlowStore();

  const selectedNode = selectedNodeId ? nodes.find((node) => node.id === selectedNodeId) : undefined;

  if (!selectedNode) {
    return (
      <aside className="w-full rounded-[32px] border border-white/10 bg-panel/70 p-6 shadow-glow backdrop-blur lg:max-w-[420px]">
        <div className="flex h-full min-h-[420px] flex-col justify-center rounded-[28px] border border-dashed border-white/10 bg-black/15 px-6 py-10 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-mist/45">Panel lateral</p>
          <h2 className="mt-4 text-2xl font-semibold text-white">Selecciona un nodo</h2>
          <p className="mt-3 text-sm leading-6 text-mist/62">
            Haz click en un nodo del canvas para editar prompts, modelo, headers, payload y campos de salida.
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-full rounded-[32px] border border-white/10 bg-panel/70 p-6 shadow-glow backdrop-blur lg:max-w-[420px]">
      <div className="mb-6 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-mist/45">Configuracion de nodo</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">{selectedNode.data.title}</h2>
          <p className="mt-2 text-sm leading-6 text-mist/62">{selectedNode.data.description}</p>
        </div>

        <button
          className="rounded-full border border-white/10 px-3 py-2 text-xs uppercase tracking-[0.2em] text-mist/62 transition hover:border-white/20 hover:text-white"
          onClick={() => selectNode(null)}
          type="button"
        >
          Cerrar
        </button>
      </div>

      <div className="max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
        {selectedNode.data.kind === 'agent' ? (
          <AgentConfigForm
            node={selectedNode.data}
            onChange={(nextNode) => updateNodeData(selectedNode.id, () => nextNode)}
          />
        ) : (
          <MicroserviceConfigForm
            node={selectedNode.data}
            onChange={(nextNode) => updateNodeData(selectedNode.id, () => nextNode)}
          />
        )}
      </div>
    </aside>
  );
}