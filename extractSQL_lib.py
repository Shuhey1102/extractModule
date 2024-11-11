import datetime
import os
import re


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
    regex = re.compile(pattern)
    
    # 結果を格納するリスト
    results = []

    # 指定したディレクトリ内の全てのファイルとフォルダを走査
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            try:
                # ファイルを開いて内容を読み込む
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()

                # ファイルの中身が正規表現に一致する場合
                matches = regex.findall(file_content)

                # 一致があれば結果に追加
                for match in matches:
                    name_values = re.findall(r'name="([^"]+)"', match)                    
                    results.append(name_values[0])

            except Exception as e:
                print(f"エラー: {file_path} を読み込む際に問題が発生しました: {e}")
    
    return results


def runExtractSQL(_filepath,_pattern):
    # 対象のフォルダパスと正規表現パターンを指定
    #root_dir = input("検索対象のフォルダのパスを入力してください: ")
    #pattern = input("検索する正規表現を入力してください: ")
    
    root_dir = _filepath
    pattern = _pattern
    #output_file = f"{crrDir}\\output\\extractSQL_{getTimeString()}.csv"

    # ファイルを検索して結果を取得
    return search_files_in_directory(root_dir, pattern)