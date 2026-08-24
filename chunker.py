import re

from tokenizer import count_tokens, ENCODING


MAX_CHUNK_TOKENS = 1000
DEFAULT_OVERLAP_TOKENS = 100


def split_into_units(text: str) -> list[str]:
    """Split text into sentence-like units while preserving punctuation."""
    units = re.split(r"(?<=[.!?।])\s+", text)

    return [unit.strip() for unit in units if unit.strip()]


def split_by_tokens(text: str, max_tokens: int) -> list[str]:
    """Hard-split text into pieces that fit within the token budget."""
    tokens = ENCODING.encode(text)

    return [
        ENCODING.decode(tokens[i:i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]


def get_overlap_text(text: str, overlap_tokens: int) -> str:
    """Return the last overlap_tokens from a text."""
    tokens = ENCODING.encode(text)

    if overlap_tokens <= 0:
        return ""

    return ENCODING.decode(tokens[-overlap_tokens:])


def chunk_text(
    text: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[dict]:

    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative.")

    if overlap_tokens >= max_tokens:
        raise ValueError(
            "overlap_tokens must be smaller than max_tokens."
        )

    units = split_into_units(text)
    chunks = []
    current_units = []

    for unit in units:
        candidate_text = " ".join(current_units + [unit])

        if count_tokens(candidate_text) <= max_tokens:
            current_units.append(unit)
            continue

        if current_units:
            chunk_text_value = " ".join(current_units)

            chunks.append(
                {
                    "text": chunk_text_value,
                    "token_count": count_tokens(chunk_text_value),
                }
            )

            overlap_text = get_overlap_text(
                chunk_text_value,
                overlap_tokens,
            )

            current_units = [overlap_text, unit] if overlap_text else [unit]

        else:
            hard_chunks = split_by_tokens(unit, max_tokens)

            for hard_chunk in hard_chunks:
                chunks.append(
                    {
                        "text": hard_chunk,
                        "token_count": count_tokens(hard_chunk),
                    }
                )

            overlap_text = get_overlap_text(
                hard_chunks[-1],
                overlap_tokens,
            )

            current_units = [overlap_text] if overlap_text else []

    if current_units:
        chunk_text_value = " ".join(current_units)

        if count_tokens(chunk_text_value) <= max_tokens:
            chunks.append(
                {
                    "text": chunk_text_value,
                    "token_count": count_tokens(chunk_text_value),
                }
            )

    return chunks


def print_chunk_summary(chunks: list[dict], snippet_length: int = 80) -> None:
    """Print chunk number, token count, and text snippets."""
    for index, chunk in enumerate(chunks, start=1):
        text = chunk["text"]

        first_snippet = text[:snippet_length]
        last_snippet = text[-snippet_length:]

        print(f"Chunk {index}")
        print(f"Tokens: {chunk['token_count']}")
        print(f"Start: {first_snippet}")
        print(f"End:   {last_snippet}")
        print()