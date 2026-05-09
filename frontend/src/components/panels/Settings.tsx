import { useEffect, useState } from "react";
import { api, type ProviderSpec, type SettingsView } from "../../api/client";

type FieldDef = {
  key: string; // setting storage key
  label: string;
  placeholder?: string;
  secret?: boolean;
};

const EXTRA_FIELD_LABEL: Record<string, string> = {
  base_url: "Base URL",
  endpoint: "Endpoint",
  api_version: "API Version",
  deployment: "Deployment name",
  command_template: "Command template",
  timeout_seconds: "Timeout (seconds)",
  output_path: "Output JSON path (optional)",
};

const EXTRA_FIELD_PLACEHOLDER: Record<string, string> = {
  base_url: "https://gateway.interno/v1",
  endpoint: "https://miorg.openai.azure.com/",
  api_version: "2024-08-01-preview",
  deployment: "gpt-4o-deployment",
  command_template: "claude -p --output-format json",
  timeout_seconds: "120",
  output_path: "result",
};

function fieldsForProvider(providerId: string, spec: ProviderSpec): FieldDef[] {
  const out: FieldDef[] = [];
  if (spec.secret_key) {
    out.push({
      key: spec.secret_key,
      label: `${spec.label} — API key`,
      placeholder: providerId === "anthropic" ? "sk-ant-..." : "sk-...",
      secret: true,
    });
  }
  for (const e of spec.extra_fields || []) {
    out.push({
      key: `${providerId}__${e}`,
      label: `${spec.label} — ${EXTRA_FIELD_LABEL[e] || e}`,
      placeholder: EXTRA_FIELD_PLACEHOLDER[e],
      secret: false,
    });
  }
  if (spec.supports_base_url && !(spec.extra_fields || []).includes("base_url")) {
    out.push({
      key: `${providerId}__base_url`,
      label: `${spec.label} — Base URL (opcional)`,
      placeholder: "https://gateway.interno/v1",
      secret: false,
    });
  }
  return out;
}

export default function SettingsModal({ onClose }: { onClose: () => void }) {
  const [view, setView] = useState<SettingsView | null>(null);
  const [providers, setProviders] = useState<Record<string, ProviderSpec>>({});
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [copilotStatus, setCopilotStatus] = useState<{ available: boolean; reason: string } | null>(
    null
  );

  useEffect(() => {
    api.getSettings().then(setView);
    api.getProviders().then(setProviders);
    api.copilotCliStatus().then(setCopilotStatus).catch(() => setCopilotStatus(null));
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

  const present = view?.present || {};

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
        style={{ width: 560, maxHeight: "90vh", overflowY: "auto" }}
      >
        <h2>⚙️ Provider settings</h2>
        <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 0 }}>
          Las claves se cifran en disco. Deja un campo vacío para mantener su valor actual.
        </p>

        {Object.entries(providers).map(([providerId, spec]) => {
          const fields = fieldsForProvider(providerId, spec);
          const isCopilot = providerId === "copilot_models" || providerId === "copilot_cli";
          if (fields.length === 0 && !isCopilot) return null;
          return (
            <fieldset
              key={providerId}
              style={{
                border: "1px solid var(--border)",
                borderRadius: 8,
                padding: 12,
                marginBottom: 12,
              }}
            >
              <legend style={{ padding: "0 8px", color: "var(--accent)" }}>
                {spec.label}
              </legend>
              {isCopilot && copilotStatus && (
                <div
                  className={copilotStatus.available ? "status ok" : "status error"}
                  style={{ marginBottom: 8, padding: "2px 6px", border: "0" }}
                >
                  gh CLI: {copilotStatus.available ? "OK" : copilotStatus.reason}
                </div>
              )}
              {fields.map((f) => (
                <div key={f.key} className="field">
                  <label>
                    {f.label}{" "}
                    {present[f.key] && (
                      <span style={{ color: "var(--ok)" }}>· configurado</span>
                    )}
                  </label>
                  <input
                    type={f.secret ? "password" : "text"}
                    placeholder={f.placeholder}
                    value={drafts[f.key] || ""}
                    onChange={(e) => setDrafts({ ...drafts, [f.key]: e.target.value })}
                  />
                </div>
              ))}
            </fieldset>
          );
        })}

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
