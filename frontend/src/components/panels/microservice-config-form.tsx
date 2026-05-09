import { runMicroserviceNode } from '../../lib/api';
import { JsonViewer } from '../ui/json-viewer';
import { useFlowStore } from '../../stores/flow-store';
import { useToastStore } from '../../stores/toast-store';
import type { MicroserviceNodeData } from '../../lib/types';

const httpMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] as const;

type MicroserviceConfigFormProps = {
    nodeId: string;
    node: MicroserviceNodeData;
    onChange: (nextNode: MicroserviceNodeData) => void;
};

export function MicroserviceConfigForm({ node, nodeId, onChange }: MicroserviceConfigFormProps) {
    const { config } = node;
    const currentFlowId = useFlowStore((state) => state.currentFlowId);
    const setNodeRuntimeState = useFlowStore((state) => state.setNodeRuntimeState);
    const pushToast = useToastStore((state) => state.pushToast);

    const updateConfig = (nextConfig: MicroserviceNodeData['config']) => {
        onChange({
            ...node,
            config: nextConfig,
        });
    };

    const handleRun = async () => {
        setNodeRuntimeState(nodeId, 'running', null, null);

        try {
            const result = await runMicroserviceNode(nodeId, config, {
                flowId: currentFlowId,
            });
            setNodeRuntimeState(nodeId, 'success', result.output, null);
            pushToast('Nodo Microservicio ejecutado correctamente.', 'success');
        }
        catch (error) {
            const nextMessage = error instanceof Error ? error.message : 'No se pudo ejecutar el microservicio.';
            setNodeRuntimeState(
                nodeId,
                'error',
                null,
                nextMessage,
            );
            pushToast(nextMessage, 'error');
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <button
                    className="rounded-full border border-ember/35 bg-ember/18 px-4 py-2 text-sm font-medium text-white transition hover:bg-ember/28"
                    onClick={() => void handleRun()}
                    type="button"
                >
                    {node.status === 'running' ? 'Ejecutando...' : 'Run'}
                </button>
                <span className="text-xs uppercase tracking-[0.24em] text-mist/45">Estado: {node.status}</span>
            </div>

            <section className="space-y-3">
                <div>
                    <label className="text-xs uppercase tracking-[0.24em] text-mist/45">Endpoint</label>
                    <input
                        className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-ember/60"
                        onChange={(event) => updateConfig({ ...config, endpoint: event.target.value })}
                        placeholder="https://api.example.com/resource"
                        value={config.endpoint}
                    />
                </div>

                <div>
                    <label className="text-xs uppercase tracking-[0.24em] text-mist/45">Metodo</label>
                    <select
                        className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-ember/60"
                        onChange={(event) =>
                            updateConfig({
                                ...config,
                                method: event.target.value as MicroserviceNodeData['config']['method'],
                            })
                        }
                        value={config.method}
                    >
                        {httpMethods.map((method) => (
                            <option key={method} value={method}>
                                {method}
                            </option>
                        ))}
                    </select>
                </div>
            </section>

            <section className="space-y-3 rounded-[28px] border border-white/8 bg-black/15 p-4">
                <div className="flex items-center justify-between gap-3">
                    <div>
                        <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Headers</p>
                        <p className="mt-1 text-sm text-mist/62">Lista dinamica de claves y valores para la request.</p>
                    </div>

                    <button
                        className="rounded-full border border-ember/35 bg-ember/15 px-4 py-2 text-sm text-white transition hover:bg-ember/25"
                        onClick={() =>
                            updateConfig({
                                ...config,
                                headers: [...config.headers, { id: crypto.randomUUID(), key: '', value: '' }],
                            })
                        }
                        type="button"
                    >
                        Anadir header
                    </button>
                </div>

                <div className="space-y-3">
                    {config.headers.map((header, index) => (
                        <div key={header.id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                            <div className="mb-3 flex items-center justify-between gap-3">
                                <span className="text-xs uppercase tracking-[0.24em] text-mist/45">Header {index + 1}</span>
                                <button
                                    className="rounded-full border border-white/10 px-3 py-1 text-xs text-mist/68 transition hover:border-ember/35 hover:text-ember"
                                    onClick={() =>
                                        updateConfig({
                                            ...config,
                                            headers: config.headers.filter((item) => item.id !== header.id),
                                        })
                                    }
                                    type="button"
                                >
                                    Eliminar
                                </button>
                            </div>

                            <div className="grid gap-3 sm:grid-cols-2">
                                <input
                                    className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-ember/60"
                                    onChange={(event) =>
                                        updateConfig({
                                            ...config,
                                            headers: config.headers.map((item) =>
                                                item.id === header.id ? { ...item, key: event.target.value } : item,
                                            ),
                                        })
                                    }
                                    placeholder="Authorization"
                                    value={header.key}
                                />
                                <input
                                    className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-ember/60"
                                    onChange={(event) =>
                                        updateConfig({
                                            ...config,
                                            headers: config.headers.map((item) =>
                                                item.id === header.id ? { ...item, value: event.target.value } : item,
                                            ),
                                        })
                                    }
                                    placeholder="Bearer ..."
                                    value={header.value}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <section className="space-y-3">
                <div>
                    <label className="text-xs uppercase tracking-[0.24em] text-mist/45">Payload JSON</label>
                    <textarea
                        className="mt-2 min-h-48 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 font-mono text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-ember/60"
                        onChange={(event) => updateConfig({ ...config, payload: event.target.value })}
                        placeholder={'{\n  "foo": "{{input.bar}}"\n}'}
                        value={config.payload}
                    />
                </div>
            </section>

            {node.lastError ? (
                <section className="rounded-[28px] border border-ember/20 bg-ember/10 p-4">
                    <p className="text-xs uppercase tracking-[0.24em] text-ember/75">Error</p>
                    <p className="mt-2 text-sm leading-6 text-ember">{node.lastError}</p>
                </section>
            ) : null}

            {node.output ? (
                <section className="space-y-3 rounded-[28px] border border-moss/20 bg-moss/10 p-4">
                    <div>
                        <p className="text-xs uppercase tracking-[0.24em] text-moss/80">Output</p>
                        <p className="mt-1 text-sm text-mist/70">Respuesta JSON del microservicio.</p>
                    </div>

                    <JsonViewer data={node.output} title="Salida del microservicio" />
                </section>
            ) : null}
        </div>
    );
}