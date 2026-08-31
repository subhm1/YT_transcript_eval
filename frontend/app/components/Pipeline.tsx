"use client";

import type { MapProgress, Stage } from "./types";

const stages = [
  { id: "fetch", label: "Fetch transcript" },
  { id: "normalize", label: "Normalize & clean" },
  { id: "tokenize", label: "Count tokens" },
  { id: "chunk", label: "Create chunks" },
  { id: "map", label: "Map · summarize chunks" },
  { id: "reduce", label: "Reduce · final summary" },
] as const;

type Props = {
  stage: Stage;
  message: string;
  mapProgress: MapProgress;
};

export default function Pipeline({
  stage,
  message,
  mapProgress,
}: Props) {
  const activeIndex = stages.findIndex(
    (item) => item.id === stage
  );

  const completedStages =
    stage === "complete"
      ? stages.length
      : Math.max(activeIndex, 0);

  const progress =
    stage === "complete"
      ? 100
      : stage === "error"
        ? (completedStages / stages.length) * 100
        : ((completedStages + 0.5) / stages.length) * 100;

  return (
    <section
      className="
        mt-8
        rounded-2xl
        border
        border-zinc-800
        bg-zinc-950
        p-7
      "
    >
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="text-xs font-bold tracking-[0.2em] text-zinc-500">
            PIPELINE
          </div>

          <div className="mt-2 text-sm font-semibold text-zinc-300">
            {message}
          </div>
        </div>

        <div className="text-xs font-bold tracking-wider text-zinc-500">
          {stage === "complete"
            ? "6 / 6"
            : `${Math.max(activeIndex + 1, 1)} / ${stages.length}`}
        </div>
      </div>

      <div className="mb-7">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs font-semibold text-zinc-600">
            PIPELINE PROGRESS
          </span>

          <span className="text-xs font-semibold text-zinc-500">
            {Math.round(progress)}%
          </span>
        </div>

        <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-900">
          <div
            className="
              h-full
              rounded-full
              bg-white
              transition-all
              duration-700
              ease-out
            "
            style={{
              width: `${Math.min(progress, 100)}%`,
            }}
          />
        </div>
      </div>

      <div className="space-y-3">
        {stages.map((item, index) => {
          const isActive = item.id === stage;

          const isDone =
            stage === "complete" ||
            index < activeIndex;

          const isPending =
            !isActive && !isDone;

          return (
            <div
              key={item.id}
              className={`
                flex
                items-center
                gap-4
                rounded-xl
                border
                px-5
                py-4
                transition-all
                duration-300
                ${
                  isActive
                    ? "border-zinc-700 bg-zinc-900/70"
                    : "border-zinc-900 bg-black"
                }
              `}
            >
              <div
                className="
                  flex
                  h-5
                  w-5
                  shrink-0
                  items-center
                  justify-center
                "
              >
                {isActive && (
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
                )}

                {isDone && !isActive && (
                  <div
                    className="
                      flex
                      h-5
                      w-5
                      items-center
                      justify-center
                      rounded-full
                      bg-emerald-500
                    "
                  >
                    <svg
                      viewBox="0 0 24 24"
                      className="h-3 w-3 text-black"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m5 12 4 4L19 6" />
                    </svg>
                  </div>
                )}

                {isPending && (
                  <div
                    className="
                      h-2.5
                      w-2.5
                      rounded-full
                      bg-zinc-800
                    "
                  />
                )}
              </div>

              <span
                className={`
                  text-base
                  font-semibold
                  transition-colors
                  ${
                    isActive || isDone
                      ? "text-white"
                      : "text-zinc-600"
                  }
                `}
              >
                {item.label}
              </span>

              {item.id === "map" &&
                isActive &&
                mapProgress.total > 0 && (
                  <span className="ml-auto text-xs font-bold tracking-wide text-zinc-500">
                    {mapProgress.current} /{" "}
                    {mapProgress.total} chunks
                  </span>
                )}

              {isActive &&
                !(
                  item.id === "map" &&
                  mapProgress.total > 0
                ) && (
                  <span className="ml-auto text-xs font-bold uppercase tracking-wider text-zinc-500">
                    running
                  </span>
                )}

              {isDone && !isActive && (
                <span className="ml-auto text-xs font-bold uppercase tracking-wider text-emerald-500">
                  done
                </span>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}