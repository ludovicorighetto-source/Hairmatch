"use client";

interface MatchScoreBadgeProps {
  score: number; // 0–1
  size?: "sm" | "md";
}

function scoreColor(score: number): string {
  if (score >= 0.75) return "bg-green-100 text-green-700 border-green-200";
  if (score >= 0.50) return "bg-yellow-100 text-yellow-700 border-yellow-200";
  return "bg-gray-100 text-gray-600 border-gray-200";
}

export function MatchScoreBadge({ score, size = "md" }: MatchScoreBadgeProps) {
  const pct = Math.round(score * 100);
  const color = scoreColor(score);
  const sizeClass = size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-semibold ${color} ${sizeClass}`}
      title={`Match score: ${pct}%`}
    >
      <span className="tabular-nums">{pct}%</span>
      <span className="text-xs font-normal opacity-70">match</span>
    </span>
  );
}
