import { create } from 'zustand';

import {
  getSettingsSnapshot,
  updateSettingsSnapshot,
} from '../lib/api';
import type { SettingsSnapshot, SettingsUpdatePayload } from '../lib/types';

type SettingsState = {
  error: string | null;
  isLoaded: boolean;
  isLoading: boolean;
  isSaving: boolean;
  settings: SettingsSnapshot | null;
  loadSettings: () => Promise<void>;
  saveSettings: (payload: SettingsUpdatePayload) => Promise<void>;
};

export const useSettingsStore = create<SettingsState>((set, get) => ({
  error: null,
  isLoaded: false,
  isLoading: false,
  isSaving: false,
  settings: null,
  loadSettings: async () => {
    if (get().isLoading) {
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const settings = await getSettingsSnapshot();
      set({ settings, isLoaded: true, isLoading: false });
    }
    catch (error) {
      set({
        error: error instanceof Error ? error.message : 'No se pudo cargar Settings.',
        isLoading: false,
      });
    }
  },
  saveSettings: async (payload) => {
    set({ isSaving: true, error: null });

    try {
      const settings = await updateSettingsSnapshot(payload);
      set({ settings, isLoaded: true, isSaving: false });
    }
    catch (error) {
      set({
        error: error instanceof Error ? error.message : 'No se pudieron guardar Settings.',
        isSaving: false,
      });
      throw error;
    }
  },
}));