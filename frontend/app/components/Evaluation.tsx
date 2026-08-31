"use client";

import type { EvaluationResult } from "./types";

type EvaluationProps = {
  loading: boolean;
  result: EvaluationResult | null;
  error: string;
};

export default function Evaluation({
  loading,
  result,
  error,
}: EvaluationProps) {
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
      <div className="mb-2 text-[10px] font-bold tracking-[0.2em] text-zinc-500">
        EVALUATION
      </div>

      <h2 className="text-lg font-bold tracking-tight text-white">
        Summary quality is measured.
      </h2>

      <p className="mt-2 text-xs font-medium leading-5 text-zinc-500">
        LLM judge evaluation against the reference benchmark.
      </p>

      {/* LOADING */}
      {loading && (
        <div className="mt-5 rounded-xl border border-zinc-800 bg-black p-4">
          <div className="flex items-center gap-3">
            <div
              className="
                h-4
                w-4
                animate-spin
                rounded-full
                border-2
                border-zinc-700
                border-t-white
              "
            />

            <div>
              <div className="text-sm font-bold text-white">
                Evaluating summary
              </div>

              <div className="mt-1 text-[11px] text-zinc-500">
                Running LLM judge...
              </div>
            </div>
          </div>

          <div className="mt-4 h-1 overflow-hidden rounded-full bg-zinc-900">
            <div
              className="
                h-full
                w-1/3
                animate-[evaluation-progress_1.5s_ease-in-out_infinite]
                rounded-full
                bg-white
              "
            />
          </div>
        </div>
      )}

      {/* ERROR */}
      {error && (
        <div
          className="
            mt-5
            rounded-xl
            border
            border-red-900/50
            bg-red-950/20
            p-4
            text-xs
            font-semibold
            text-red-300
          "
        >
          {error}
        </div>
      )}

      {/* RESULTS */}
      {!loading && !error && result && (
        <>
          {/* DIMENSIONS */}
          <div className="mt-5 grid grid-cols-3 gap-2">
            <EvaluationMetric
              label="COVERAGE"
              description="Important information"
            />

            <EvaluationMetric
              label="FAITHFULNESS"
              description="Supported claims"
            />

            <EvaluationMetric
              label="CONCISENESS"
              description="Avoids unnecessary detail"
            />
          </div>

          {/* SCORES */}
          <div className="mt-5">
            <div className="mb-3 text-[10px] font-bold tracking-[0.2em] text-zinc-500">
              JUDGE RESULTS
            </div>

            <div className="grid grid-cols-4 gap-2">
              <ScoreCard
                label="COVERAGE"
                score={result.coverage}
              />

              <ScoreCard
                label="FAITHFULNESS"
                score={result.faithfulness}
              />

              <ScoreCard
                label="CONCISENESS"
                score={result.conciseness}
              />

              <ScoreCard
                label="OVERALL"
                score={result.overall}
              />
            </div>
          </div>

          {/* REASON */}
          <div
            className="
              mt-3
              rounded-xl
              border
              border-zinc-800
              bg-black
              p-4
            "
          >
            <div className="text-[10px] font-bold tracking-[0.18em] text-zinc-500">
              JUDGE REASON
            </div>

            <p className="mt-2 text-xs font-medium leading-5 text-zinc-300">
              {result.reason}
            </p>
          </div>
        </>
      )}

      {/* INITIAL STATE */}
      {!loading && !error && !result && (
        <div
          className="
            mt-5
            rounded-xl
            border
            border-dashed
            border-zinc-800
            bg-black
            p-5
            text-center
            text-xs
            font-medium
            text-zinc-600
          "
        >
          Evaluation will appear after summarization.
        </div>
      )}
    </section>
  );
}

function EvaluationMetric({
  label,
  description,
}: {
  label: string;
  description: string;
}) {
  return (
    <div
      className="
        rounded-xl
        border
        border-zinc-800
        bg-black
        p-3
      "
    >
      <div className="text-[10px] font-bold text-white">
        {label}
      </div>

      <p className="mt-1 text-[10px] leading-4 text-zinc-500">
        {description}
      </p>
    </div>
  );
}

function ScoreCard({
  label,
  score,
}: {
  label: string;
  score: number;
}) {
  return (
    <div
      className="
        rounded-xl
        border
        border-zinc-800
        bg-black
        p-3
      "
    >
      <div className="text-[9px] font-bold tracking-[0.12em] text-zinc-500">
        {label}
      </div>

      <div className="mt-1 flex items-baseline gap-1">
        <span className="text-2xl font-bold text-white">
          {score}
        </span>

        <span className="text-[10px] text-zinc-600">
          / 5
        </span>
      </div>
    </div>
  );
}