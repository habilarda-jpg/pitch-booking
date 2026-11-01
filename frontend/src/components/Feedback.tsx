import type { ReactNode } from "react";

type AlertKind = "success" | "error" | "info";

interface AlertProps {
  kind: AlertKind;
  title?: string;
  children: ReactNode;
  onDismiss?: () => void;
}

const ICONS: Record<AlertKind, string> = { success: "✓", error: "!", info: "i" };

export function Alert({ kind, title, children, onDismiss }: AlertProps) {
  return (
    <div className={`alert alert--${kind}`} role={kind === "error" ? "alert" : "status"}>
      <span className="alert__icon" aria-hidden="true">
        {ICONS[kind]}
      </span>
      <div className="alert__body">
        {title && <p className="alert__title">{title}</p>}
        <div>{children}</div>
      </div>
      {onDismiss && (
        <button type="button" className="alert__close" onClick={onDismiss} aria-label="Dismiss message">
          ×
        </button>
      )}
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function Spinner() {
  return <span className="spinner spinner--small" aria-hidden="true" />;
}
