import type { JsonValue } from '../../lib/types';

type JsonViewerProps = {
  data: JsonValue;
  name?: string;
};

export function JsonViewer({ data, name = 'root' }: JsonViewerProps) {
  if (data === null || typeof data !== 'object') {
    return <span className="font-mono text-sm text-mist/80">{JSON.stringify(data)}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <details className="rounded-2xl border border-white/8 bg-black/20 px-4 py-3" open>
        <summary className="cursor-pointer text-sm text-white">{name} [{data.length}]</summary>
        <div className="mt-3 space-y-2 pl-4">
          {data.map((item, index) => (
            <JsonViewer data={item} key={`${name}-${index}`} name={`${index}`} />
          ))}
        </div>
      </details>
    );
  }

  return (
    <details className="rounded-2xl border border-white/8 bg-black/20 px-4 py-3" open>
      <summary className="cursor-pointer text-sm text-white">{name}</summary>
      <div className="mt-3 space-y-2 pl-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="grid grid-cols-[minmax(100px,160px)_1fr] gap-3 text-sm">
            <span className="font-mono text-tide">{key}</span>
            {value !== null && typeof value === 'object' ? (
              <JsonViewer data={value as JsonValue} name={key} />
            ) : (
              <span className="font-mono text-mist/80">{JSON.stringify(value)}</span>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}