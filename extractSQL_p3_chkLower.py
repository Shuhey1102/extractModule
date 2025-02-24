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

def check_lowercase_in_sql(xml_string):
    # コメントを除去
    xml_string = re.sub(r'<!--.*?-->', '', xml_string, flags=re.DOTALL)
    # エスケープされたタグを通常のタグに変換
    xml_string = xml_string.replace('&lt;', '<').replace('&gt;', '>').replace('count(*)', 'COUNT(*)').replace('inner join', 'INNER JOIN')
    xml_string = xml_string.replace('left join', 'LEFT JOIN').replace('trim(', 'TRIM(').replace(' as ', ' AS ').replace("'yyyymm'","'YYYYMM'")
    xml_string = xml_string.replace(" and "," AND ").replace(" or "," OR ").replace(" where "," WHERE ")

    # パターン1: <property name="...sql..."> (大文字・小文字区別なし)
    property_pattern = re.compile(r'(?i)<property name="[^"]*sql[^"]*">\s*"(.*?)"', re.DOTALL)
    # パターン2: <initMethod ...> の中の <arg>タグの中身
    initmethod_pattern = re.compile(r'<initMethod[^>]*>\s*<arg>\s*"(.*?)"', re.DOTALL)

    targetsWord = ""

    # 対象SQLを抽出
    sql_statements = []
    sql_statements += property_pattern.findall(xml_string)
    sql_statements += initmethod_pattern.findall(xml_string)

    # 小文字を含むか判定
    for sql in sql_statements:
        if re.search(r'[a-z]', sql):
            targetsWord += sql + " "

    return targetsWord

def search_files_in_directory(root_dir, pattern):
    # 正規表現パターンをコンパイル
    regex = re.compile(pattern, re.DOTALL)

    
    fromRegex = re.compile(r"", re.DOTALL)

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
                # matches = regex.findall(file_content.replace("\n",""))

                # 一致があれば結果に追加
                for match in matches:
                    sql = match[2]
                    sqlNGString = check_lowercase_in_sql(sql)
                    if sqlNGString != "":
                        results.append([filename, dirpath, match[0],match[2],sqlNGString])

            except Exception as e:
                print(f"エラー: {file_path} を読み込む際に問題が発生しました: {e}")
    
    return results

def write_to_csv(results, output_file):
    # 結果をCSVファイルに書き出し
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ファイル名', '親ディレクトリのパス', 'NAME','SQL','NG'])  # ヘッダー
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
