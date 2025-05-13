import camelot


def load(path):
    # https://camelot-py.readthedocs.io/en/master/user/quickstart.html#
    tables = camelot.read_pdf(path)
    print(tables)


def main():
    load("./fixtures/复杂PDF/billionaires_page-1-5.pdf")


if __name__ == "__main__":
    main()
