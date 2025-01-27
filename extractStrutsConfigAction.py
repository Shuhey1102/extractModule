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

    # <action-mappings> を探す
    action_mappings = root.find("action-mappings")
    if action_mappings is None:
        print("Error: <action-mappings> タグが見つかりません。")
        exit()

    # 出力データのリスト
    rows = []

    # XMLデータをパース
    for action in action_mappings.findall("action"):
        path = action.attrib.get("path", "")
        action_type = action.attrib.get("type", "")
        
        # <forward> タグを処理
        forwards = action.findall("forward")
        if forwards:
            for forward in forwards:
                fwd_name = forward.attrib.get("name", "")
                fwd_path = forward.attrib.get("path", "")
                rows.append([path, fwd_name, fwd_path, action_type])
        else:
            # forward がない場合
            rows.append([path, "", "", action_type])

    # CSVファイルに書き込み
    with open("action_mappings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー行
        writer.writerow(["path", "fwd_Name", "fwd_Path", "Action"])
        # データ行
        writer.writerows(rows)

    print("action_mappings.csv ファイルが作成されました。")

if __name__ == "__main__":
    main()
