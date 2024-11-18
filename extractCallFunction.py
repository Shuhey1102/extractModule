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

#baseURL = "C:\\emd-web-struts2.5\\emd-web-struts2.5\\src\\"
baseURL = "N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\"
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
    
    return (file_path,objects)

# def load_csv_to_objects_custom(file_path,baseURL):
#     objects = []
 
#     # CSVファイルを一括ロード
#     with open(file_path, mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)  # ヘッダーをキーとした辞書形式で各行を取得
        
#         # 各行を辞書形式でリストに格納
#         for row in reader:
#             obj = {}
#             for header, value in row.items():
#                 keys = header.split('.')  # 'object.item1' のようなドット区切りのキーを分割
#                 current_obj = obj
#                 for key in keys[:-1]:  # ネストされた辞書を作成
#                     if key not in current_obj:
#                         current_obj[key] = {}
#                     current_obj = current_obj[key]

#                 #if header == "fileNameFull":
#                 #    value = value.replace(baseURL,"").replace("\\",".").replace(".java","")

#                 current_obj[keys[-1]] = value  # 最後の要素に値を割り当て
#             objects.append(obj)
    
#     return (file_path,objects)


def call(file_path,target,processdict,importList_header,importList_detail):

    #callFunctions = load_csv_to_objects(file_path)

    tmpFileName = ""
    tmpFunctionList = []
    targetProcess = processdict[target]
    for callFunc in targetProcess:
        
        if tmpFileName == callFunc["fileName"]:
            continue
        else:
            tmpFileName = callFunc["fileName"]
            tmpFunctionList = [item["function"] for item in targetProcess if item["fileName"] == callFunc["fileName"]]                    
            
        filtered_data_header = [item for item in importList_header if callFunc["fileNameFull"] == (item["ParentPath"]+"\\"+item["FileName"])]        
        for data_header in filtered_data_header:
            
            #data_header["line"].replace("import").replace(";").strip()

            filtered_data_detail = [item for item in importList_detail 
                                        if item["FileName"]==data_header["FileName"] and item["ParentPath"]==data_header["ParentPath"] and item["Funcition"]==data_header["Funcition"]
                                        and (not(item["line"].startswith("//")) or not(item["line"].startswith("/*")))]     
            
            for data_detail in filtered_data_detail:
                
                function_pattern = "|".join(map(re.escape, tmpFunctionList))
                regex = re.compile(rf"\b(\w+)\.(\w+)\s*\(")      
                match = regex.search(data_detail["line"])
                if match:
                    # マッチしたクラス名と関数名を返す
                    class_name, function_name = match.groups()

            

def runParalell(directory_path,importList_header,importList_detail):

    #runParalell

    processdict={}
    with ProcessPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(directory_path):
            if entry.is_dir(): 
                file_path = entry.path+"\\output.csv"
                futures.append(executor.submit(load_csv_to_objects,file_path))

        for future in concurrent.futures.as_completed(futures):
            try:
                key_raw,value = future.result()
                key = key_raw.replace(directory_path,"").replace("\\",".").replace("_",".")
                processdict[key] = value
            except Exception as e:
                print(f"Error processing folder: {e}") 

    with ProcessPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(directory_path):
            if entry.is_dir(): 
                file_path = entry.path+"\\output.csv"
                target = entry.path.split("\\")[-1].replace("_",".")
                futures.append(executor.submit(call,file_path,target,processdict,importList_header,importList_detail))

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
    importList_header = [importItem for importItem in importList[1] if importItem["header/detail"] == "h" ]
    importList_detail = [importItem for importItem in importList[1] if importItem["header/detail"] == "d" ]    
    importList[1].clear()

    #run('N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\business\\service\\impl',"N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\")
    runParalell(input("プロセスフォルダ:"),importList_header,importList_detail)
    #runParalell("N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\")
