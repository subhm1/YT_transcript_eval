# YT Transcript Eval

A production-style YouTube transcript summarization and evaluation system built to explore the engineering challenges behind LLM-powered summarization.

Instead of sending an entire transcript to an LLM in one request, the system explicitly handles transcript ingestion, token accounting, intelligent chunking, Map-Reduce summarization, structured LLM output, evaluation, streaming execution, and observable metrics.

The project is intentionally framework-light and focuses on understanding and implementing the underlying system rather than hiding the pipeline behind an orchestration framework.

## Architecture

```text
                    YouTube URL
                         │
                         ▼
                 Extract Video ID
                         │
                         ▼
                Fetch Transcript
                         │
                         ▼
                Normalize + Clean
                         │
                         ▼
                  Token Counting
                         │
                         ▼
              Intelligent Chunking
                         │
                         ▼
              ┌───────────────────┐
              │    MAP PHASE      │
              │                   │
              │ Chunk 1 → Summary │
              │ Chunk 2 → Summary │
              │ Chunk 3 → Summary │
              │       ...         │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │   REDUCE PHASE    │
              │                   │
              │ Chunk summaries   │
              │       ↓           │
              │ Final JSON output │
              └─────────┬─────────┘
                        │
                        ▼
                Final Summary
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
          Metrics              Evaluation
                                   │
                                   ▼
                           LLM-as-a-Judge
                                   │
                                   ▼
                     Coverage / Faithfulness /
                         Conciseness / Overall
```

For the application layer:

```text
Next.js Frontend
       │
       │ SSE
       ▼
FastAPI Backend
       │
       ▼
Python Pipeline
       │
       ├── Transcript processing
       ├── Tokenization
       ├── Chunking
       ├── Map
       └── Reduce
```

## Why Map-Reduce?

A long transcript should not simply be placed into a single LLM request.

That approach creates several problems:

* Context-window constraints
* Larger requests
* Higher latency
* Less predictable token usage
* Increased cost when using hosted models
* Reduced control over intermediate processing

This project therefore separates summarization into two stages.

### Map

Each transcript chunk is summarized independently.

```text
Transcript
    ↓
Chunk 1 → Summary 1
Chunk 2 → Summary 2
Chunk 3 → Summary 3
...
```

Because the chunks are processed independently, the Map stage can also be parallelized later if required.

### Reduce

The individual summaries are combined into a final summary.

```text
Summary 1
Summary 2
Summary 3
...
    ↓
Reduce
    ↓
Final Summary
```

The Reduce stage does not receive the original transcript. It works from the intermediate summaries produced during Map.

## LLM Architecture

The current local inference pipeline uses:

* Ollama
* Qwen3 4B
* `think=False`
* Structured JSON output for the reducer
* Deterministic temperature configuration

The reducer requests output in the following form:

```json
{
  "bullets": [
    "Important point one",
    "Important point two",
    "Important point three"
  ]
}
```

The application does not blindly trust the model output.

The reducer validates:

* JSON validity
* Object structure
* Required `bullets` field
* Bullet count
* Non-empty bullet strings

Only validated output is converted into the final summary.

## Transcript Processing

The transcript layer is deliberately separated from the LLM layer.

The processing flow is:

```text
YouTube URL
    ↓
Video ID extraction
    ↓
Transcript retrieval
    ↓
Normalization
    ↓
Mechanical cleaning
    ↓
Token counting
    ↓
Chunking
```

Transcript segments are normalized into an internal representation containing:

```python
{
    "start": ...,
    "duration": ...,
    "text": ...
}
```

This prevents the rest of the application from depending directly on the transcript library's internal objects.

The cleaning stage is intentionally conservative.

It performs mechanical operations such as whitespace normalization and removal of musical-note characters, but does not attempt to rewrite or "correct" the transcript.

This is important because an automatic transcript is source data. Silently correcting ASR output could change the information being evaluated.

## Intelligent Chunking

The chunker operates under a token budget rather than an arbitrary character limit.

Current configuration targets:

```text
Maximum chunk size: 1000 tokens
Overlap:            100 tokens
```

The chunker attempts to preserve meaningful boundaries while ensuring that chunks remain within the configured token budget.

For example, a real transcript produced:

```text
Transcript tokens: 4903
Chunks:            6
```

with individual chunk sizes remaining within the configured limit.

## Metrics

The pipeline exposes engineering metrics rather than returning only a final text summary.

Current metrics include:

