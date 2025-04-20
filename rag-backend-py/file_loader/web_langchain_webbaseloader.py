from langchain_community.document_loaders import WebBaseLoader


def load(page_url):
    loader = WebBaseLoader(web_path=page_url)
    docs = loader.load()
    return docs


def main():
    docs = load("https://hedon.top/2025/04/13/ai-rag-tech-overview/")
    assert len(docs) == 1
    doc = docs[0]
    print(f"{doc.metadata}\n")
    print(doc.page_content.strip())


if __name__ == "__main__":
    main()
