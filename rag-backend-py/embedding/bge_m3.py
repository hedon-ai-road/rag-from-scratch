from FlagEmbedding import BGEM3FlagModel, FlagReranker

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

# 使用方法一： 生成稠密向量 / 稀疏权重 / ColBERT 片段
# 稠密向量：用于整体语义
# 稀疏权重：精准搜索
# 多向量 ColBERT：细粒度匹配
sentence_1 = ["什么是 BGE-M3？"]
sentence_2 = ["BGE-M3 是一款多功能多语种向量模型。"]

output_1 = model.encode(
    sentence_1, return_dense=True, return_sparse=True, return_colbert_vecs=True
)
output_2 = model.encode(
    sentence_2, return_dense=True, return_sparse=True, return_colbert_vecs=True
)
lexical_score = model.compute_lexical_matching_score(
    output_1["lexical_weights"][0], output_2["lexical_weights"][0]
)
semantic_similarity = output_1["dense_vecs"] @ output_2["dense_vecs"].T
colbert_score = model.colbert_score(
    output_1["colbert_vecs"][0], output_2["colbert_vecs"][0]
)
print(
    float(semantic_similarity[0][0]) * 0.4
    + float(lexical_score) * 0.2
    + float(colbert_score) * 0.4
)


# 使用方法二： 直接获得三路相关度并做加权融合
pairs = [("什么是 BGE-M3？", "BGE-M3 是一款多功能多语种向量模型。")]  # query, doc
scores = model.compute_score(pairs, weights_for_different_modes=[0.4, 0.2, 0.4])
print(scores["colbert+sparse+dense"][0])  # 加权总分
