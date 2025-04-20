from langchain_community.document_loaders import JSONLoader


def main():
    print("The result of json loader:")
    print("1. the info of main character:")
    main_loader = JSONLoader(
        file_path="fixtures/灭神纪/人物角色.json",
        jq_schema='.mainCharacter|"姓名：" + .name  + "，背景：" + .backstory',
        text_content=True,
    )
    main_char = main_loader.load()
    print(main_char)
    print("\n2. the info of support characters:")
    support_loader = JSONLoader(
        file_path="fixtures/灭神纪/人物角色.json",
        jq_schema='.supportCharacters[] | "姓名:" + .name + "，背景:" + .background',
        text_content=True,
    )
    support_chars = support_loader.load()
    print(support_chars)


if __name__ == "__main__":
    main()
