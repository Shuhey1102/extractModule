import os
import re
import datetime
import csv
import shutil
from concurrent.futures import ProcessPoolExecutor
import concurrent

#current datetime
dt_now = datetime.datetime.now()
crrDir = os.path.dirname(__file__)

baseURL = "C:\\emd-web-struts2.5\\emd-web-struts2.5\\src\\"
#baseURL = "N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\"
importList = []
importList_header = []
importList_detail = []

def load_csv_to_objects(file_path):
    objects = []
    
    # CSVファイルを一括ロード
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # ヘッダーをキーとした辞書形式で各行を取得
        
        # 各行を辞書形式でリストに格納
        for row in reader:
            obj = {}
            for header, value in row.items():
                keys = header.split('.')  # 'object.item1' のようなドット区切りのキーを分割
                current_obj = obj
                for key in keys[:-1]:  # ネストされた辞書を作成
                    if key not in current_obj:
                        current_obj[key] = {}
                    current_obj = current_obj[key]
                current_obj[keys[-1]] = value  # 最後の要素に値を割り当て
            objects.append(obj)
    
    return objects

def load_csv_to_objects_custom(file_path,baseURL):
    objects = []
 
    # CSVファイルを一括ロード
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # ヘッダーをキーとした辞書形式で各行を取得
        
        # 各行を辞書形式でリストに格納
        for row in reader:
            obj = {}
            for header, value in row.items():
                keys = header.split('.')  # 'object.item1' のようなドット区切りのキーを分割
                current_obj = obj
                for key in keys[:-1]:  # ネストされた辞書を作成
                    if key not in current_obj:
                        current_obj[key] = {}
                    current_obj = current_obj[key]

                if header == "fileNameFull":
                    value = value.replace(baseURL,"").replace("\\",".").replace(".java","")

                current_obj[keys[-1]] = value  # 最後の要素に値を割り当て
            objects.append(obj)
    
    return objects


def call(file_path,baseURL):

    # 正規表現パターンをコンパイル

    callFunctions = load_csv_to_objects_custom(file_path,baseURL)
    for callFunc in callFunctions:
        regex = re.compile(f"{callFunc["fileNameFull"]}")
        filtered_data_header = [item for item in importList_header if regex.search(item["line"])]
        for data_header in filtered_data_header:
            filtered_data_detail_col = [item["colNum"] for item in importList_detail if item["FileName"]==data_header["FileName"] and item["ParentPath"]==data_header["ParentPath"] and item["Funcition"]==data_header["Funcition"]]    
            

        #if callFunc["fileNameFull"]

def runParalell(directory_path):

    #runParalell
    with ProcessPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(directory_path):
            if entry.is_dir(): 
                file_path = entry.path+"\\output.csv"
                futures.append(executor.submit(call,file_path, baseURL))

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error processing folder: {e}")    


if __name__ == "__main__":

    # tmpOutput_dir = crrDir + "\\output\\list\\"
    # if os.path.isdir(tmpOutput_dir):
    #     shutil.rmtree(tmpOutput_dir)
    # if not(os.path.isdir(tmpOutput_dir)):    
    #     os.mkdir(tmpOutput_dir)
    #commonRec
    importList = load_csv_to_objects(input("セットする対象ファイルパス:"))
    importList_header = [importItem for importItem in importList if importItem["header/detail"] == "h" ]
    importList_detail = [importItem for importItem in importList if importItem["header/detail"] == "d" ]    
    importList.clear()

    #run('N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\business\\service\\impl',"N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\")
    runParalell(input("プロセスフォルダ:"))
    #runParalell("N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\")
