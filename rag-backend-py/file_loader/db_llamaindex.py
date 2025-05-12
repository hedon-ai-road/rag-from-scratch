from llama_index.readers.database import DatabaseReader


def main():
    reader = DatabaseReader(uri="mysql://root@localhost:3306/goapm")
    query = "select * from `t_user`"
    documents = reader.load_data(query=query)
    print(documents)
    return


if __name__ == "__main__":
    main()
