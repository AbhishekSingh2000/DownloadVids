import React from "react";
import { Button } from "@/components/ui/button";
import { Loader2, Download, RefreshCw, Video, Music2, ExternalLink } from "lucide-react";
import { TESTIDS } from "@/constants/testIds";
import { openDownload } from "@/lib/api";
import { toast } from "sonner";

const EXTERNAL_HELPER = {
  instagram: "https://fastdl.app/en",
  tiktok: "https://www.tikwm.com/",
  youtube: "https://ymp4.download/en/",
  facebook: "https://snapsave.app/",
  linkedin: "https://iloveyt.net/en/linkedin-video-downloader",
};

export default function RowActions({ row, onPrepare, compact = false }) {
  const { status, inf_id, idx, mp4_ready, mp3_ready, platform, url } = row;

  const openHelper = async () => {
    try {
      await navigator.clipboard.writeText(url);
      toast.info("URL copied — paste it on the opened site", { description: url });
    } catch {}
    window.open(EXTERNAL_HELPER[platform] || url, "_blank", "noopener,noreferrer");
  };

  if (status === "pending") {
    return (
      <div className={compact ? "flex flex-wrap gap-2 w-full" : "flex flex-wrap gap-2 justify-end"}>
        <Button
          size="sm"
          className="bg-[#0EA5E9] hover:bg-[#0284C7] active:bg-[#0369A1] text-white shadow-sm"
          onClick={() => onPrepare(idx, inf_id)}
          data-testid={TESTIDS.rowPrepare(inf_id)}
        >
          <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
          Prepare
        </Button>
      </div>
    );
  }

  if (status === "preparing") {
    return (
      <div className={compact ? "flex flex-wrap gap-2 w-full" : "flex flex-wrap gap-2 justify-end"}>
        <Button size="sm" disabled className="bg-sky-100 text-sky-800">
          <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
          Preparing…
        </Button>
      </div>
    );
  }

  return (
    <div className={compact ? "flex flex-wrap gap-2 w-full" : "flex flex-wrap gap-2 justify-end"}>
      <Button
        variant="outline" size="sm"
        disabled={!mp4_ready}
        className="border-[#CFE8F6] text-[#075985] hover:bg-[#F0F9FF] disabled:opacity-40"
        onClick={() => openDownload(idx, "mp4")}
        data-testid={TESTIDS.rowDownloadMp4(inf_id)}
      >
        <Video className="h-3.5 w-3.5 mr-1.5" />
        MP4
      </Button>
      <Button
        variant="outline" size="sm"
        disabled={!mp3_ready}
        className="border-[#CFE8F6] text-[#075985] hover:bg-[#F0F9FF] disabled:opacity-40"
        onClick={() => openDownload(idx, "mp3")}
        data-testid={TESTIDS.rowDownloadMp3(inf_id)}
      >
        <Music2 className="h-3.5 w-3.5 mr-1.5" />
        MP3
      </Button>
      {(!mp4_ready || !mp3_ready) && (
        <Button
          variant="ghost" size="sm"
          className="text-slate-700 hover:bg-slate-100"
          onClick={openHelper}
          data-testid={TESTIDS.rowOpenExternal(inf_id)}
          title="Open in browser downloader (URL will be copied)"
        >
          <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
          Open
        </Button>
      )}
      <Button
        variant="ghost" size="sm"
        className="text-slate-700 hover:bg-slate-100"
        onClick={() => onPrepare(idx, inf_id)}
        data-testid={TESTIDS.rowRetry(inf_id)}
      >
        <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
        {status === "error" ? "Retry" : "Refresh"}
      </Button>
    </div>
  );
}
