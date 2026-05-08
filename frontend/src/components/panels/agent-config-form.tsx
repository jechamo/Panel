import type { ChangeEvent, DragEvent } from 'react';

import { runAgentNode, uploadAttachment } from '../../lib/api';
import { JsonViewer } from '../ui/json-viewer';
import { useFlowStore } from '../../stores/flow-store';
import type { AgentNodeData, AttachmentReference } from '../../lib/types';

type AgentConfigFormProps = {
  nodeId: string;
  node: AgentNodeData;
  onChange: (nextNode: AgentNodeData) => void;
};

export function AgentConfigForm({ node, nodeId, onChange }: AgentConfigFormProps) {
  const { config } = node;
  const currentFlowId = useFlowStore((state) => state.currentFlowId);
  const setNodeRuntimeState = useFlowStore((state) => state.setNodeRuntimeState);

  const updateConfig = (nextConfig: AgentNodeData['config']) => {
    onChange({
      ...node,
      config: nextConfig,
    });
  };

  const addAttachments = (attachments: AttachmentReference[]) => {
    updateConfig({
      ...config,
      attachments: [...config.attachments, ...attachments],
    });
  };

  const uploadFiles = async (files: FileList) => {
    if (!currentFlowId) {
      setNodeRuntimeState(nodeId, 'error', node.output, 'Guarda el flujo antes de subir adjuntos.');
      return;
    }

    try {
      const uploadedAttachments = await Promise.all(
        Array.from(files).map((file) => uploadAttachment(currentFlowId, file)),
      );
      addAttachments(uploadedAttachments);
      setNodeRuntimeState(nodeId, node.status, node.output, null);
    }
    catch (error) {
      setNodeRuntimeState(
        nodeId,
        'error',
        node.output,
        error instanceof Error ? error.message : 'No se pudieron subir los adjuntos.',
      );
    }
  };

  const handleAttachmentSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || event.target.files.length === 0) {
      return;
    }

    await uploadFiles(event.target.files);

    event.target.value = '';
  };

  const handleAttachmentDrop = async (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();

    if (event.dataTransfer.files.length === 0) {
      return;
    }

    await uploadFiles(event.dataTransfer.files);
  };

  const handleRun = async () => {
    setNodeRuntimeState(nodeId, 'running', null, null);

    try {
      const result = await runAgentNode(nodeId, config, {
        flowId: currentFlowId,
      });
      setNodeRuntimeState(nodeId, 'success', result.output, null);
    }
    catch (error) {
      setNodeRuntimeState(
        nodeId,
        'error',
        null,
        error instanceof Error ? error.message : 'No se pudo ejecutar el agente.',
      );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          className="rounded-full border border-tide/35 bg-tide/18 px-4 py-2 text-sm font-medium text-white transition hover:bg-tide/28"
          onClick={() => void handleRun()}
          type="button"
        >
          {node.status === 'running' ? 'Ejecutando...' : 'Run'}
        </button>
        <span className="text-xs uppercase tracking-[0.24em] text-mist/45">Estado: {node.status}</span>
      </div>

      <section className="space-y-3">
        <div>
          <label className="text-xs uppercase tracking-[0.24em] text-mist/45">Modelo Anthropic</label>
          <input
            className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-tide/60"
            onChange={(event) => updateConfig({ ...config, model: event.target.value })}
            placeholder="ID exacto del modelo configurado"
            type="text"
            value={config.model}
          />
        </div>

        <div>
          <label className="text-xs uppercase tracking-[0.24em] text-mist/45">System prompt</label>
          <textarea
            className="mt-2 min-h-28 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
            onChange={(event) => updateConfig({ ...config, systemPrompt: event.target.value })}
            placeholder="Define el comportamiento base del agente"
            value={config.systemPrompt}
          />
        </div>

        <div>
          <label className="text-xs uppercase tracking-[0.24em] text-mist/45">User prompt</label>
          <textarea
            className="mt-2 min-h-36 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
            onChange={(event) => updateConfig({ ...config, userPrompt: event.target.value })}
            placeholder="Soporta plantillas como {{input.campo}} o {{archivos.documento}}"
            value={config.userPrompt}
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
        <section className="space-y-3 rounded-[28px] border border-tide/20 bg-tide/10 p-4">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-tide/80">Output</p>
            <p className="mt-1 text-sm text-mist/70">Respuesta estructurada validada contra los campos declarados.</p>
          </div>

          {typeof node.output === 'string' ? (
            <pre className="whitespace-pre-wrap rounded-2xl border border-white/8 bg-black/20 px-4 py-3 text-sm leading-6 text-mist/88">{node.output}</pre>
          ) : (
            <JsonViewer data={node.output} />
          )}
        </section>
      ) : null}

      <section className="space-y-3 rounded-[28px] border border-white/8 bg-black/15 p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Adjuntos</p>
            <p className="mt-1 text-sm text-mist/62">Subida real a backend. Requiere guardar antes el flujo actual.</p>
          </div>

          <label className="rounded-full border border-tide/35 bg-tide/18 px-4 py-2 text-sm text-white transition hover:bg-tide/28">
            Anadir archivos
            <input
              accept=".docx,.xlsx,.pdf"
              className="hidden"
              multiple
              onChange={(event) => {
                void handleAttachmentSelect(event);
              }}
              type="file"
            />
          </label>
        </div>

        <label
          className="flex min-h-28 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/10 px-4 py-5 text-center text-sm text-mist/58 transition hover:border-tide/35 hover:text-white"
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            void handleAttachmentDrop(event);
          }}
        >
          <span className="font-medium text-white">Arrastra .docx, .xlsx o .pdf aqui</span>
          <span className="mt-2 text-mist/55">O usa el selector superior para subir varios archivos.</span>
        </label>

        <div className="space-y-2">
          {config.attachments.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-white/10 px-4 py-5 text-sm text-mist/48">
              No hay adjuntos aun.
            </div>
          ) : (
            config.attachments.map((attachment) => (
              <div key={attachment.id} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-mist/72">
                <div>
                  <p className="text-white">{attachment.name}</p>
                  <p className="text-xs text-mist/45">
                    {attachment.mimeType} · {'{{'}archivos.{attachment.variableName}{'}}'}
                  </p>
                </div>

                <button
                  className="rounded-full border border-white/10 px-3 py-1 text-xs text-mist/68 transition hover:border-ember/35 hover:text-ember"
                  onClick={() =>
                    updateConfig({
                      ...config,
                      attachments: config.attachments.filter((item) => item.id !== attachment.id),
                    })
                  }
                  type="button"
                >
                  Quitar
                </button>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="space-y-3 rounded-[28px] border border-white/8 bg-black/15 p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Campos de salida</p>
            <p className="mt-1 text-sm text-mist/62">Define el schema JSON esperado del agente.</p>
          </div>

          <button
            className="rounded-full border border-moss/35 bg-moss/15 px-4 py-2 text-sm text-white transition hover:bg-moss/25"
            onClick={() =>
              updateConfig({
                ...config,
                outputFields: [
                  ...config.outputFields,
                  { id: crypto.randomUUID(), name: '', description: '' },
                ],
              })
            }
            type="button"
          >
            Anadir campo
          </button>
        </div>

        <div className="space-y-3">
          {config.outputFields.map((field, index) => (
            <div key={field.id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <span className="text-xs uppercase tracking-[0.24em] text-mist/45">Campo {index + 1}</span>
                <button
                  className="rounded-full border border-white/10 px-3 py-1 text-xs text-mist/68 transition hover:border-ember/35 hover:text-ember"
                  onClick={() =>
                    updateConfig({
                      ...config,
                      outputFields: config.outputFields.filter((item) => item.id !== field.id),
                    })
                  }
                  type="button"
                >
                  Eliminar
                </button>
              </div>

              <div className="space-y-3">
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
                  onChange={(event) =>
                    updateConfig({
                      ...config,
                      outputFields: config.outputFields.map((item) =>
                        item.id === field.id ? { ...item, name: event.target.value } : item,
                      ),
                    })
                  }
                  placeholder="nombre_del_campo"
                  value={field.name}
                />
                <textarea
                  className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
                  onChange={(event) =>
                    updateConfig({
                      ...config,
                      outputFields: config.outputFields.map((item) =>
                        item.id === field.id ? { ...item, description: event.target.value } : item,
                      ),
                    })
                  }
                  placeholder="Descripcion del campo de salida"
                  value={field.description}
                />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}