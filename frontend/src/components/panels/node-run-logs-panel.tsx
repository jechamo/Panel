import { useEffect } from 'react';

import type { NodeRunLog } from '../../lib/types';
import { getNodeRunsKey, useNodeRunsStore } from '../../stores/node-runs-store';
import { JsonViewer } from '../ui/json-viewer';

type NodeRunLogsPanelProps = {
    flowId: string | null;
    lastError: string | null;
    nodeId: string;
    nodeStatus: string;
    outputSignature: string;
};

export function NodeRunLogsPanel({
    flowId,
    lastError,
    nodeId,
    nodeStatus,
    outputSignature,
}: NodeRunLogsPanelProps) {
    const error = useNodeRunsStore((state) => state.error);
    const isLoading = useNodeRunsStore((state) => state.isLoading);
    const loadNodeRuns = useNodeRunsStore((state) => state.loadNodeRuns);
    const logs = useNodeRunsStore((state) => state.logsByNode[getNodeRunsKey(nodeId, flowId)] ?? []);

    useEffect(() => {
        if (!flowId) {
            return;
        }

        void loadNodeRuns(nodeId, flowId);
    }, [flowId, lastError, loadNodeRuns, nodeId, nodeStatus, outputSignature]);

    return (
        <section className="space-y-3 rounded-[28px] border border-white/8 bg-black/15 p-4">
            <div className="flex items-center justify-between gap-3">
                <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Logs del nodo</p>
                    <p className="mt-1 text-sm text-mist/62">Input, output, timestamps y errores de las ultimas ejecuciones.</p>
                </div>
                {isLoading ? <span className="text-xs uppercase tracking-[0.18em] text-mist/45">Cargando</span> : null}
            </div>

            {!flowId ? (
                <div className="rounded-2xl border border-dashed border-white/10 px-4 py-5 text-sm text-mist/50">
                    Guarda el flujo para persistir y consultar logs del nodo.
                </div>
            ) : error ? (
                <div className="rounded-2xl border border-ember/20 bg-ember/10 px-4 py-4 text-sm text-ember">{error}</div>
            ) : logs.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-white/10 px-4 py-5 text-sm text-mist/50">
                    No hay ejecuciones registradas aun para este nodo.
                </div>
            ) : (
                <div className="space-y-3">
                    {logs.map((log) => (
                        <RunLogCard key={log.id} log={log} />
                    ))}
                </div>
            )}
        </section>
    );
}

function RunLogCard({ log }: { log: NodeRunLog }) {
    return (
        <article className="rounded-[24px] border border-white/8 bg-white/[0.03] p-4">
            <div className="mb-3 flex items-start justify-between gap-3">
                <div>
                    <p className="text-sm font-medium text-white">{formatRunTimestamp(log.startedAt)}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.22em] text-mist/45">
                        {log.nodeKind} · finalizado {formatRunTimestamp(log.finishedAt)}
                    </p>
                </div>
                <span
                    className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${log.status === 'success' ? 'border-moss/30 bg-moss/15 text-moss' : 'border-ember/30 bg-ember/15 text-ember'}`}
                >
                    {log.status}
                </span>
            </div>

            {log.error ? (
                <div className="mb-3 rounded-2xl border border-ember/20 bg-ember/10 px-4 py-3 text-sm text-ember">{log.error}</div>
            ) : null}

            <div className="space-y-3">
                <JsonViewer data={log.input} defaultExpanded={false} title="Input" />
                <JsonViewer data={log.output} defaultExpanded={false} title="Output" />
            </div>
        </article>
    );
}

function formatRunTimestamp(value: string): string {
    return new Date(value).toLocaleString('es-ES', {
        dateStyle: 'short',
        timeStyle: 'medium',
    });
}