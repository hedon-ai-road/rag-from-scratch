from langchain_community.document_loaders import PyPDFLoader


def load(path):
    loader = PyPDFLoader(file_path=path)
    docs = loader.load()
    return docs


def main():
    docs = load("./fixtures/黑悟空/黑神话悟空.pdf")
    for doc in docs:
        print(doc.page_content)


if __name__ == "__main__":
    main()
