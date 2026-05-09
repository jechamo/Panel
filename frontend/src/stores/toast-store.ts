import { create } from 'zustand';

type ToastTone = 'error' | 'info' | 'success';

export type ToastItem = {
    id: string;
    message: string;
    tone: ToastTone;
};

type ToastState = {
    dismissToast: (id: string) => void;
    pushToast: (message: string, tone?: ToastTone) => void;
    toasts: ToastItem[];
};

export const useToastStore = create<ToastState>((set) => ({
    dismissToast: (id) =>
        set((state) => ({
            toasts: state.toasts.filter((toast) => toast.id !== id),
        })),
    pushToast: (message, tone = 'info') => {
        const id = crypto.randomUUID();
        set((state) => ({
            toasts: [...state.toasts, { id, message, tone }],
        }));

        window.setTimeout(() => {
            set((state) => ({
                toasts: state.toasts.filter((toast) => toast.id !== id),
            }));
        }, 3200);
    },
    toasts: [],
}));