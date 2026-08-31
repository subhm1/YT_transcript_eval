# Engineering Decisions

This file records the important decisions, failed approaches, debugging discoveries, and trade-offs I made while building this project.


---

## 1. I started with a simple transcript processing pipeline:

At first, I wanted to keep the project simple and understand every stage myself instead of using a framework like LangChain.

Decided to build the pipeline explicitly:

YouTube URL
→ transcript fetching
→ transcript cleaning
→ token counting
→ chunking
→ map summarization
→ reduce summarization
→ evaluation

The goal was to understand what happens inside a summarization pipeline rather than hiding the important parts behind a framework.

---

## 2. Separated the pipeline into small modules:

Initially considered keeping everything in one script, but that would make it difficult to test and debug individual stages.

So separated the project into modules such as:

- `fetcher.py`
- `tokenizer.py`
- `chunker.py`
- `gemini_client.py`
- `ollama_client.py`
- `reducer.py`
- `pipeline.py`

This made it possible to test individual stages independently and also made failures easier to locate.

---

## 3. I chose explicit map-reduce summarization:

Long transcripts cannot always be sent to an LLM in one call.

Therefore implemented:

1. Split the transcript into chunks.
2. Summarize every chunk independently.
3. Send the chunk summaries to a reducer.
4. Generate the final summary.

The important decision here was to make the map-reduce process explicit instead of relying on an abstraction.

This also gave me useful metrics such as:

- transcript token count
- number of chunks
- number of map calls
- reducer input tokens
- total execution time

---

## 4. Initially used Gemini for map summarization but ;(

Used Gemini for the map stage because I wanted to use a real LLM API for the summarization process.

The implementation worked, but found an imp problem during testing.

While running `test_map.py`, Gemini returned:

`503 UNAVAILABLE`

The error message said that the model was experiencing high demand.

The interesting part was that the failure happened after several successful calls. The pipeline successfully processed the first few chunks and then failed on a later request.This showed me that an external API can fail even when my code is correct.

Therefore I do not consider an API failure to automatically mean that the pipeline implementation is broken.

---

## 5. Moved the reducer to local Ollama:

For the reduce stage, used Ollama locally with:

`qwen3:4b`

The reducer accepts the individual map summaries and asks the local model to produce structured JSON.

The expected structure is:

```json
{
  "bullets": [
    "bullet 1",
    "bullet 2",
    "bullet 3"
  ]
}
```

Also added validation after the model response.

The reducer checks:

- the output is not empty
- the output is valid JSON
- the JSON is an object
- only the `bullets` field exists
- `bullets` is a list
- there are between 3 and 8 bullets

This was deliberate because I did not want to blindly trust an LLM response.

---

## 6. Found that structured output still needs validation

The reducer was instructed to return JSON, and Ollama was also given a JSON schema.

Still added explicit validation in Python.

Bcz I thought the model output is external data from the perspective of my application and it should verify the result before using it.

This made the reducer more deterministic and easier to debug.

---

## 7. Found a formatting problem in the reducer output

During an end-to-end run, the reducer returned bullets that already started with `-`.

The reducer then added another `-` when converting the list into the final string.

This produced output like:

`- - Qualitative research methodology...`

The model itself was technically returning valid JSON, so the problem was in my application-level formatting.

Fixed the reducer so that it strips the bullet formatting before adding the final bullet prefix.

This was a useful reminder that valid model output does not necessarily mean valid application output.

---

## 8. Tested the reducer independently before trusting the whole pipeline:

I created a small manual reducer test using simple summaries such as:

- Python is a programming language used for automation.
- Python has a large ecosystem of libraries.

The reducer returned valid JSON and the Python validation passed.

This gave me a cheap way to test reducer behavior without running the entire YouTube pipeline.

Created `test_reducer_manual.py` for a more realistic manual reducer test using several sections.

---

## 9. Deliberately tested a real YouTube video (Benchmarked)

After the individual stages were working, I tested the complete pipeline using a real YouTube video.

The pipeline successfully performed:

- fetch
- normalize
- chunk
- map
- reduce
- complete

One successful run produced:

- 3816 transcript tokens
- 5 chunks
- 5 map calls
- 740 reducer input tokens
- approximately 62 seconds execution time

This confirmed that the individual components were actually connected into a working end-to-end system.

---

## 10. Testing the video outside the evaluation benchmark :

I tested it with a non-benchmark YouTube video. The pipeline successfully generated a summary and completed normally.

The evaluation panel correctly reported:

`This video is not part of the evaluation benchmark.`

This was kinda CORRECT behavior.

Summarization and evaluation are separate concerns:

- Any supported YouTube video can be summarized.
- Only known benchmark videos should receive benchmark evaluation.

---

## 11. added an evaluation layer instead of pretending every summary has a score

The project is not only a summarizer.

I wanted to evaluate summary quality against reference summaries.

The evaluation system therefore checks whether the current video belongs to the benchmark dataset.

If it does not, the application should not invent an evaluation score.

This is why the frontend can show the generated summary while explicitly saying that the video is not part of the evaluation benchmark.

---

## 12. Initially had an import problem in the evaluation test

When I ran the complete pytest suite, collection failed with:

`ModuleNotFoundError: No module named 'judge'`

The problem came from:

