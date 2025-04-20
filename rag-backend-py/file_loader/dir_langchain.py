from langchain_community.document_loaders import DirectoryLoader


def load(dir):
    loader = DirectoryLoader(dir)
    docs = loader.load()
    return docs


def main():
    docs = load("./fixtures/黑悟空")
    print(f"the count of documents: {len(docs)}")
    print(docs)


if __name__ == __name__:
    main()
