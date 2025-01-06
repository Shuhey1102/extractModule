import os
import csv
from concurrent.futures import ProcessPoolExecutor
import extractSQL_lib
import datetime
import concurrent

OKExtention = (
    ".sql",
    ".dicon",
    ".java",
    ".xml",
    ".db",
    "jav",
    "json"
)


#current datetime
dt_now = datetime.datetime.now()
crrDir = os.path.dirname(__file__)

def getTimeString():
    """get Month
    Args:
    """        
    return dt_now.strftime('%Y%m%d%H%M%S')

outputFilename = f"output_2_{getTimeString()}.csv"

def search_files_for_keywords_in_folder(folder_path,file_name, keywords):
    # 結果を格納するリスト
    results = []

    file_path = os.path.join(folder_path, file_name)
    try:
        if file_path.endswith(OKExtention):
            
            # ファイルを行ごとに読み込む             
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_number, line in enumerate(file, start=1):  # 行番号をカウント
                    # ファイルの中身に対してキーワードを検索
                    for keyword in keywords:
                        if keyword in line.upper():

                            # 一致した場合、結果に追加
                            results.append([file_name, folder_path, keyword, line.strip(), line_number])                                
    except Exception as e:
        raise Exception(f"エラー: {file_path} を読み込む際に問題が発生しました: {e}")

    return results

def write_results_to_csv(results, output_dir,cnt):
    # 結果をCSVファイルに書き出し
    #os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, outputFilename)
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if cnt == 0 :
            writer.writerow(['FileName', 'ParentPath', 'targetWord','line','Funcition','colNum','header/detail']) 
        writer.writerows(results)    

def process_folder(folder_path,file_name, keywords):
    # フォルダ内のファイルを検索して結果を取得
    return search_files_for_keywords_in_folder(folder_path,file_name, keywords)

def main():
    # キーワードリストを直接指定
    keywords = [
        "(+)","CONCAT","CURRENT DATE","CURRENT TIME","CURRENT TIMESTAMP","DATE(","DECODE","DECODE(","FETCH FIRST ","FROM (","HOUR(","INT(","INTEGER","INTEGER(","MINUTE","MINUTE(","NVL","OPTIMIZE FOR ","REPLACE","ROUND","ROWNUM","SUBSTR","TO_CHAR","TO_DATE","TRIM","TRUNC","VALUE(","||"
    ]

    # while(True):
    #     isEnd = input("追加すべき検索キーワードがありますか？(y:n): ")
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
        for dirpath, _, filenames in os.walk(root_dir):
            # サブフォルダごとに処理を開始
            for filename in filenames:
                futures.append(executor.submit(process_folder, dirpath, filename, keywords))                

    cnt = 0
    for future in concurrent.futures.as_completed(futures):
        try:
            results = future.result()

            # 結果をフォルダごとのoutput.csvに書き出し
            if results:
                #output_dir = os.path.join(folder_path, 'output')
                output_dir = f"{crrDir}\\output\\"                                                
                write_results_to_csv(results, output_dir,cnt)
                cnt+=1

        except Exception as e:
            print(f"Error processing folder: {e}")
            SystemExit(1)

    print("すべての検索結果がフォルダごとにoutput.csvに保存されました")
    return outputFilename

if __name__ == '__main__':
    main()
