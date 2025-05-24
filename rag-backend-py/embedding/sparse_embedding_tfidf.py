from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "The quick brown fox jumps over the lazy dog.",  # 句子 A
    "A fast brown fox leaps above a sleepy dog.",  # 句子 B
]
queries = [
    ["The quick brown fox jumps over the lazy dog."],
    ["The quick brown fox jumps over the lazy."],
    ["The quick brown fox jumps over."],
    ["A fast brown fox leaps above a sleepy dog."],
    ["dog"],
    ["Dog"],
]

# TF-IDF（Term Frequency – Inverse Document Frequency，词频-逆文档频率）
# 一种经典的加权方案，用来衡量 词语 t 对 文档 d 在 语料库 D 中的重要程度。
# 词在本篇文档里出现得越多，就越重要	TF(t,d) = 出现次数 或 频率变体	捕捉“局部重要性”
# 词在整个语料里出现得越少，就越能区分文档	IDF(t,D) = log ((N + 1)/(df(t)+1))

# 一句话：一个词语，在全篇中出现得越少，但是在局部出现得越多，那它对局部的重要性就越高。
tfidf = TfidfVectorizer()
doc_mat = tfidf.fit_transform(docs)
query_vecs = [tfidf.transform(query) for query in queries]

scores = [cosine_similarity(query_vec, doc_mat) for query_vec in query_vecs]
print(f"sparse vector dim: {doc_mat.shape[1]}")

for score in scores:
    print(f"similarity: {score.ravel()}")
