import { useEffect, useState } from 'react';

import { useSettingsStore } from '../../stores/settings-store';
import { useToastStore } from '../../stores/toast-store';

type SettingsPanelProps = {
    isOpen: boolean;
    onClose: () => void;
};

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
    const { error, isLoading, isSaving, loadSettings, saveSettings, settings } = useSettingsStore();
    const pushToast = useToastStore((state) => state.pushToast);
    const [anthropicApiKey, setAnthropicApiKey] = useState('');
    const [openaiApiKey, setOpenaiApiKey] = useState('');
    const [geminiApiKey, setGeminiApiKey] = useState('');
    const [message, setMessage] = useState<string | null>(null);

    useEffect(() => {
        if (!isOpen) {
            return;
        }

        void loadSettings();
    }, [isOpen, loadSettings]);

    if (!isOpen) {
        return null;
    }

    const handleSave = async () => {
        setMessage(null);

        try {
            await saveSettings({
                anthropicApiKey,
                openaiApiKey,
                geminiApiKey,
            });
            setAnthropicApiKey('');
            setOpenaiApiKey('');
            setGeminiApiKey('');
            setMessage('Settings guardados en backend/.env.');
            pushToast('Settings guardados en backend/.env.', 'success');
        }
        catch (error) {
            setMessage(null);
            pushToast(error instanceof Error ? error.message : 'No se pudieron guardar Settings.', 'error');
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/55 px-4 py-6 backdrop-blur-sm">
            <div className="w-full max-w-2xl rounded-[32px] border border-white/10 bg-panel/95 p-6 shadow-glow">
                <div className="mb-6 flex items-start justify-between gap-4">
                    <div>
                        <p className="text-xs uppercase tracking-[0.3em] text-mist/45">Settings</p>
                        <h2 className="mt-2 text-2xl font-semibold text-white">Credenciales y modelos</h2>
                        <p className="mt-2 text-sm leading-6 text-mist/62">
                            Las API keys se persisten en backend/.env para simplificar el flujo local de esta fase.
                        </p>
                    </div>

                    <button
                        className="rounded-full border border-white/10 px-3 py-2 text-xs uppercase tracking-[0.2em] text-mist/62 transition hover:border-white/20 hover:text-white"
                        onClick={onClose}
                        type="button"
                    >
                        Cerrar
                    </button>
                </div>

                <div className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
                    <div className="space-y-4">
                        <ProviderField
                            configured={Boolean(settings?.anthropicConfigured)}
                            label="Anthropic API Key"
                            onChange={setAnthropicApiKey}
                            provider="anthropic"
                            value={anthropicApiKey}
                        />
                        <ProviderField
                            configured={Boolean(settings?.openaiConfigured)}
                            label="OpenAI API Key"
                            onChange={setOpenaiApiKey}
                            provider="openai"
                            value={openaiApiKey}
                        />
                        <ProviderField
                            configured={Boolean(settings?.geminiConfigured)}
                            label="Gemini API Key"
                            onChange={setGeminiApiKey}
                            provider="gemini"
                            value={geminiApiKey}
                        />

                        <div className="flex items-center gap-3">
                            <button
                                className="rounded-full border border-tide/35 bg-tide/18 px-4 py-2 text-sm font-medium text-white transition hover:bg-tide/28 disabled:cursor-not-allowed disabled:opacity-60"
                                disabled={isSaving}
                                onClick={() => void handleSave()}
                                type="button"
                            >
                                {isSaving ? 'Guardando...' : 'Guardar Settings'}
                            </button>
                            {isLoading ? <span className="text-sm text-mist/62">Cargando...</span> : null}
                        </div>

                        {message ? <p className="text-sm text-moss">{message}</p> : null}
                        {error ? <p className="text-sm text-ember">{error}</p> : null}
                    </div>

                    <section className="rounded-[28px] border border-white/8 bg-black/15 p-4">
                        <p className="text-xs uppercase tracking-[0.24em] text-mist/45">Catalogo de modelos</p>
                        <p className="mt-2 text-sm text-mist/62">
                            El selector del nodo Agente lee backend/config/models.yaml via API.
                        </p>

                        <div className="mt-4 space-y-2">
                            {settings?.models.length ? (
                                settings.models.map((model) => (
                                    <div
                                        key={`${model.provider}-${model.id}`}
                                        className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3"
                                    >
                                        <p className="text-sm font-medium text-white">{model.label}</p>
                                        <p className="mt-1 text-xs uppercase tracking-[0.22em] text-mist/45">
                                            {model.provider} · {model.id}
                                        </p>
                                    </div>
                                ))
                            ) : (
                                <div className="rounded-2xl border border-dashed border-white/10 px-4 py-5 text-sm text-mist/50">
                                    No hay modelos configurados. Edita backend/config/models.yaml con ids oficiales.
                                </div>
                            )}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}

type ProviderFieldProps = {
    configured: boolean;
    label: string;
    onChange: (value: string) => void;
    provider: string;
    value: string;
};

function ProviderField({ configured, label, onChange, provider, value }: ProviderFieldProps) {
    return (
        <div className="rounded-[28px] border border-white/8 bg-black/15 p-4">
            <div className="mb-3 flex items-center justify-between gap-3">
                <label className="text-sm font-medium text-white">{label}</label>
                <span
                    className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.22em] ${configured ? 'border-moss/30 bg-moss/15 text-moss' : 'border-white/10 bg-white/5 text-mist/55'}`}
                >
                    {configured ? 'configurada' : 'vacia'}
                </span>
            </div>

            <input
                className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-mist/30 focus:border-tide/60"
                onChange={(event) => onChange(event.target.value)}
                placeholder={`Introduce la clave de ${provider}`}
                type="password"
                value={value}
            />
        </div>
    );
}