```text
transcript_tokens
number_of_chunks
map_calls
reduce_input_tokens
execution_time_seconds
```

Example:

```text
transcript_tokens:       3816
number_of_chunks:        5
map_calls:               5
reduce_input_tokens:     740
execution_time_seconds:  62.31
```

These metrics make it possible to reason about how transcript length, chunking, LLM calls, and latency interact.

## Evaluation

A summarization system should not be considered successful simply because it produces plausible-looking text.

This project therefore includes a benchmark dataset and an LLM-as-a-judge evaluation pipeline.

The current benchmark contains four videos covering different transcript characteristics.

| Video                                    | Reference          | Transcript Type | Length |
| ---------------------------------------- | ------------------ | --------------- | ------ |
| The Danger of a Single Story             | TED                | Manual          | Medium |
| Your Body Language May Shape Who You Are | TED                | Manual          | Medium |
| The History of Our World in 18 Minutes   | TED                | Manual          | Short  |
| The Power of Vulnerability               | Brené Brown / TEDx | Auto            | Medium |

Reference summaries are based on independently available descriptions rather than summaries generated by this system.

### Evaluation dimensions

The judge evaluates four scores.

#### Coverage

Does the generated summary capture the important information represented by the reference?

#### Faithfulness

Are the claims in the generated summary supported by the available source material?

#### Conciseness

Does the summary communicate the information without unnecessary repetition or detail?

#### Overall

An overall assessment of the generated summary.

The judge also returns a textual reason explaining its assessment.

### Current benchmark results

The latest aggregate results are:

```text
Coverage:       3.50 / 5
Faithfulness:   3.75 / 5
Conciseness:    4.50 / 5
Overall:        3.50 / 5
```

These results are intentionally reported rather than hidden.

The evaluation showed that the system produces reasonably concise summaries, while coverage and faithfulness still have room for improvement.

This is an important part of the project: the evaluation harness exposed limitations in the summarization system instead of simply demonstrating successful examples.

## Evaluation Pipeline

```text
Benchmark Dataset
       │
       ▼
Run Summarization Pipeline
       │
       ▼
Generated Summaries
       │
       ▼
LLM-as-a-Judge
       │
       ├── Coverage
       ├── Faithfulness
       ├── Conciseness
       └── Overall
       │
       ▼
CSV Results
       │
       ▼
Pandas Analysis
```

The evaluation code is located under:

```text
evaluation/
```

Relevant files include:

```text
evaluation/
├── dataset.csv
├── generated_results.csv
├── judge_results.csv
├── judge.py
├── run_evaluation.py
├── run_judge.py
├── analyze_results.py
└── transcripts/
```

## Streaming Pipeline

The backend exposes a streaming version of the pipeline.

Instead of waiting silently for the entire process to finish, the frontend receives pipeline events as processing progresses.

Stages include:

```text
fetch
normalize
chunk
map
reduce
complete
```

Example event:

```json
{
  "stage": "fetch",
  "status": "running",
  "message": "Fetching transcript"
}
```

The completed event contains the final result and metrics.

This makes the actual LLM processing observable from the frontend.

## Backend

The backend is implemented using FastAPI.

Endpoints:

```text
GET  /health
POST /summarize/stream
```

The streaming endpoint uses Server-Sent Events.

The backend is responsible for exposing the Python pipeline to the frontend without moving the actual summarization logic into the UI layer.

## Frontend

The frontend is implemented using Next.js.

The interface is intentionally minimal and engineering-focused rather than resembling a generic AI chatbot.

It displays:

* YouTube URL input
* Pipeline execution stages
* Streaming progress
* Final summary
* Transcript token count
* Number of chunks
* Map calls
* Reduce input tokens
* Processing latency
* Evaluation information

The visual direction uses a restrained black-and-white interface inspired by modern developer tooling.

The goal is for the interface to communicate:

```text
MAP-REDUCE
EVALUATION
TOKEN METRICS
LATENCY
```

rather than simply:

```text
Paste URL → AI Summary
```

The frontend production build has been verified with:

```bash
npm run lint
npm run build
```

## Project Structure

