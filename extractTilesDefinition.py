import xml.etree.ElementTree as ET
import csv
import datetime
import os
import re


#current datetime
dt_now = datetime.datetime.now()
crrDir = os.path.dirname(__file__)


def main():

    file_path = input("filePath : ")
    # ファイルを開いて内容を読み込む
    with open(file_path, 'r', encoding='UTF-8') as file:
        file_content = file.read()

    # XML解析
    root = ET.fromstring(file_content)

    # 出力データのリスト
    rows = []

    # XMLデータをパース
    for definition in root.findall("definition"):
        name = definition.attrib.get("name", "")
        layout = definition.attrib.get("extends", "")
        jsp_path = definition.attrib.get("path", "")

        # put タグを解析
        for put in definition.findall("put"):
            part_name = put.attrib.get("name", "")
            value = put.attrib.get("value", "")
            rows.append([name, part_name, value, layout])

        # pathがある場合、partsが空の行を追加
        if jsp_path:
            rows.append([name, "", jsp_path, layout])

    # CSVファイルに書き込み
    with open(crrDir + "\\" +"tiles_definitions_2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー行
        writer.writerow(["name", "parts", "jspPath", "Layout"])
        # データ行
        writer.writerows(rows)

    print("tiles_definitions.csv ファイルが作成されました。")

if __name__ == "__main__":
    main()
