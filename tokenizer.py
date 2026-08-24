import tiktoken

ENCODING = tiktoken.get_encoding("o200k_base")

def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))