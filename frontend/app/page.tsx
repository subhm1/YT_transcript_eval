"use client";

import { useState } from "react";

import Pipeline from "./components/Pipeline";
import Summary from "./components/Summary";
import Evaluation from "./components/Evaluation";

import type {
  Metrics,
  PipelineEvent,
  Stage,
  MapProgress,
  EvaluationResult,
} from "./components/types";

const engineeringTags = [
  "MAP-REDUCE",
  "EVALUATION",
  "TOKEN METRICS",
  "LATENCY",
];

export default function Home() {
  const [url, setUrl] = useState("");

  const [stage, setStage] = useState<Stage>("idle");
  const [message, setMessage] = useState("");

  const [summary, setSummary] = useState("");
  const [metrics, setMetrics] = useState<Metrics>({});

  const [error, setError] = useState("");

  const [mapProgress, setMapProgress] = useState<MapProgress>({
    current: 0,
    total: 0,
  });

  const [evaluationLoading, setEvaluationLoading] =
    useState(false);

  const [evaluationResult, setEvaluationResult] =
    useState<EvaluationResult | null>(null);

  const [evaluationError, setEvaluationError] =
    useState("");

  const isRunning =
    stage !== "idle" &&
    stage !== "complete" &&
    stage !== "error";

  function extractVideoId(videoUrl: string): string | null {
    try {
      const parsedUrl = new URL(videoUrl);

      if (parsedUrl.hostname.includes("youtu.be")) {
        return parsedUrl.pathname.slice(1) || null;
      }

      if (
        parsedUrl.hostname.includes("youtube.com") ||
        parsedUrl.hostname.includes("www.youtube.com")
      ) {
        return parsedUrl.searchParams.get("v");
      }

      return null;
    } catch {
      return null;
    }
  }

  async function evaluateSummary(
    videoId: string,
    generatedSummary: string
  ) {
    setEvaluationLoading(true);
    setEvaluationResult(null);
    setEvaluationError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/evaluate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            video_id: videoId,
            generated_summary: generatedSummary,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Evaluation failed."
        );
      }

      if (!data.evaluation) {
        throw new Error(
          "Evaluation response did not contain results."
        );
      }

      setEvaluationResult(data.evaluation);
    } catch (err) {
      setEvaluationError(
        err instanceof Error
          ? err.message
          : "Evaluation failed."
      );
    } finally {
      setEvaluationLoading(false);
    }
  }

  async function summarize() {
    setStage("fetch");
    setMessage("Starting pipeline...");

    setSummary("");
    setMetrics({});
    setError("");

    setMapProgress({
      current: 0,
      total: 0,
    });

    setEvaluationLoading(false);
    setEvaluationResult(null);
    setEvaluationError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/summarize/stream",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url }),
        }
      );

      if (!response.ok || !response.body) {
        throw new Error(
          "Failed to connect to summarization API."
        );
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let pipelineVideoId: string | null = null;
      let finalSummary = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const events = buffer.split("\n\n");

        buffer = events.pop() ?? "";

        for (const event of events) {
          const line = event
            .split("\n")
            .find((line) => line.startsWith("data:"));

          if (!line) {
            continue;
          }

          const rawData = line
            .replace(/^data:\s*/, "")
            .trim();

          if (!rawData) {
            continue;
          }

          const data: PipelineEvent =
            JSON.parse(rawData);

          if (data.stage) {
            setStage(data.stage);
          }

          if (data.message) {
            setMessage(data.message);
          }

          if (
            data.current !== undefined &&
            data.total !== undefined
          ) {
            setMapProgress({
              current: data.current,
              total: data.total,
            });
          }

          if (data.status === "error") {
            throw new Error(
              data.message || "Pipeline failed."
            );
          }

          if (data.result) {
            if (data.result.summary !== undefined) {
              finalSummary = data.result.summary;

              setSummary(data.result.summary);
            }

            if (data.result.metrics) {
              setMetrics(data.result.metrics);
            }

            if (data.result.video_id) {
              pipelineVideoId =
                data.result.video_id;
            }
          }
        }
      }

      setStage("complete");
      setMessage("Pipeline complete.");

      /*
       * The pipeline should ideally return video_id.
       * If it does not, extract it from the submitted URL.
       */
      const videoId =
        pipelineVideoId || extractVideoId(url);

      if (videoId && finalSummary) {
        await evaluateSummary(
          videoId,
          finalSummary
        );
      } else {
        setEvaluationError(
          "Could not determine the video ID for evaluation."
        );
      }
    } catch (err) {
      setStage("error");

      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    }
  }

  return (
    <main className="h-screen overflow-hidden bg-black font-sans text-white">
      <div className="mx-auto flex h-full max-w-[1600px] flex-col px-6 py-6">
        {/* HEADER */}
        <header className="shrink-0">
          <div className="mb-3 flex flex-wrap gap-2">
            {engineeringTags.map((tag) => (
              <span
                key={tag}
                className="
                  rounded-full
                  border
                  border-zinc-700
                  px-3
                  py-1
                  text-[10px]
                  font-bold
                  tracking-wide
                  text-zinc-100
                "
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mb-1 text-[10px] font-bold tracking-[0.2em] text-zinc-500">
            TRANSCRIPT INTELLIGENCE
          </div>

          <h1 className="text-4xl font-bold tracking-[-0.04em] text-white">
            YouTube Video → Summary
          </h1>

          <p className="mt-2 max-w-3xl text-sm font-medium leading-6 text-zinc-400">
            A framework-light transcript processing
            pipeline with explicit chunking, map-reduce
            summarization, token accounting, latency
            tracking, and evaluation.
          </p>
        </header>

        {/* URL INPUT */}
        <section
          className="
            mt-4
            shrink-0
            rounded-xl
            border
            border-zinc-800
            bg-zinc-950
            p-3
          "
        >
          <div className="flex gap-2">
            <input
              value={url}
              onChange={(e) =>
                setUrl(e.target.value)
              }
              onKeyDown={(e) => {
                if (
                  e.key === "Enter" &&
                  url &&
                  !isRunning
                ) {
                  summarize();
                }
              }}
              placeholder="Paste a YouTube URL"
              className="
                min-w-0
                flex-1
                rounded-lg
                border
                border-zinc-800
                bg-black
                px-4
                py-3
                text-sm
                font-medium
                text-white
                outline-none
                placeholder:text-zinc-600
                focus:border-zinc-500
              "
            />

            <button
              onClick={summarize}
              disabled={!url || isRunning}
              className="
                rounded-lg
                bg-white
                px-6
                py-3
                text-xs
                font-bold
                text-black
                transition
                hover:bg-zinc-200
                disabled:cursor-not-allowed
                disabled:opacity-40
              "
            >
              {isRunning
                ? "Running..."
                : "Summarize"}
            </button>
          </div>
        </section>

        {/* MAIN TWO-COLUMN AREA */}
        <section
          className="
            mt-4
            grid
            min-h-0
            flex-1
            grid-cols-2
            gap-4
          "
        >
          {/* LEFT HALF */}
          <div className="min-h-0 overflow-hidden">
            {stage !== "idle" ? (
              <Pipeline
                stage={stage}
                message={message}
                mapProgress={mapProgress}
              />
            ) : (
              <div
                className="
                  flex
                  h-full
                  items-center
                  justify-center
                  rounded-2xl
                  border
                  border-zinc-800
                  bg-zinc-950
                  text-center
                "
              >
                <div>
                  <div className="text-xs font-bold tracking-[0.2em] text-zinc-600">
                    PIPELINE
                  </div>

                  <div className="mt-2 text-sm font-medium text-zinc-500">
                    Enter a YouTube URL to begin.
                  </div>
                </div>
              </div>
            )}

            {error && (
              <section
                className="
                  mt-3
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
              </section>
            )}
          </div>

          {/* RIGHT HALF */}
          <div className="min-h-0 overflow-hidden">
            <div className="flex h-full min-h-0 flex-col overflow-y-auto pr-1">
              {/* SUMMARY */}
              {summary ? (
                <Summary
                  summary={summary}
                  metrics={metrics}
                />
              ) : (
                <section
                  className="
                    flex
                    min-h-[220px]
                    items-center
                    justify-center
                    rounded-2xl
                    border
                    border-zinc-800
                    bg-zinc-950
                    p-8
                  "
                >
                  <div className="text-center">
                    <div className="text-xs font-bold tracking-[0.2em] text-zinc-600">
                      GENERATED SUMMARY
                    </div>

                    <div className="mt-2 text-sm font-medium text-zinc-500">
                      Summary will appear here.
                    </div>
                  </div>
                </section>
              )}

              {/* EVALUATION */}
              <div className="mt-3 shrink-0">
                <Evaluation
                  loading={evaluationLoading}
                  result={evaluationResult}
                  error={evaluationError}
                />
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}