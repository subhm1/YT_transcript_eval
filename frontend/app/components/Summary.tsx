"use client";

import type { Metrics } from "./types";

type Props = {
  summary: string;
  metrics: Metrics;
};

export default function Summary({
  summary,
  metrics,
}: Props) {
  const hasMetrics = Object.keys(metrics).length > 0;

  return (
    <section
      className="
        rounded-2xl
        border
        border-zinc-800
        bg-zinc-950
        p-6
      "
    >
      <div className="mb-4 text-[10px] font-bold tracking-[0.2em] text-zinc-500">
        GENERATED SUMMARY
      </div>

      <div
        className="
          max-h-[220px]
          overflow-hidden
          whitespace-pre-wrap
          text-sm
          font-medium
          leading-6
          text-zinc-200
        "
      >
        {summary}
      </div>

      {hasMetrics && (
        <div className="mt-6">
          <div className="mb-3 text-[10px] font-bold tracking-[0.2em] text-zinc-500">
            TOKEN / LATENCY METRICS
          </div>

          <div
            className="
              grid
              grid-cols-5
              overflow-hidden
              rounded-xl
              border
              border-zinc-800
            "
          >
            <Metric
              label="TOKENS"
              value={metrics.transcript_tokens}
            />

            <Metric
              label="CHUNKS"
              value={metrics.number_of_chunks}
            />

            <Metric
              label="MAP CALLS"
              value={metrics.map_calls}
            />

            <Metric
              label="REDUCE"
              value={metrics.reduce_input_tokens}
            />

            <Metric
              label="LATENCY"
              value={
                metrics.execution_time_seconds !== undefined
                  ? `${metrics.execution_time_seconds}s`
                  : undefined
              }
            />
          </div>
        </div>
      )}
    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string | number | undefined;
}) {
  return (
    <div className="bg-black px-3 py-3">
      <div className="text-[9px] font-bold tracking-[0.12em] text-zinc-600">
        {label}
      </div>

      <div className="mt-1 text-sm font-bold text-zinc-200">
        {value ?? "—"}
      </div>
    </div>
  );
}