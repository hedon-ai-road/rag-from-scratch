from llama_index.core import SimpleDirectoryReader


def load(dir):
    dir_reader = SimpleDirectoryReader(dir)
    documents = dir_reader.load_data()
    print(f"the count of documents: {len(documents)}")
    print(documents)


def main():
    load("./fixtures/黑悟空")


if __name__ == "__main__":
    main()
