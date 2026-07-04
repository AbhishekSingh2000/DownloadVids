import React, { useEffect, useMemo, useState, useCallback } from "react";
import { api, platformLabel, platformBadgeClasses, openDownload } from "@/lib/api";
import { TESTIDS } from "@/constants/testIds";
import { toast } from "sonner";
import {
  Loader2, Download, RefreshCw, ChevronDown, ChevronUp,
  ExternalLink, Copy, CheckCircle2, AlertTriangle, Search,
  Music2, Video, Play, X, Filter, Trash2, Sun, Moon, Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader,
  AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Skeleton } from "@/components/ui/skeleton";
import RowActions from "@/components/RowActions";
import StatusChip from "@/components/StatusChip";

const PLATFORMS = ["all", "instagram", "tiktok", "youtube", "facebook"];
const STATUSES = ["all", "pending", "preparing", "ready", "error"];

export default function Dashboard() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [platform, setPlatform] = useState("all");
  const [status, setStatus] = useState("all");
  const [bulkPreparing, setBulkPreparing] = useState(false);
  const [bulkDownloading, setBulkDownloading] = useState(false);
  const [expandedError, setExpandedError] = useState({});
  const [dark, setDark] = useState(false);

  const loadRows = useCallback(async () => {
    try {
      const r = await api.get("/videos");
      setRows(r.data);
    } catch (e) {
      toast.error("Failed to load links", { description: e?.message });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadRows(); }, [loadRows]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const prepareRow = useCallback(async (idx, infId) => {
    // Optimistically flip to preparing
    setRows((prev) => prev.map((r) => (r.idx === idx ? { ...r, status: "preparing", last_error: null } : r)));
    try {
      const r = await api.post(`/videos/${idx}/prepare`);
      const updated = r.data;
      setRows((prev) => prev.map((row) => (row.idx === idx ? updated : row)));
      if (updated.status === "ready") {
        toast.success(`${infId} ready`, {
          description: `${updated.creator || "unknown"} · ${updated.duration_str}`,
        });
      } else {
        toast.error(`${infId} failed`, { description: updated.last_error || "unknown error" });
      }
      return updated;
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || "prepare failed";
      setRows((prev) => prev.map((row) => (row.idx === idx ? { ...row, status: "error", last_error: msg } : row)));
      toast.error(`${infId} failed`, { description: msg });
    }
  }, []);

  const bulkPrepareAll = useCallback(async () => {
    setBulkPreparing(true);
    const targets = rows.filter((r) => r.status !== "ready" && r.status !== "preparing");
    const tid = toast.loading(`Preparing 0/${targets.length}...`);
    let done = 0, ok = 0, fail = 0;
    // Sequential to be gentle on 3rd-party downloaders
    for (const row of targets) {
      const res = await prepareRow(row.idx, row.inf_id);
      done += 1;
      if (res?.status === "ready") ok += 1; else fail += 1;
      toast.loading(`Preparing ${done}/${targets.length} · ${ok} ready · ${fail} failed`, { id: tid });
    }
    toast.success(`Prepare complete: ${ok} ready · ${fail} failed`, { id: tid });
    setBulkPreparing(false);
  }, [rows, prepareRow]);

  const bulkDownload = useCallback(async (fmt) => {
    setBulkDownloading(true);
    const ready = rows.filter((r) => (fmt === "mp4" ? r.mp4_ready : r.mp3_ready));
    if (ready.length === 0) {
      toast.info(`No ${fmt.toUpperCase()} ready. Click Prepare All first.`);
      setBulkDownloading(false);
      return;
    }
    const tid = toast.loading(`Downloading ${fmt.toUpperCase()} 0/${ready.length}...`);
    for (let i = 0; i < ready.length; i++) {
      const r = ready[i];
      openDownload(r.idx, fmt);
      toast.loading(`Downloading ${fmt.toUpperCase()} ${i + 1}/${ready.length}...`, { id: tid });
      // small delay so browsers don't drop multiple downloads
      await new Promise((res) => setTimeout(res, 700));
    }
    toast.success(`Started ${ready.length} ${fmt.toUpperCase()} downloads`, { id: tid });
    setBulkDownloading(false);
  }, [rows]);

  const resetAll = useCallback(async () => {
    try {
      await api.post("/videos/reset");
      await loadRows();
      toast.success("All rows reset");
    } catch (e) {
      toast.error("Reset failed", { description: e?.message });
    }
  }, [loadRows]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((r) => {
      if (platform !== "all" && r.platform !== platform) return false;
      if (status !== "all" && r.status !== status) return false;
      if (!q) return true;
      return (
        r.inf_id.toLowerCase().includes(q) ||
        r.url.toLowerCase().includes(q) ||
        (r.creator || "").toLowerCase().includes(q)
      );
    });
  }, [rows, query, platform, status]);

  const stats = useMemo(() => ({
    total: rows.length,
    ready: rows.filter((r) => r.status === "ready").length,
    preparing: rows.filter((r) => r.status === "preparing").length,
    errors: rows.filter((r) => r.status === "error").length,
  }), [rows]);

  return (
    <div className="min-h-screen">
      {/* Top Bar */}
      <header className="sticky top-0 z-30 bg-white/95 border-b border-slate-200 backdrop-blur-md">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-sky-500 to-cyan-500 flex items-center justify-center shadow-sm">
              <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
            </div>
            <div className="leading-tight">
              <h1 className="text-lg font-semibold text-slate-900">Content Link Downloader</h1>
              <p className="text-xs text-slate-500">Instagram · TikTok · YouTube · Facebook — MP4 &amp; MP3</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost" size="icon"
              data-testid={TESTIDS.themeToggle}
              onClick={() => setDark((v) => !v)}
              aria-label="Toggle theme"
            >
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* KPI Cards */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KPI title="Total links" value={stats.total} icon={<Video className="h-4 w-4" />} testid={TESTIDS.kpiTotal} />
          <KPI title="Ready" value={stats.ready} tone="success" icon={<CheckCircle2 className="h-4 w-4" />} testid={TESTIDS.kpiReady} />
          <KPI title="Preparing" value={stats.preparing} tone="info" icon={<Loader2 className={`h-4 w-4 ${stats.preparing ? "animate-spin" : ""}`} />} testid={TESTIDS.kpiPreparing} />
          <KPI title="Errors" value={stats.errors} tone="danger" icon={<AlertTriangle className="h-4 w-4" />} testid={TESTIDS.kpiErrors} />
        </section>

        {/* Bulk actions */}
        <section className="rounded-xl bg-white border border-slate-200 shadow-[0_1px_2px_rgba(16,24,40,0.06)] p-3 sm:p-4 flex flex-wrap gap-2 items-center justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <Button
              onClick={bulkPrepareAll} disabled={bulkPreparing}
              className="bg-[#0EA5E9] hover:bg-[#0284C7] active:bg-[#0369A1] text-white shadow-sm"
              data-testid={TESTIDS.bulkPrepareAll}
            >
              {bulkPreparing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
              Prepare All
            </Button>
            <Button
              variant="outline"
              disabled={bulkDownloading}
              onClick={() => bulkDownload("mp4")}
              className="border-[#CFE8F6] text-[#075985] hover:bg-[#F0F9FF]"
              data-testid={TESTIDS.bulkDownloadMp4}
            >
              <Video className="h-4 w-4 mr-2" />
              Download All MP4 <span className="ml-2 text-[11px] text-slate-500">({stats.ready})</span>
            </Button>
            <Button
              variant="outline"
              disabled={bulkDownloading}
              onClick={() => bulkDownload("mp3")}
              className="border-[#CFE8F6] text-[#075985] hover:bg-[#F0F9FF]"
              data-testid={TESTIDS.bulkDownloadMp3}
            >
              <Music2 className="h-4 w-4 mr-2" />
              Download All MP3
            </Button>
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="ghost" className="text-slate-700 hover:bg-slate-100" data-testid={TESTIDS.bulkReset}>
                <Trash2 className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Reset all rows?</AlertDialogTitle>
                <AlertDialogDescription>
                  This clears all cached metadata and downloaded files. The 41 links themselves remain.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel data-testid={TESTIDS.bulkResetCancel}>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={resetAll}
                  className="bg-[#DC2626] hover:bg-[#B91C1C] text-white"
                  data-testid={TESTIDS.bulkResetConfirm}
                >Reset</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </section>

        {/* Filters */}
        <section className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search by INF ID, creator, or URL"
              value={query} onChange={(e) => setQuery(e.target.value)}
              className="pl-9 bg-white" data-testid={TESTIDS.searchInput}
            />
          </div>
          <div className="flex gap-2">
            <Select value={platform} onValueChange={setPlatform}>
              <SelectTrigger className="w-40 bg-white" data-testid={TESTIDS.platformFilter}>
                <Filter className="h-4 w-4 mr-1 text-slate-500" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PLATFORMS.map((p) => (
                  <SelectItem key={p} value={p}>{p === "all" ? "All platforms" : platformLabel(p)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-36 bg-white" data-testid={TESTIDS.statusFilter}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>{s === "all" ? "All statuses" : s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </section>

        {/* Table (desktop) / Cards (mobile) */}
        <section className="rounded-xl bg-white border border-slate-200 shadow-[0_1px_2px_rgba(16,24,40,0.06)] overflow-hidden">
          {/* Desktop */}
          <div className="hidden md:block overflow-x-auto">
            <Table className="min-w-[1100px]">
              <TableHeader className="bg-slate-50 sticky top-0 z-10">
                <TableRow>
                  <TableHead className="w-[90px]">INF ID</TableHead>
                  <TableHead className="w-[110px]">Platform</TableHead>
                  <TableHead className="w-[80px]">Thumb</TableHead>
                  <TableHead>Creator</TableHead>
                  <TableHead className="w-[110px]">Duration</TableHead>
                  <TableHead>Link</TableHead>
                  <TableHead className="w-[110px]">Status</TableHead>
                  <TableHead className="w-[280px] text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading && Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 8 }).map((__, j) => (
                      <TableCell key={j}><Skeleton className="h-6 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))}
                {!loading && filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-16 text-slate-500">
                      No links match your filters.
                    </TableCell>
                  </TableRow>
                )}
                {!loading && filtered.map((row) => (
                  <RowLine
                    key={row.idx} row={row}
                    onPrepare={prepareRow}
                    expandedError={expandedError[row.inf_id]}
                    setExpandedError={(v) => setExpandedError((prev) => ({ ...prev, [row.inf_id]: v }))}
                  />
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Mobile stacked cards */}
          <div className="md:hidden divide-y divide-slate-200">
            {loading && Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="p-4"><Skeleton className="h-24 w-full" /></div>
            ))}
            {!loading && filtered.length === 0 && (
              <div className="p-8 text-center text-slate-500">No links match your filters.</div>
            )}
            {!loading && filtered.map((row) => (
              <RowCard key={row.idx} row={row} onPrepare={prepareRow} />
            ))}
          </div>
        </section>

        {/* Footer info */}
        <footer className="pt-2 pb-8 text-xs text-slate-500 flex flex-wrap gap-x-6 gap-y-2">
          <span>Server-side downloads via public 3rd-party services (fastdl · tikwm · snapsave · pytubefix).</span>
          <span>YouTube stream URLs are IP-locked — if server download fails, use the external opener.</span>
        </footer>
      </main>
    </div>
  );
}

function KPI({ title, value, tone = "neutral", icon, testid }) {
  const toneCls = {
    neutral: "text-slate-700",
    success: "text-emerald-700",
    info: "text-sky-700",
    danger: "text-red-700",
  }[tone];
  return (
    <Card className="kpi-card p-4 bg-white border-slate-200" data-testid={testid}>
      <div className="flex items-center justify-between">
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{title}</div>
        <div className={toneCls}>{icon}</div>
      </div>
      <div className={`mt-2 text-3xl font-semibold tabular-nums ${toneCls}`}>{value}</div>
    </Card>
  );
}

function RowLine({ row, onPrepare, expandedError, setExpandedError }) {
  const stateClass = ({
    pending: "row-pending", preparing: "row-preparing", ready: "row-ready", error: "row-error",
  })[row.status] || "row-pending";

  return (
    <>
      <TableRow className={stateClass}>
        <TableCell className="font-mono text-xs font-semibold text-slate-900">{row.inf_id}</TableCell>
        <TableCell>
          <Badge variant="outline" className={`text-xs ${platformBadgeClasses(row.platform)} font-medium`}>
            {platformLabel(row.platform)}
          </Badge>
        </TableCell>
        <TableCell>
          {row.thumbnail ? (
            <HoverCard openDelay={200}>
              <HoverCardTrigger asChild>
                <img
                  src={row.thumbnail} alt="thumb"
                  className="h-14 w-14 rounded-md object-cover border border-slate-200 bg-slate-100 cursor-pointer"
                  data-testid={TESTIDS.rowThumbnail(row.inf_id)}
                  onError={(e) => { e.currentTarget.style.display = "none"; }}
                />
              </HoverCardTrigger>
              <HoverCardContent className="w-60 p-2 bg-white">
                <img src={row.thumbnail} alt="preview" className="w-full rounded-md" />
              </HoverCardContent>
            </HoverCard>
          ) : (
            <Skeleton className="h-14 w-14 rounded-md" />
          )}
        </TableCell>
        <TableCell>
          <div className="text-sm font-medium text-slate-900 truncate max-w-[220px]" title={row.creator || ""}>
            {row.creator || <span className="text-slate-400">—</span>}
          </div>
        </TableCell>
        <TableCell>
          <span className="font-mono tabular-nums text-sm text-slate-700">{row.duration_str || "[0:00:00]"}</span>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-1 max-w-[300px]">
            <a href={row.url} target="_blank" rel="noopener noreferrer" className="text-xs text-sky-700 hover:underline truncate" title={row.url}>
              {row.url}
            </a>
            <Button
              variant="ghost" size="icon" className="h-7 w-7 shrink-0"
              onClick={() => { 
                try {
                  navigator.clipboard.writeText(row.url).then(() => {
                    toast.success("Link copied");
                  }).catch(() => {
                    toast.info("Link: " + row.url, { description: "Copy manually" });
                  });
                } catch (e) {
                  toast.info("Link: " + row.url, { description: "Copy manually" });
                }
              }}
              data-testid={TESTIDS.rowCopyLink(row.inf_id)}
              aria-label="Copy link"
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
        </TableCell>
        <TableCell>
          <StatusChip status={row.status} infId={row.inf_id} />
        </TableCell>
        <TableCell className="text-right">
          <RowActions row={row} onPrepare={onPrepare} />
        </TableCell>
      </TableRow>
      {row.status === "error" && row.last_error && (
        <TableRow className={`${stateClass} border-t-0`}>
          <TableCell colSpan={8} className="pt-0 pb-3">
            <Collapsible open={!!expandedError} onOpenChange={setExpandedError}>
              <CollapsibleTrigger asChild>
                <button
                  className="text-xs text-red-700 hover:underline inline-flex items-center gap-1"
                  data-testid={TESTIDS.rowErrorExpand(row.inf_id)}
                >
                  {expandedError ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                  {expandedError ? "Hide error" : "Show error details"}
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="mt-2 text-xs font-mono bg-[#FFF7ED] border border-[#FED7AA] rounded-md p-2 text-slate-800">
                  {row.last_error}
                </div>
              </CollapsibleContent>
            </Collapsible>
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

function RowCard({ row, onPrepare }) {
  const stateClass = ({
    pending: "row-pending", preparing: "row-preparing", ready: "row-ready", error: "row-error",
  })[row.status] || "row-pending";
  return (
    <div className={`p-4 ${stateClass}`}>
      <div className="flex items-start gap-3">
        {row.thumbnail ? (
          <img src={row.thumbnail} alt="thumb" className="h-14 w-14 rounded-md object-cover border border-slate-200 shrink-0"
               onError={(e) => { e.currentTarget.style.display = "none"; }} />
        ) : (
          <Skeleton className="h-14 w-14 rounded-md shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs font-semibold">{row.inf_id}</span>
            <Badge variant="outline" className={`text-[10px] ${platformBadgeClasses(row.platform)} font-medium`}>
              {platformLabel(row.platform)}
            </Badge>
            <StatusChip status={row.status} infId={row.inf_id} />
          </div>
          <div className="text-sm font-medium text-slate-900 truncate">{row.creator || "—"}</div>
          <div className="text-xs font-mono text-slate-600">{row.duration_str}</div>
          <a href={row.url} target="_blank" rel="noopener noreferrer" className="text-[11px] text-sky-700 hover:underline block truncate">{row.url}</a>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <RowActions row={row} onPrepare={onPrepare} compact />
      </div>
      {row.status === "error" && row.last_error && (
        <div className="mt-2 text-xs font-mono bg-[#FFF7ED] border border-[#FED7AA] rounded-md p-2 text-slate-800">
          {row.last_error}
        </div>
      )}
    </div>
  );
}
