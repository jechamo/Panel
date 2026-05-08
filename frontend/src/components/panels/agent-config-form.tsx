import type { ChangeEvent } from 'react';

import type { AgentNodeData, AttachmentReference } from '../../lib/types';

const modelOptions = [
  { value: 'anthropic', label: 'Anthropic (Settings pendiente)' },
  { value: 'openai', label: 'OpenAI (Settings pendiente)' },
  { value: 'gemini', label: 'Gemini (Settings pendiente)' },
];

type AgentConfigFormProps = {
  node: AgentNodeData;
  onChange: (nextNode: AgentNodeData) => void;
};

function mapAttachments(files: FileList): AttachmentReference[] {
  return Array.from(files).map((file) => ({
    id: crypto.randomUUID(),
    mimeType: file.type || 'application/octet-stream',
    name: file.name,
  }));
}

export function AgentConfigForm({ node, onChange }: AgentConfigFormProps) {
  const { config } = node;

  const updateConfig = (nextConfig: AgentNodeData['config']) => {
    onChange({
      ...node,
      config: nextConfig,
    });
  };

  const handleAttachmentSelect = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || event.target.files.length === 0) {
      return;
    }

    updateConfig({
      ...config,
      attachments: [...config.attachments, ...mapAttachments(event.target.files)],
    });

    event.target.value = '';
  };

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <div>
          <label className="text-xs uppercase tracking-[0.24em] text-mist/45">Modelo</label>
          <select
            className="mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-tide/60"
            onChange={(event) => updateConfig({ ...config, model: event.target.value })}
            value={config.model}
          >
            {modelOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
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

      <section className="space-y-3 rounded-[28px] border border-white/8 bg-black/15 p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Adjuntos</p>
            <p className="mt-1 text-sm text-mist/62">Se guardan como referencias locales hasta la fase de upload.</p>
          </div>

          <label className="rounded-full border border-tide/35 bg-tide/18 px-4 py-2 text-sm text-white transition hover:bg-tide/28">
            Anadir archivos
            <input
              accept=".docx,.xlsx,.pdf"
              className="hidden"
              multiple
              onChange={handleAttachmentSelect}
              type="file"
            />
          </label>
        </div>

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
                  <p className="text-xs text-mist/45">{attachment.mimeType}</p>
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