import { Handle, Position } from '@xyflow/react';

import type { WorkflowNodeData } from '../../lib/types';

const statusTone: Record<WorkflowNodeData['status'], string> = {
  idle: 'border-white/15 bg-white/5 text-mist/75',
  running: 'border-tide/30 bg-tide/15 text-tide',
  success: 'border-moss/30 bg-moss/15 text-moss',
  error: 'border-ember/30 bg-ember/15 text-ember',
};

const accentTone: Record<WorkflowNodeData['kind'], string> = {
  agent: 'from-tide/80 to-tide/30',
  microservice: 'from-ember/80 to-ember/30',
};

type WorkflowNodeProps = {
  data: WorkflowNodeData;
};

export function WorkflowNode({ data }: WorkflowNodeProps) {
  return (
    <div className="relative min-w-[260px] rounded-[28px] border border-white/10 bg-[#0b111a]/95 p-4 shadow-[0_24px_64px_rgba(8,15,30,0.45)] backdrop-blur">
      <Handle className="!h-3 !w-3 !border-0 !bg-tide" position={Position.Top} type="target" />

      <div className={`absolute inset-x-4 top-0 h-px bg-gradient-to-r ${accentTone[data.kind]}`} />

      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-[11px] uppercase tracking-[0.28em] text-mist/45">
            {data.kind === 'agent' ? 'LLM Node' : 'HTTP Node'}
          </span>
          <h3 className="mt-2 text-lg font-semibold text-white">{data.title}</h3>
        </div>

        <span className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.22em] ${statusTone[data.status]}`}>
          {data.status}
        </span>
      </div>

      <p className="mt-3 text-sm leading-6 text-mist/68">{data.description}</p>

      <div className="mt-5 flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-3 py-2 text-xs text-mist/58">
        <span>Entradas encadenables</span>
        <span>Salidas reutilizables</span>
      </div>

      <Handle className="!h-3 !w-3 !border-0 !bg-ember" position={Position.Bottom} type="source" />
    </div>
  );
}