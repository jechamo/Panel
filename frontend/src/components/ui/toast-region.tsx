import { useToastStore } from '../../stores/toast-store';

const toneClassNames = {
    error: 'border-ember/30 bg-ember/15 text-ember',
    info: 'border-white/10 bg-white/8 text-mist/85',
    success: 'border-moss/30 bg-moss/15 text-moss',
} as const;

export function ToastRegion() {
    const dismissToast = useToastStore((state) => state.dismissToast);
    const toasts = useToastStore((state) => state.toasts);

    return (
        <div className="pointer-events-none fixed right-4 top-4 z-[80] flex w-full max-w-sm flex-col gap-3">
            {toasts.map((toast) => (
                <div
                    className={`pointer-events-auto rounded-[24px] border px-4 py-3 shadow-glow backdrop-blur ${toneClassNames[toast.tone]}`}
                    key={toast.id}
                >
                    <div className="flex items-start justify-between gap-3">
                        <p className="text-sm leading-6">{toast.message}</p>
                        <button
                            className="rounded-full border border-current/20 px-2 py-1 text-[11px] uppercase tracking-[0.18em]"
                            onClick={() => dismissToast(toast.id)}
                            type="button"
                        >
                            Cerrar
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}