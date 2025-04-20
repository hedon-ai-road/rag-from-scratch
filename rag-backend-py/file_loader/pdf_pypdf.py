import logging
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger("rag-backend.file_loader.pdf_pypdf")


def load(path):
    """
    Load a PDF file using PyPDFLoader

    Args:
        path: Path to the PDF file

    Returns:
        List of document objects with page content and metadata
    """
    try:
        logger.info(f"Loading PDF from {path} with PyPDFLoader")
        loader = PyPDFLoader(file_path=path)
        docs = loader.load()

        if not docs:
            logger.warning(f"PyPDFLoader returned no documents for {path}")
            return []

        logger.info(f"PyPDFLoader successfully loaded {len(docs)} pages from {path}")

        # Debug the first document
        if docs and len(docs) > 0:
            logger.info(f"First page content sample: {docs[0].page_content[:100]}...")
            logger.info(f"First page metadata: {docs[0].metadata}")

        return docs
    except Exception as e:
        logger.error(f"Error loading PDF with PyPDFLoader: {str(e)}", exc_info=True)
        return []


def main():
    docs = load("./fixtures/黑悟空/黑神话悟空.pdf")
    print(f"Loaded {len(docs)} documents")
    for i, doc in enumerate(docs):
        print(f"Document {i+1} - Page: {doc.metadata.get('page', 'unknown')}")
        print(f"Content sample: {doc.page_content[:100]}...")
        print("-" * 50)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
