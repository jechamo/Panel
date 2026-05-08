import { useEffect, useState } from 'react';

import { createFlow, getFlow, listFlows, runFlow, updateFlow } from '../../lib/api';
import type { FlowSummary } from '../../lib/types';
import { useFlowStore } from '../../stores/flow-store';

export function FlowPersistenceBar() {
  const { buildFlowPayload, currentFlowId, currentFlowName, loadFlow, setCurrentFlowMeta } = useFlowStore();
  const [flows, setFlows] = useState<FlowSummary[]>([]);
  const [isListOpen, setIsListOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isListOpen) {
      return;
    }

    void refreshFlows();
  }, [isListOpen]);

  const refreshFlows = async () => {
    try {
      setFlows(await listFlows());
    }
    catch (error) {
      setMessage(error instanceof Error ? error.message : 'No se pudo cargar la lista de flujos.');
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      const payload = buildFlowPayload();
      const document = currentFlowId
        ? await updateFlow({ id: currentFlowId, ...payload })
        : await createFlow(payload);

      setCurrentFlowMeta(document.id, document.name);
      setMessage(currentFlowId ? 'Flujo actualizado.' : 'Flujo guardado.');

      if (isListOpen) {
        await refreshFlows();
      }
    }
    catch (error) {
      setMessage(error instanceof Error ? error.message : 'No se pudo guardar el flujo.');
    }
    finally {
      setIsSaving(false);
    }
  };

  const handleLoad = async (flowId: string) => {
    try {
      const flow = await getFlow(flowId);
      loadFlow(flow);
      setIsListOpen(false);
      setMessage(`Flujo ${flow.name} cargado.`);
    }
    catch (error) {
      setMessage(error instanceof Error ? error.message : 'No se pudo cargar el flujo.');
    }
  };

  const handleRunAll = async () => {
    setIsRunning(true);
    setMessage(null);

    try {
      const payload = buildFlowPayload();
      const persistedFlow = currentFlowId
        ? await updateFlow({ id: currentFlowId, ...payload })
        : await createFlow(payload);

      const executedFlow = await runFlow(persistedFlow.id);
      loadFlow(executedFlow);
      setCurrentFlowMeta(executedFlow.id, executedFlow.name);
      setMessage('Flujo ejecutado. Estados y outputs sincronizados desde backend.');

      if (isListOpen) {
        await refreshFlows();
      }
    }
    catch (error) {
      setMessage(error instanceof Error ? error.message : 'No se pudo ejecutar el flujo.');
    }
    finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="rounded-[28px] border border-white/10 bg-black/20 p-3 backdrop-blur md:min-w-[360px]">
      <div className="flex flex-col gap-3">
        <input
          className="w-full rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
          onChange={(event) => setCurrentFlowMeta(currentFlowId, event.target.value)}
          placeholder="Nombre del flujo"
          value={currentFlowName}
        />

        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-full border border-moss/35 bg-moss/15 px-4 py-2 text-sm text-white transition hover:bg-moss/25 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSaving}
            onClick={() => void handleSave()}
            type="button"
          >
            {isSaving ? 'Guardando...' : 'Guardar'}
          </button>
          <button
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-mist/80 transition hover:border-white/20 hover:text-white"
            onClick={() => setIsListOpen((current) => !current)}
            type="button"
          >
            {isListOpen ? 'Cerrar lista' : 'Cargar'}
          </button>
          <button
            className="rounded-full border border-tide/35 bg-tide/18 px-4 py-2 text-sm text-white transition hover:bg-tide/28 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isRunning}
            onClick={() => void handleRunAll()}
            type="button"
          >
            {isRunning ? 'Ejecutando flujo...' : 'Run All'}
          </button>
        </div>

        {message ? <p className="text-sm text-mist/72">{message}</p> : null}

        {isListOpen ? (
          <div className="space-y-2 rounded-2xl border border-white/10 bg-black/25 p-3">
            {flows.length === 0 ? (
              <p className="text-sm text-mist/55">No hay flujos guardados aun.</p>
            ) : (
              flows.map((flow) => (
                <button
                  key={flow.id}
                  className="flex w-full items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-left text-sm text-mist/78 transition hover:border-tide/30 hover:bg-tide/10"
                  onClick={() => void handleLoad(flow.id)}
                  type="button"
                >
                  <span className="truncate text-white">{flow.name}</span>
                  <span className="ml-3 text-xs uppercase tracking-[0.24em] text-mist/45">v{flow.version}</span>
                </button>
              ))
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}