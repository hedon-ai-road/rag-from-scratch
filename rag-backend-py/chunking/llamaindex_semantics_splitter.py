from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from typing import List
from langchain_core.documents import Document as LangChainDocument


class LlamaindexSemanticsSplitter:
    """Semantic splitter using LlamaIndex."""

    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=OpenAIEmbedding(),
        )

    def split_documents(
        self, documents: List[LangChainDocument]
    ) -> List[LangChainDocument]:
        """Split documents into chunks."""
        # Convert LangChain documents to LlamaIndex documents
        llama_docs = []
        for doc in documents:
            llama_doc = Document(
                text=doc.page_content,
                metadata=doc.metadata if hasattr(doc, "metadata") else {},
            )
            llama_docs.append(llama_doc)

        # Split using LlamaIndex
        chunks = self.splitter.get_nodes_from_documents(llama_docs)

        # Convert back to LangChain documents
        result = []
        for chunk in chunks:
            langchain_doc = LangChainDocument(
                page_content=chunk.text, metadata=chunk.metadata or {}
            )
            result.append(langchain_doc)

        return result


def chunk(docs: list[Document]):
    """
    chunk_overlap is the overlap between chunks.
    chunk_size is only for prefer, not the exact size of the chunk.
    maybe you would see:
        Created a chunk of size 87, which is longer than the specified 50
    """
    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=OpenAIEmbedding(),
    )
    chunks = splitter.get_nodes_from_documents(docs)
    return chunks


def main():
    # at root directory:
    #   uv run -m chunking.character_text_splitter
    from file_loader import dir_llamaindex as DirLoader

    docs = DirLoader.load("./fixtures/黑悟空/")

    print("")
    print("")
    chunks = chunk(docs=docs)
    print("Chunks:")
    for (index, c) in enumerate(chunks):
        print(f"===== {index} chunk =====")
        print(c)
        print()
    return


if __name__ == "__main__":
    main()
