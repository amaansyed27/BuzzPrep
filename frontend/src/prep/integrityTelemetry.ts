import { useEffect } from "react";
import type { IntegrityTelemetryEvent } from "../apiTypes";

let pendingEvents: IntegrityTelemetryEvent[] = [];

function record(type: IntegrityTelemetryEvent["type"]) {
  pendingEvents = [
    ...pendingEvents,
    { type, timestamp: new Date().toISOString() },
  ].slice(-100);
}

export function drainIntegrityEvents(): IntegrityTelemetryEvent[] {
  const events = pendingEvents;
  pendingEvents = [];
  return events;
}

export function restoreIntegrityEvents(events: IntegrityTelemetryEvent[]) {
  pendingEvents = [...events, ...pendingEvents].slice(-100);
}

export function useIntegrityTelemetry(enabled: boolean) {
  useEffect(() => {
    if (!enabled) return;

    const onVisibility = () => record(document.hidden ? "tab_hidden" : "tab_visible");
    const onBlur = () => record("window_blur");
    const onFocus = () => record("window_focus");
    const onFullscreen = () => record(document.fullscreenElement ? "fullscreen_enter" : "fullscreen_exit");
    const onOnline = () => record("reconnect");

    record(document.hasFocus() ? "window_focus" : "window_blur");
    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFullscreen);
    window.addEventListener("blur", onBlur);
    window.addEventListener("focus", onFocus);
    window.addEventListener("online", onOnline);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFullscreen);
      window.removeEventListener("blur", onBlur);
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("online", onOnline);
    };
  }, [enabled]);
}
