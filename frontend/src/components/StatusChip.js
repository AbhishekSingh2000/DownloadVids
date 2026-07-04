import React from "react";
import { TESTIDS } from "@/constants/testIds";
import { statusChipClasses } from "@/lib/api";
import { Loader2, CheckCircle2, AlertTriangle, Clock } from "lucide-react";

const ICONS = {
  pending: <Clock className="h-3 w-3" />,
  preparing: <Loader2 className="h-3 w-3 animate-spin" />,
  ready: <CheckCircle2 className="h-3 w-3" />,
  error: <AlertTriangle className="h-3 w-3" />,
};

export default function StatusChip({ status, infId }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${statusChipClasses(status)}`}
      data-testid={TESTIDS.rowStatus(infId)}
    >
      {ICONS[status]}
      {status}
    </span>
  );
}
