from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter as LangChainRecursiveCharacterTextSplitter,
)
from typing import List


class RecursiveCharacterTextSplitter:
    """Recursive character text splitter."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 20):
        separators = ["\n\n", "."]
        self.splitter = LangChainRecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        return self.splitter.split_documents(documents)


def chunk(docs: list[Document], chunk_size=500, chunk_overlap=20):
    """
    chunk_overlap is the overlap between chunks.
    chunk_size is only for prefer, not the exact size of the chunk.
    maybe you would see:
        Created a chunk of size 87, which is longer than the specified 50
    """
    separators = ["\n\n", "."]
    text_splitter = LangChainRecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    chunks = text_splitter.split_documents(docs)
    return chunks


def main():
    # at root directory:
    #   uv run -m chunking.character_text_splitter
    from file_loader import txt_langchain_textloader as TxtLoader

    docs = TxtLoader.load("./fixtures/黑悟空/黑悟空版本介绍.md")

    print("")
    print("")
    chunks = chunk(docs=docs, chunk_size=40, chunk_overlap=10)
    print("Chunks:")
    for (index, c) in enumerate(chunks):
        print(f"===== {index} chunk =====")
        print(c)
        print()
    return


if __name__ == "__main__":
    main()
