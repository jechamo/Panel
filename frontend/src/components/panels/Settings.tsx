import { useEffect, useState } from "react";
import { api, type SettingsView } from "../../api/client";

const FIELDS: { key: keyof SettingsView; label: string; placeholder: string }[] = [
  { key: "anthropic_api_key", label: "Anthropic API Key", placeholder: "sk-ant-..." },
  { key: "openai_api_key", label: "OpenAI API Key", placeholder: "sk-..." },
  { key: "gemini_api_key", label: "Google Gemini API Key", placeholder: "AIza..." },
  { key: "github_token", label: "GitHub Token (for GitHub Models)", placeholder: "ghp_..." },
];

export default function SettingsModal({ onClose }: { onClose: () => void }) {
  const [view, setView] = useState<SettingsView | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getSettings().then(setView);
  }, []);

  const save = async () => {
    setBusy(true);
    try {
      for (const [k, v] of Object.entries(drafts)) {
        if (v.length > 0) await api.putSetting(k, v);
      }
      const fresh = await api.getSettings();
      setView(fresh);
      setDrafts({});
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>⚙️ Provider settings</h2>
        <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 0 }}>
          Keys are encrypted at rest. Leave a field empty to keep its current value.
        </p>
        {FIELDS.map((f) => (
          <div key={f.key} className="field">
            <label>
              {f.label}{" "}
              {view?.[f.key] && (
                <span style={{ color: "var(--ok)" }}>· configured</span>
              )}
            </label>
            <input
              type="password"
              placeholder={f.placeholder}
              value={drafts[f.key] || ""}
              onChange={(e) => setDrafts({ ...drafts, [f.key]: e.target.value })}
            />
          </div>
        ))}
        <div className="actions">
          <button onClick={onClose}>Close</button>
          <button className="primary" onClick={save} disabled={busy}>
            {busy ? "Saving…" : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
