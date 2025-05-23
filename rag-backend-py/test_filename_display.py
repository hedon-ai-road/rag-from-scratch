import asyncio
from database.service import DatabaseService
from file_loader.service import FileLoaderService


async def test_filename_display():
    service = FileLoaderService()
    db_service = DatabaseService()

    print("Testing filename display logic...")

    # 检查现有文件的显示名称
    files, total = await service.get_all_files(1, 10)
    print(f"Found {total} files:")

    for file in files:
        print(f"  File ID: {file.file_id}")
        print(f"  Display Name: {file.file_name}")
        print(f"  Loading Method: {file.loadingMethod}")

        # 检查第一个文档的metadata
        docs = db_service.get_documents(file.file_id)
        if docs:
            first_doc = docs[0]
            print(
                f'  First doc metadata keys: {list(first_doc.doc_metadata.keys()) if first_doc.doc_metadata else "None"}'
            )
            if first_doc.doc_metadata and "original_filename" in first_doc.doc_metadata:
                print(
                    f'  Original filename in metadata: {first_doc.doc_metadata["original_filename"]}'
                )
            else:
                print(f"  No original_filename in metadata")
        print()


if __name__ == "__main__":
    asyncio.run(test_filename_display())
