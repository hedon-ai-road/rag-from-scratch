# 前端项目功能详情

## 1. Load File

![image-20250405193253345](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405193253345.png)

1. 支持选择 PDF 图片（暂且先支持这个，后续再支持不同的文件格式）
2. 支持选择各种 PDF 文件加载工具，比如 python 里面有 PyMuPDF、PyPDF、Unstructured，你可以选择 Rust 现有的 crate 来替代。
3. 点击「Load File」后会对 File 进行加载，加载后的文件名以 {origin*name}*{timestamp}.json 格式存储
4. 支持 Document PreView 和 Document Manager
   1. Document Preview 支持看 Document Content
   2. Document Manager 支持 List、View、Delete Document

## 2. Chunk File

![image-20250405193737766](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405193737766.png)

可支持选择上一步 Load File 中已加载的文件，进行 Chunk，支持以下 Chunk Method 方式：

1. By Pages
2. By Sentences
3. Fixed Size
4. By Paragraphs

支持 Chunks Preview 和 Chunks Management

## 3. Embedding File

![image-20250405193958540](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405193958540.png)

支持选择已 Chunks 的文档，选择不同的 Embedding Provider 和对应的不同的 Model 进行 Generate Embeddings，同样支持 Embedding Preview 和 Embedding Management。

## 4. Indexing with Vector DB

![image-20250405194105973](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405194105973.png)

1. 支持选择 Embedding File
2. 支持选择 Vector DB
3. 支持选择 Index Mode
   1. FLAT
   2. IVF_FLAT
   3. IVF_SQ8
   4. HNSW
4. 支持选择 Collection

点击 Display Collection 进行 indexing，或 Delete Collection，右边显示 indexing results

## 5. Similarity Search

![image-20250405194231593](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405194231593.png)

1. 支持输入 question
2. 支持选择不同的 vector db 及其拥有的 collection
3. 支持配置 Top K Results、Similarity Threshold、Minimum Word Count、Save Search Result
4. 点击 Search 进行搜索，右边显示 search results

## 6. Generation

![image-20250405194421514](https://hedonspace.oss-cn-beijing.aliyuncs.com/img/image-20250405194421514.png)

1. 支持选择上一步保存的 Search Results File，右边显示 Search Context
2. 支持输入 Question
3. 支持选择不同的 LLM Generation provider（huggingface，ollma，openai，deepseek）及其对应的模型（ollama3.2，chatgpt4o，deepseek-chat）
4. 点击 Generate 进行生成
