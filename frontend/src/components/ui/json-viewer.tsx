import { useState } from 'react';

import type { JsonObject, JsonValue } from '../../lib/types';

type JsonViewerProps = {
  data: JsonValue;
  defaultExpanded?: boolean;
  title?: string;
};

export function JsonViewer({ data, defaultExpanded = true, title = 'Output JSON' }: JsonViewerProps) {
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'error'>('idle');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopyStatus('copied');
      window.setTimeout(() => setCopyStatus('idle'), 1400);
    }
    catch {
      setCopyStatus('error');
      window.setTimeout(() => setCopyStatus('idle'), 1800);
    }
  };

  return (
    <section className="overflow-hidden rounded-[28px] border border-white/8 bg-black/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]">
      <div className="flex items-center justify-between gap-4 border-b border-white/8 bg-white/[0.03] px-4 py-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Viewer</p>
          <h3 className="mt-1 text-sm font-medium text-white">{title}</h3>
        </div>

        <button
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs uppercase tracking-[0.18em] text-mist/72 transition hover:border-white/20 hover:text-white"
          onClick={() => void handleCopy()}
          type="button"
        >
          {copyStatus === 'idle' ? 'Copiar JSON' : copyStatus === 'copied' ? 'Copiado' : 'Error'}
        </button>
      </div>

      <div className="space-y-2 p-4">
        <JsonBranch data={data} defaultExpanded={defaultExpanded} label="root" level={0} />
      </div>
    </section>
  );
}

type JsonBranchProps = {
  data: JsonValue;
  defaultExpanded: boolean;
  label: string;
  level: number;
};

function JsonBranch({ data, defaultExpanded, label, level }: JsonBranchProps) {
  if (data === null || typeof data !== 'object') {
    return <JsonLeaf label={label} value={data} />;
  }

  if (Array.isArray(data)) {
    return (
      <details className="rounded-2xl border border-white/8 bg-white/[0.02]" open={defaultExpanded || level < 1}>
        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 marker:hidden">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm text-tide">{label}</span>
            <span className="rounded-full border border-white/8 bg-black/20 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-mist/55">
              array
            </span>
          </div>
          <span className="text-xs text-mist/55">{data.length} items</span>
        </summary>

        <div className="space-y-2 border-t border-white/6 px-3 py-3">
          {data.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/8 px-3 py-3 text-sm text-mist/45">[]</div>
          ) : (
            data.map((item, index) => (
              <JsonBranch
                data={item}
                defaultExpanded={false}
                key={`${label}-${index}`}
                label={`[${index}]`}
                level={level + 1}
              />
            ))
          )}
        </div>
      </details>
    );
  }

  return (
    <details className="rounded-2xl border border-white/8 bg-white/[0.02]" open={defaultExpanded || level < 1}>
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 marker:hidden">
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm text-tide">{label}</span>
          <span className="rounded-full border border-white/8 bg-black/20 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-mist/55">
            object
          </span>
        </div>
        <span className="text-xs text-mist/55">{Object.keys(data as JsonObject).length} keys</span>
      </summary>

      <div className="space-y-2 border-t border-white/6 px-3 py-3">
        {Object.keys(data as JsonObject).length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/8 px-3 py-3 text-sm text-mist/45">{'{}'}</div>
        ) : (
          Object.entries(data as JsonObject).map(([key, value]) => (
            <JsonBranch
              data={value}
              defaultExpanded={false}
              key={key}
              label={key}
              level={level + 1}
            />
          ))
        )}
      </div>
    </details>
  );
}

type JsonLeafProps = {
  label: string;
  value: JsonValue;
};

function JsonLeaf({ label, value }: JsonLeafProps) {
  return (
    <div className="grid grid-cols-[minmax(120px,180px)_1fr] gap-3 rounded-2xl border border-white/8 bg-white/[0.02] px-4 py-3 text-sm">
      <span className="font-mono text-tide">{label}</span>
      <span className={`font-mono ${getValueTone(value)}`}>{formatValue(value)}</span>
    </div>
  );
}

function formatValue(value: JsonValue): string {
  if (typeof value === 'string') {
    return `"${value}"`;
  }

  return JSON.stringify(value);
}

function getValueTone(value: JsonValue): string {
  if (typeof value === 'string') {
    return 'text-moss';
  }

  if (typeof value === 'number') {
    return 'text-ember';
  }

  if (typeof value === 'boolean') {
    return 'text-tide';
  }

  if (value === null) {
    return 'text-mist/50';
  }

  return 'text-mist/80';
}