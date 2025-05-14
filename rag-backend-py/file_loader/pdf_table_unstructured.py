from unstructured.partition.pdf import partition_pdf


def load(path):
    # https://docs.unstructured.io/examplecode/codesamples/apioss/table-extraction-from-pdf
    elements = partition_pdf(
        filename=path,
        skip_infer_table_types=False,
        strategy="hi_res",
    )

    tables = [el for el in elements if el.category == "Table"]
    return tables


def main():
    tables = load("./fixtures/复杂PDF/billionaires_page-1-5.pdf")
    for table in tables:
        print(
            f"""
            {table.id}: \n
            page_name: {table.metadata.page_name}\n
            page_num: {table.metadata.page_number}\n
            text: {table.text}
            """
        )


if __name__ == "__main__":
    main()
