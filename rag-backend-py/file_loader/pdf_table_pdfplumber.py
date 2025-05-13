import pdfplumber


def load(path):
    # https://github.com/jsvine/pdfplumber?tab=readme-ov-file#extracting-tables
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            print(page.extract_tables(table_settings={}))


def main():
    load("./fixtures/复杂PDF/billionaires_page-1-5.pdf")


if __name__ == "__main__":
    main()
