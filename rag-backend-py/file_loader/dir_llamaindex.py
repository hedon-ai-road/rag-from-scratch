from llama_index.core import SimpleDirectoryReader


def load(dir):
    dir_reader = SimpleDirectoryReader(dir)
    documents = dir_reader.load_data()
    return documents


def main():
    documents = load("./fixtures/黑悟空")
    print(f"the count of documents: {len(documents)}")
    print(documents)


if __name__ == "__main__":
    main()
