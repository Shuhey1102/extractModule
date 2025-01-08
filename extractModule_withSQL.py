import os
import csv
from concurrent.futures import ProcessPoolExecutor
import extractSQL_lib
import datetime
import re
import concurrent

#current datetime
dt_now = datetime.datetime.now()

crrDir = os.path.dirname(__file__)

def getTimeString():
    """get Month
    Args:
    """        
    return dt_now.strftime('%Y%m%d%H%M%S')

outputFilename = f"output_sql_{getTimeString()}.csv"

def search_files_for_keywords_in_folder(folder_path, keywords):
    # 結果を格納するリスト
    results = []

    daoFunction = ["setDiconDir","pagerSelectSQL","selectSQL","updateSQL","selectOrderSQL","selectSQLReplace","replaceSqlKpiTableId","getDiconPath","removeBlankRow","setLocator"]
 
    # 正規表現の作成
    dao_pattern = "|".join(re.escape(func) for func in daoFunction)
    sql_pattern = "|".join(re.escape(sql[3]) for sql in keywords)
    regex_pattern = rf"({dao_pattern})\(\"({sql_pattern})\".*?\);"

    # フォルダ内の全てのファイルを走査
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            try:
                # ファイルを行ごとに読み込む             
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line_number, line in enumerate(file, start=1):  # 行番号をカウント

                        # ファイルの中身に対してキーワードを検索
                        # for keyword in keywords:
                        #     if keyword in line:
                        #         # 一致した場合、結果に追加
                        #         results.append([filename, dirpath, keyword, line.strip(), line_number])

                        for match in re.finditer(regex_pattern, line.strip()):                            
                            
                            sqlStatement = [item[4] for item in keywords if item[3] == match.group(2)][0]

                            # 一致した場合、結果に追加
                            results.append([filename, dirpath, match.group(2), line.strip(),match.group(2), line_number,sqlStatement])

            except Exception as e:
                print(f"エラー: {file_path} を読み込む際に問題が発生しました: {e}")

    return results

def write_results_to_csv(results, output_dir,cnt):
    # 結果をCSVファイルに書き出し
    #os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, outputFilename)
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if int(cnt) == 0 :
            writer.writerow(['fileName', 'ParentPath', 'targetWord','line','funcition','colNum','SQL']) 
        writer.writerows(results)

def process_folder(dirname ,folder_path, keywords):
    # フォルダ内のファイルを検索して結果を取得
    return search_files_for_keywords_in_folder(folder_path, keywords)

def main():
    # 検索対象のフォルダパスを指定
    sql_dir = input("SQLの抽出フォルダ: ")

    # キーワードリストを直接指定
    keywords = extractSQL_lib.runExtractSQL(sql_dir,r"<component name=\"(.*?)\"(.*?)>(.*?)</component>")

    # while(True):
    #     isEnd = input("他に追加すべき検索キーワードがありますか？(y:n): ")
    #     if isEnd == "n":
    #         break        
    #     key = input("検索キーワード: ")
    #     if(str.strip(key) != ""):
    #         keywords.append(key)
    #         print(f"{key}を追加しました")

    root_dir = input("検索対象のフォルダ: ")

    # サブフォルダごとに並行で検索処理を実行
    with ProcessPoolExecutor() as executor:
        futures = []
        # フォルダごとに検索処理を並行で実行
        for entry in os.scandir(root_dir):
            if entry.is_dir(): 
                folder_path = entry.path
                futures.append(executor.submit(process_folder, entry.name ,folder_path, keywords))                               

    
    cnt = 0
    for future in concurrent.futures.as_completed(futures):
        try:
            results = future.result()

            # 結果をフォルダごとのoutput.csvに書き出し
            if results:
                #output_dir = os.path.join(folder_path, 'output')
                output_dir = f"{crrDir}\\output\\"
                write_results_to_csv(results,output_dir,cnt)
                cnt+=1            

        except Exception as e:
            print(f"Error processing folder: {e}")
            SystemExit(1)

    print("すべての検索結果がフォルダごとにoutput.csvに保存されました")
    return outputFilename

if __name__ == '__main__':
    main()