```text
YT_transcript_eval/
│
├── api/
│   └── main.py
│
├── evaluation/
│   ├── dataset.csv
│   ├── generated_results.csv
│   ├── judge_results.csv
│   ├── judge.py
│   ├── run_evaluation.py
│   ├── run_judge.py
│   ├── analyze_results.py
│   └── transcripts/
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   └── components/
│   └── package.json
│
├── chunker.py
├── fetcher.py
├── gemini_client.py
├── ollama_client.py
├── pipeline.py
├── reducer.py
├── tokenizer.py
│
├── test_fetcher.py
├── test_map.py
├── test_ollama.py
├── test_pipeline.py
├── test_reduce.py
├── test_reducer.py
├── test_tokenizer.py
├── test_transcript.py
│
├── DECISIONS.md
├── README.md
├── requirements.txt
└── .gitignore
```

## Local Setup

### Requirements

The current development environment uses:

```text
Python 3.11
Node.js
npm
Ollama
Qwen3 4B
```

Create and activate the Python environment:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Install and run Ollama separately, then make sure the model exists:

```powershell
ollama pull qwen3:4b
```

The project also uses environment variables where required.

Create a `.env` file for any configured external API credentials.

Do not commit `.env`.

### Run the backend

From the repository root:

```powershell
uvicorn api.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### Run the frontend

The frontend has its own Node.js project.

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

## Running the Pipeline

The core Python pipeline can be executed through the project's test/manual execution scripts.

The main orchestration function is:

```python
run_pipeline(url)
```

The streaming equivalent is:

```python
run_pipeline_stream(url)
```

A typical request through the backend is:

```text
POST /summarize/stream
```

with:

```json
{
  "url": "https://www.youtube.com/watch?v=X4Qm9cGRub0"
}
```

## Testing

The project contains tests and manual verification scripts covering the major components:

* Transcript URL parsing
* Transcript retrieval
* Transcript normalization
* Token counting
* Chunking
* Ollama inference
* Map processing
* Reduce processing
* End-to-end pipeline execution
* Evaluation and judge behavior

One limitation is important to state explicitly:

Some files named as tests are currently script-style verification programs rather than conventional pytest test suites. Some also perform real LLM/API calls.

Therefore, the repository should not be interpreted as having comprehensive automated unit-test coverage.

This was identified during development and documented as an engineering limitation rather than hidden.

## Known Limitations

### Local inference

The current summarization model runs through Ollama locally.

This makes the project straightforward to reproduce on a development machine with sufficient hardware, but it also means the backend cannot simply be deployed to a generic cloud server and continue using the developer's local Ollama instance.

A future production deployment would require either:

* hosted inference
* a server running Ollama and the model
* another inference architecture

Public deployment is intentionally outside the current scope.

### Evaluation dataset size

The current benchmark contains four videos.

This is sufficient to demonstrate the evaluation methodology, but it is not large enough to make broad claims about model quality.

The benchmark should therefore be interpreted as an engineering evaluation harness rather than a statistically representative benchmark.

### ASR quality

Automatic transcripts can contain:

* missing punctuation
* recognition errors
* ambiguous phrases
* language-specific artifacts

The summarizer cannot always distinguish a genuine source statement from a transcript recognition error.

### Map context loss

Each Map call sees only its own chunk.

This makes the system scalable and parallelizable, but can lose information that depends on context spanning multiple chunks, such as:

* references to earlier ideas
* arguments resolved later
* long-running narratives
* concepts introduced in one chunk and explained in another

### LLM variability

Even with constrained prompts and structured output, LLM-generated summaries can still vary in quality.

The evaluation layer exists partly to make these weaknesses measurable.

## Engineering Decisions

Important implementation decisions and failed approaches are documented separately in:

```text
DECISIONS.md
```

That document records the reasoning behind decisions such as:

* transcript retrieval behavior
* transcript normalization
* token-based chunking
* Map-Reduce architecture
* local Qwen3 inference
* structured reducer output
* output validation
* LLM/API failures
* testing limitations
* deployment constraints

The goal is to document not only what was built, but why it was built that way.

## What This Project Demonstrates

This project intentionally goes beyond calling an LLM API.

It demonstrates:

```text
Data ingestion
      ↓
Data normalization
      ↓
Token accounting
      ↓
Chunking strategy
      ↓
LLM inference
      ↓
Map-Reduce orchestration
      ↓
Structured output validation
      ↓
Streaming execution
      ↓
Latency/token metrics
      ↓
Evaluation harness
      ↓
LLM-as-a-Judge
      ↓
Backend API
      ↓
Frontend observability
```

The main engineering question is not:

> "Can an LLM summarize a YouTube video?"

It is:

> "How do you build, observe, and evaluate a reliable LLM processing pipeline around long-form unstructured input?"

That distinction is the main purpose of the project.
