import os
import re
import csv
import datetime

#current datetime
dt_now = datetime.datetime.now()

crrDir = os.path.dirname(__file__)

def getTimeString():
    """get Month
    Args:
    """        
    return dt_now.strftime('%Y%m%d%H%M%S')

def search_files_in_directory(root_dir, pattern):
    # 正規表現パターンをコンパイル
    regex = re.compile(pattern, re.DOTALL)
    
    # 結果を格納するリスト
    results = []

    # 指定したディレクトリ内の全てのファイルとフォルダを走査
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            try:
                if file_path.endwith(".sql"):
                    # ファイルを開いて内容を読み込む
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()

                    # # ファイルの中身が正規表現に一致する場合
                    # matches = regex.findall(file_content)
                    # # matches = regex.findall(file_content.replace("\n",""))

                    # # 一致があれば結果に追加
                    # for match in matches:
                    results.append([filename, dirpath, filename,file_content])

            except Exception as e:
                print(f"エラー: {file_path} を読み込む際に問題が発生しました: {e}")
    
    return results

def write_to_csv(results, output_file):
    # 結果をCSVファイルに書き出し
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ファイル名', '親ディレクトリのパス', 'NAME','SQL'])  # ヘッダー
        writer.writerows(results)

def main():
    # 対象のフォルダパスと正規表現パターンを指定
    #root_dir = input("検索対象のフォルダのパスを入力してください: ")
    #pattern = input("検索する正規表現を入力してください: ")
    
    root_dir = input("検索対象のフォルダのパスを入力してください: ")
    pattern = r"<component name=\"(.*?)\"(.*?)>(.*?)</component>"

    output_file = f"{crrDir}\\output\\extractSQL_{getTimeString()}.csv"

    # ファイルを検索して結果を取得
    results = search_files_in_directory(root_dir, pattern)

    # 結果をCSVに書き出す
    write_to_csv(results, output_file)
    print(f"結果が{output_file}に保存されました")

if __name__ == '__main__':
    main()
