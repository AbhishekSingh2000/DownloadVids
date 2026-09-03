// Central place for API config + helpers
import axios from "axios";

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API, timeout: 180000 });

export const platformLabel = (p) => ({
  instagram: "Instagram",
  tiktok: "TikTok",
  youtube: "YouTube",
  facebook: "Facebook",
  linkedin: "LinkedIn",
}[p] || p);

export const platformBadgeClasses = (p) => ({
  instagram: "bg-[#FFF1F7] text-[#9D174D] border border-[#FBCFE8]",
  tiktok:    "bg-[#ECFEFF] text-[#155E75] border border-[#A5F3FC]",
  youtube:   "bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]",
  facebook:  "bg-[#EFF6FF] text-[#1D4ED8] border border-[#BFDBFE]",
  linkedin:  "bg-[#EFF6FF] text-[#075985] border border-[#7DD3FC]",
}[p] || "bg-slate-100 text-slate-700 border border-slate-200");

export const countryBadgeClasses = (c) => ({
  Germany: "bg-[#FEF3C7] text-[#78350F] border border-[#FDE68A]",
  Italy:   "bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]",
}[c] || "bg-slate-100 text-slate-700 border border-slate-200");

export const countryFlag = (c) => ({
  Germany: "🇩🇪",
  Italy:   "🇮🇹",
}[c] || "");

export const statusChipClasses = (s) => ({
  pending:    "bg-slate-100 text-slate-700",
  preparing:  "bg-sky-100 text-sky-800",
  ready:      "bg-emerald-100 text-emerald-800",
  error:      "bg-red-100 text-red-800",
}[s] || "bg-slate-100 text-slate-700");

export const rowStateClass = (s) => ({
  pending: "row-pending",
  preparing: "row-preparing",
  ready: "row-ready",
  error: "row-error",
}[s] || "row-pending");

export const openDownload = async (idx, fmt) => {
  // Trigger a browser download by navigating to the endpoint
  const url = `${API}/videos/${idx}/download?fmt=${fmt}`;
  const a = document.createElement("a");
  a.href = url;
  a.rel = "noopener noreferrer";
  a.target = "_self";
  a.click();
};

export const buildFilename = (creator, infId, durSec, ext) => {
  const safe = (creator || "unknown").replace(/[^A-Za-z0-9._-]/g, "_").replace(/^_+|_+$/g, "") || "unknown";
  const s = Math.max(0, parseInt(durSec || 0, 10));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, "0");
  const sec = (s % 60).toString().padStart(2, "0");
  return `${safe}_${infId}_[${h}:${m}:${sec}].${ext}`;
};
