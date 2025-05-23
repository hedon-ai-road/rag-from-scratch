from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import Language
from typing import List


class RecursiveCharacterCodeSplitter:
    """Recursive character code splitter."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 20):
        self.splitter = RecursiveCharacterTextSplitter.from_language(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            language=Language.PYTHON,
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
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        language=Language.PYTHON,
    )
    chunks = text_splitter.split_documents(docs)
    return chunks


def main():
    # at root directory:
    #   uv run -m chunking.character_text_splitter
    from file_loader import txt_langchain_textloader as TxtLoader

    docs = TxtLoader.load("./chunking/recursive_character_text_splitter.py")

    print("")
    print("")
    chunks = chunk(docs=docs, chunk_size=400, chunk_overlap=50)
    print("Chunks:")
    for (index, c) in enumerate(chunks):
        print(f"===== {index} chunk =====")
        print(c)
        print()
    return


if __name__ == "__main__":
    main()
