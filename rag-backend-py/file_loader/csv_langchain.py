from langchain_community.document_loaders import CSVLoader


def load(path):
    loader = CSVLoader(
        file_path=path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": ["种类", "名称", "描述"],
        },
    )
    docs = loader.load()
    return docs


def main():
    docs = load("./fixtures/黑悟空/黑神话悟空.csv")
    print(docs)


if __name__ == "__main__":
    main()
