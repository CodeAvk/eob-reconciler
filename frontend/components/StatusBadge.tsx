import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react";
import type { CaseStatus } from "@/lib/api";

const MAP = {
  queued: { label: "Queued", icon: Clock, cls: "badge-neutral" },
  processing: { label: "Processing", icon: Loader2, cls: "badge-info" },
  done: { label: "Complete", icon: CheckCircle2, cls: "badge-ok" },
  failed: { label: "Failed", icon: XCircle, cls: "badge-danger" },
} as const;

export default function StatusBadge({ status }: { status: CaseStatus }) {
  const { label, icon: Icon, cls } = MAP[status];
  return (
    <span className={`badge ${cls}`}>
      <Icon size={14} aria-hidden className={status === "processing" ? "spin" : undefined} />
      {label}
    </span>
  );
}