```python
from judge import judge_summary
```

inside `evaluation/test_judge.py`.

Because `judge.py` lives inside the `evaluation` package, the correct import is:

```python
from evaluation.judge import judge_summary
```

I temporarily changed it to test the correct import.

After understanding the issue, I restored the file because I did not want to make an unnecessary repository change without deciding how the evaluation tests should actually be structured.

---

## 13. Found that some of my test files were not actually pytest tests:

When I ran:

```powershell
python -m pytest evaluation/test_judge.py -v
```

pytest reported:

`collected 0 items`

This initially looked like a failure.

After inspecting the file, I realized that `evaluation/test_judge.py` contains executable test code at module level rather than pytest test functions such as:

```python
def test_something():
    ...
```

So pytest was collecting the file but finding no test functions.

The same issue exists in some of the older project test files.

This taught me an important distinction:

A file named `test_*.py` is not automatically a pytest test.

For pytest to collect tests, I need actual pytest-compatible test functions or classes.

---

## 14. Discovered that some old test files execute real API calls during collection

```powershell
python -m pytest test_fetcher.py test_map.py test_ollama.py test_pipeline.py test_reduce.py test_reducer.py test_tokenizer.py test_transcript.py -v
```

The run reached `test_map.py` and started making real Gemini API calls.

Eventually Gemini returned:

`503 UNAVAILABLE`

This took several minutes because the external API call and retry behavior happened during test collection.

The important lesson was that tests should not make expensive external API calls merely by being imported.

I need to distinguish between:

- unit tests
- integration tests
- manual experiments
- external API tests

The current repository still contains some scripts that behave more like manual integration tests than true pytest tests.

---

## 15. I installed pytest into the project environment.

## 16. I verified the frontend independently

The frontend is a Next.js application.

I ran:

```powershell
cd frontend
npm run lint
npm run build
```

Both completed successfully.

The production build reported:

`Compiled successfully`

and successfully generated the `/` route.

This gave me confidence that the frontend was at least syntactically valid, type-safe, lint-clean, and buildable.

---

## 17. I connected the frontend to the actual pipeline

The frontend now exposes the complete pipeline visually.

It shows:

1. Fetch transcript
2. Normalize & clean
3. Count tokens
4. Create chunks
5. Map · summarize chunks
6. Reduce · final summary

It also displays metrics such as:

- tokens
- chunks
- map calls
- reduce tokens
- latency

I wanted the UI to expose what the pipeline is actually doing instead of presenting the system as a black box.

---

## 18. I kept benchmark evaluation separate from normal summarization

A normal user should be able to enter a YouTube URL and receive a summary even when the video is not part of the benchmark dataset.

At the same time, benchmark videos should receive evaluation information.

Therefore I kept these two paths separate:

Normal pipeline:

`YouTube → transcript → summarization → result`

Evaluation:

`benchmark video → generated summary → judge → evaluation result`

This prevents the application from confusing "I generated a summary" with "I measured summary quality."

---

## 19. Pushed the complete pipeline to GitHub

## 20. I decided that production cleanup is separate from making the pipeline work

At this point, the main engineering goal has been achieved:

The system can fetch a transcript, process it, summarize it through map-reduce, reduce the summaries, expose metrics, evaluate benchmark videos, and display the result through a frontend.

I do not want to endlessly modify working code just to make it look cleaner.

---

## 21. I learned that "working" and "production-ready" are different

The pipeline working end-to-end does not automatically make it production-ready.

A production-oriented version should also consider:

- predictable error handling
- external API failures
- invalid YouTube URLs
- missing transcripts
- unavailable transcripts
- LLM failures
- malformed model responses
- evaluation dataset misses
- request validation
- frontend/backend communication failures
- logging
- configuration
- reproducibility
- tests

I therefore consider the current project an end-to-end working system that still has room for engineering hardening.

---

## 22. My main failure modes so far

The most important failures I encountered were:

### Gemini API failure

Gemini returned:

`503 UNAVAILABLE`

This showed that external model providers can fail independently of application correctness.

### Reducer formatting issue

The model returned bullets with `-`, and my application added another `-`.

This produced:

`- - bullet`

I fixed the application-level formatting.

### Evaluation import failure

`from judge import judge_summary`

failed when pytest imported the evaluation test.

The package-aware import was:

`from evaluation.judge import judge_summary`

### Pytest collected zero tests

Some files were named like tests but contained top-level executable code rather than pytest test functions.

### External API during test collection

`test_map.py` performed real Gemini calls during import, which made the test suite slow and vulnerable to API failures.

### Missing pytest

Pytest was initially not installed in the virtual environment.

### Non-benchmark evaluation

A non-benchmark video initially appeared as an evaluation case, but the correct behavior was to show that the video is outside the benchmark rather than generate a fake evaluation score.

---

## 23. Current state

The current project has:

- YouTube transcript fetching
- transcript normalization
- token counting
- explicit chunking
- map summarization
- local Ollama reduce summarization
- structured reducer output
- reducer validation
- streaming pipeline events
- token metrics
- latency metrics
- benchmark dataset
- LLM-based evaluation
- non-benchmark handling
- FastAPI backend
- Next.js frontend
- production frontend build
- GitHub repository with a clean working tree

The core end-to-end pipeline is working.
