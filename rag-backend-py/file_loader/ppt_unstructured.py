from unstructured.partition.ppt import partition_ppt
from langchain_core.documents import Document


def load(ppt_path):
    ppt_elements = partition_ppt(filename=ppt_path)
    print("the content of ppt:")
    for element in ppt_elements:
        print(element.text)

    docs = [
        Document(page_content=element.text, metadata={"source": ppt_path})
        for element in ppt_elements
        if element.text and element.text.strip()
    ]
    return docs


def main():
    docs = load("./fixtures/黑悟空/黑神话悟空.pptx")
    print(docs)


if __name__ == "__main__":
    main()
