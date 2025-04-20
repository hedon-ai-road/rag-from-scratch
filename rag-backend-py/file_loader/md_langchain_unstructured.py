from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document


def load(file):
    loader = UnstructuredMarkdownLoader(file_path=file, mode="elements")
    return loader.load()


def main():
    docs = load("./fixtures/黑悟空/黑悟空版本介绍.md")
    print(docs)


if __name__ == "__main__":
    main()
