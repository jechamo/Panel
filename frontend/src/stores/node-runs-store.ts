import { create } from 'zustand';

import { listNodeRuns } from '../lib/api';
import type { NodeRunLog } from '../lib/types';

type NodeRunsState = {
    error: string | null;
    isLoading: boolean;
    logsByNode: Record<string, NodeRunLog[]>;
    loadNodeRuns: (nodeId: string, flowId?: string | null) => Promise<void>;
};

function makeKey(nodeId: string, flowId?: string | null): string {
    return `${flowId ?? 'local'}::${nodeId}`;
}

export const useNodeRunsStore = create<NodeRunsState>((set) => ({
    error: null,
    isLoading: false,
    logsByNode: {},
    loadNodeRuns: async (nodeId, flowId) => {
        set({ isLoading: true, error: null });

        try {
            const logs = await listNodeRuns(nodeId, flowId);
            set((state) => ({
                error: null,
                isLoading: false,
                logsByNode: {
                    ...state.logsByNode,
                    [makeKey(nodeId, flowId)]: logs,
                },
            }));
        }
        catch (error) {
            set({
                error: error instanceof Error ? error.message : 'No se pudieron cargar los logs del nodo.',
                isLoading: false,
            });
        }
    },
}));

export function getNodeRunsKey(nodeId: string, flowId?: string | null): string {
    return makeKey(nodeId, flowId);
}