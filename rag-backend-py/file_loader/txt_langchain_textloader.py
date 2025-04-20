from langchain_community.document_loaders import TextLoader


def load(file):
    loader = TextLoader(file)
    documents = loader.load()
    return documents


def main():
    docs = load("./fixtures/黑悟空/黑悟空设定.txt")
    print(docs)


if __name__ == "__main__":
    main()
