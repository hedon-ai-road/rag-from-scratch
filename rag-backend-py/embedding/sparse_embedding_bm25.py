import math
import re
from collections import Counter
import pandas as pd

docs = [
    "The quick brown fox jumps over the lazy dog.",
    "A fast brown fox leaps above a sleepy dog.",
]
query = "The quick brown fox jumps over the lazy dog."


# 1. tokenize docs and query
def tokenize(text: str):
    return [w.lower() for w in re.findall(r"\b\w+\b", text)]


doc_tokens = [tokenize(d) for d in docs]
query_tokens = tokenize(query)

# 2. Pre-compute document frequencies (df) & constants
N = len(docs)
df_counter = Counter()
for tokens in doc_tokens:
    df_counter.update(set(tokens))

# BM25 hyper-parameters(Okapi defaults)
k1 = 1.2
b = 0.75
avgdl = sum(len(t) for t in doc_tokens) / N


def idf(term: str) -> float:
    return math.log((N - df_counter[term] + 0.5) / (df_counter[term] + 0.5) + 1)


# 3. BM25 scoring function
def bm25_score(token_docs):
    score = 0.0
    dl = len(token_docs)
    tf_counts = Counter(token_docs)
    for term in query_tokens:
        if term not in tf_counts:
            continue
        tf = tf_counts[term]
        term_idf = idf(term)
        denom = tf + k1 * (1 - b + b * dl / avgdl)
        score += term_idf * (tf * (k1 + 1) / denom)
    return score


scores = [bm25_score(toks) for toks in doc_tokens]

# ----------------------------
# 4. Present results
results_df = (
    pd.DataFrame({"doc_id": [0, 1], "document": docs, "bm25_score": scores})
    .sort_values("bm25_score", ascending=False)
    .reset_index(drop=True)
)

print(results_df)
