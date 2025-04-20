from langchain_unstructured import UnstructuredLoader


def load(path):
    loader = UnstructuredLoader(
        file_path=path, strategy="hi_res", partition_via_api=False, coordiantes=True
    )
    docs = []
    for doc in loader.lazy_load():
        docs.append(doc)

    return docs


def main():
    docs = load("./fixtures/黑悟空/黑神话悟空.pdf")
    print(docs)


if __name__ == "__main__":
    main()
