from langchain_community.document_loaders import UnstructuredImageLoader


def load(img_path):
    loader = UnstructuredImageLoader(file_path=img_path)
    return loader.load()


def main():
    docs = load("./fixtures/黑悟空/黑悟空英文.jpg")
    print(docs)


if __name__ == "__main__":
    main()
