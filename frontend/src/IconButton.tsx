import React from "react";

export function IconButton({ label, disabled }: { label: string; disabled?: boolean }) {
  return (
    <button className="icon-button" aria-label={label} disabled={disabled} title={label}>
      <span className="icon-dot" aria-hidden="true" />
    </button>
  );
}
