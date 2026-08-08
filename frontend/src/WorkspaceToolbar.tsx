import React from "react";
import { IconButton } from "./IconButton";

export default function WorkspaceToolbar() {
  return (
    <div className="workspace-toolbar" role="toolbar" aria-label="Workspace toolbar">
      {/* Some controls will be UI-only for now */}
      <IconButton label="Fit view" disabled />
      <IconButton label="Export" disabled />
      <IconButton label="Hints" disabled />
    </div>
  );
}
