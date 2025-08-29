// frontend/src/components/SettingsPanel.tsx
import { useState } from "react";

export function SettingsPanel({
  sttServerEnabled,
  onToggleServerStt,
}: {
  sttServerEnabled: boolean;
  onToggleServerStt: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2">
      <input
        type="checkbox"
        checked={sttServerEnabled}
        onChange={(e) => onToggleServerStt(e.target.checked)}
      />
      <span>Use server STT (audio leaves device)</span>
    </label>
  );
}
