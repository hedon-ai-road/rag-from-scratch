from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter


def chunk(docs: list[Document], chunk_size=500, chunk_overlap=20):
    """
    chunk_overlap is the overlap between chunks.
    chunk_size is only for prefer, not the exact size of the chunk.
    maybe you would see:
        Created a chunk of size 87, which is longer than the specified 50
    """
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(docs)
    return chunks


def main():
    # at root directory:
    #   uv run -m chunking.character_text_splitter
    from file_loader import txt_langchain_textloader as TxtLoader

    docs = TxtLoader.load("./fixtures/黑悟空/黑悟空设定.txt")
    print("Documents:")
    for doc in docs:
        print(doc)

    print("")
    print("")
    chunks = chunk(docs=docs, chunk_size=50, chunk_overlap=10)
    print("Chunks:")
    for c in chunks:
        print(c)
    return


if __name__ == "__main__":
    main()
