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
#baseURL = "C:\\New_EQPBatch\\New_EQPBatch\\emdw-batch\\src\\"
baseURL = "C:\\New_EQPBatch\\New_EQPBatch\\emdw-batch\\src\\"
#baseURL = "N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\"

class FunctionInfo:
    def __init__(self,function_Name, function_className ,function_signature, start_line, end_line):
        
        self.FileName = function_Name.split("\\")[-1].replace(".java","")
        self.ClassNameFull = function_Name
        self.className = function_className
        self.function_signature = function_signature
        self.function_name = function_signature.split('(')[0].split()[-1]
        self.arguments = function_signature.split('(')[1].split(')')[0]
        self.function_name_ful = self.function_name + "("+self.arguments+")"
        self.start_line = start_line
        self.end_line = end_line

    def __repr__(self):
        return (f"FileName='{self.FileName}',ClassName='{self.className}',functionName='{self.function_name}', args='({self.arguments})', "
                f"start_line={self.start_line}, end_line={self.end_line},FileNameFull='{self.ClassNameFull}'")

class JavaFileAnalyzer:

    # 除外キーワードのリスト
    EXCLUDE_KEYWORDS = [
        "if", "while", "for", "switch", "catch",  # 制御構文
        "IllegalArgumentException", "RuntimeException", "IllegalStateException","SQLRuntimeException", # 例外
        "ArrayList", "HashMap", "LinkedList",  # クラス名
    ]
    # キーワードを正規表現形式に
    exclude_pattern = r'|'.join(EXCLUDE_KEYWORDS)
    
    class_pattern = re.compile(r'\b(public\s+)?(final\s+)?(class|interface)\s+\w+')
    #method_partial_pattern = re.compile(r'\b(public|protected|private|static|final|\s)*\s*(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*')
    #method_partial_pattern = re.compile(r'\b(public|protected|private|static|final|\s)\s+(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*')
    # method_partial_pattern = re.compile(
    #     rf'^[ \t]*'                                            # 行頭の空白（インデント対応）
    #     rf'(public|protected|private|static|final|\s)*\s*'     # 修飾子
    #     rf'(static|final|\s)?\s*'                              # static や final
    #     rf'(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+'       # 戻り値の型
    #     rf'(?!{exclude_pattern})\w+\s*'                        # メソッド名。ただし除外キーワードは含めない
    #     rf'\([^)]*'  
    # )
    method_partial_pattern = re.compile(r'^[ \t]*(public|protected|private|static|final|\s)*\s*(static|final|\s)?\s*(\w+(\[\])?|\w+<([^<>]*(?:<[^<>]*>[^<>]*)*)>)\s+(?!{exclude_pattern})\w+\s*\([^)]*')

    #method_pattern = re.compile(r'\b(public|protected|private|static|final|\s)\s+(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*\)\s*(throws\s+\w+(\s*,\s*\w+)*)?\s*\{')
    #method_pattern = re.compile(r'\b(public|protected|private|static|final|\s)*\s*(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*\)\s*(throws\s+\w+(\s*,\s*\w+)*)?\s*\{')
    # method_pattern = re.compile(
    #     rf'^[ \t]*'
    #     rf'(public|protected|private|static|final|\s)*\s*'
    #     rf'(static|final|\s)?\s*'
    #     rf'(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+'
    #     rf'(?!{exclude_pattern})\w+\s*'
    #     rf'\([^)]*\)'
    #     rf'(\s*throws\s+\w+(\s*,\s*\w+)*)?'
    #     rf'\s*\{{'
    # )
    method_pattern = re.compile(r'^[ \t]*(public|protected|private|static|final|\s)*\s*(static|final|\s)?\s*(\w+(\[\])?|\w+<([^<>]*(?:<[^<>]*>[^<>]*)*)>)\s+(?!{exclude_pattern})\w+\s*\([^)]*\)(\s*throws\s+\w+(\s*,\s*\w+)*)?\s*\{')

    sb_append_pattern = re.compile(r'sb\.append\s*\(.*?[{}].*?\)')
    comment_pattern = re.compile(r'^\s*//')
    extends_pattern = re.compile(r'extends\s+(\w+)')
    implements_pattern = re.compile(r'implements\s+([\w\s,]+)')
 
    def __init__(self):
        self.functions = []
        self.parent_stack = []

    def analyze_file(self, file_path, parm ,targetFile):
        """
            file_path : file_path for searching
            parm : 0:originalItem / 1 : ExtendsItem
            targetFile : None:originalItem / Except for None:ExtendsItem
        """
        stack = []
        dummy_stack = []
        imports_stack = []
        in_class_scope = False
        in_comment_scope = False
        checkMethod = False
        tmpline_number = 0
        tmpFunction_signature = ""
        checkExclude = False

        with open(file_path, 'r', encoding='utf-8') as file:

            for line_number, line in enumerate(file, 1):
                
                # if file.name == "C:\\New_EQPBatch\\New_EQPBatch\\emdw-batch-kowa-step2\\src\\jp\\co\\komatsu\\emdw\\batch\\KOWAMailBatchInvoker.java":
                # #     # if line_number > 314:
                #         print()
                # else:
                #     continue

                if line.strip().startswith("import"):
                    imports_stack.append(baseURL + line.replace("import","").replace(";","").replace(".","\\").strip()+".java")

                # Class or Interface Detection
                if not (in_class_scope) and self.class_pattern.search(line):
                    in_class_scope = True
                    className = line.strip().split('{')[0].strip()
                    extendsWK = self.extends_pattern.search(line)
                    if extendsWK:
                        extendstmp = extendsWK.group(1).rsplit("throws", 1)[0]
                        extendsFilePath = ""
                        for importsItem in imports_stack:
                            importsItemTmp = importsItem.split("\\")[-1].replace(".java","")                     
                            if importsItemTmp == extendstmp:
                                extendsFilePath = importsItem
                                break

                        if extendsFilePath == '':
                            extendsFilePath = "\\".join(file.name.split("\\")[:-1]) + "\\"+ extendstmp +".java"

                        parent_Folder = '.'.join(file.name.replace(baseURL,"").split("\\")[:5])
                        child_Folder = '.'.join(extendsFilePath.replace(baseURL,"").split("\\")[:5])                                                
                        defaultPath = '.'.join(file.name.replace(baseURL,"").split("\\")[:3])

                        if not(child_Folder.startswith(defaultPath)):
                            continue

                        self.parent_stack.append([file.name,extendsFilePath,parent_Folder,child_Folder])


                    implementsWK = self.implements_pattern.search(line)
                    if implementsWK:
                        implementstmpWkString = implementsWK.group(1).rsplit("throws", 1)[0].strip()
                        implementstmpWkList = implementstmpWkString.split(",")
                       
                        for implementstmp in implementstmpWkList:

                            extendsFilePath = ""
                            for importsItem in imports_stack:
                                importsItemTmp = importsItem.split("\\")[-1].replace(".java","")                   
                                if importsItemTmp == implementstmp.strip():
                                    extendsFilePath = importsItem
                                    break

                            if extendsFilePath == '':
                              extendsFilePath = "\\".join(file.name.split("\\")[:-1]) + "\\" + implementstmp.strip() +".java"

                            parent_Folder = '.'.join(file.name.replace(baseURL,"").split("\\")[:5])
                            child_Folder = '.'.join(extendsFilePath.replace(baseURL,"").split("\\")[:5])
                            defaultPath = '.'.join(file.name.replace(baseURL,"").split("\\")[:2])

                            if not(child_Folder.startswith(defaultPath)):
                                continue

                            self.parent_stack.append([file.name,extendsFilePath,parent_Folder,child_Folder])
                    continue                    

                if not(in_comment_scope) and line.strip().startswith("/*") and not(line.strip().endswith("*/")):
                    in_comment_scope = True

                if in_comment_scope and line.strip().endswith("*/"):
                    in_comment_scope = False
                    continue
            
                if not(in_comment_scope):
                    # Skip Comment
                    if self.comment_pattern.search(line):
                        continue

                    # skip if "{}" is included in sb.append
                    if self.sb_append_pattern.search(line):
                        continue
                    
                    # Function Detection using `{` split to get function signature
                    if in_class_scope and self.method_pattern.search(line) and not(checkMethod):
                        
                        # checkExclude = False
                        function_signature = line.strip().split('{')[0].strip()
                        for key in self.EXCLUDE_KEYWORDS:
                            if key == function_signature.split('(')[0].split()[-1]:
                                checkExclude = True
                                break

                        if checkExclude:
                            checkExclude = False
                            continue

                        function_obj = FunctionInfo(file.name,className,function_signature, line_number, None)
                        stack.append(function_obj)

                    elif in_class_scope and self.method_partial_pattern.search(line)  and not(checkMethod):

                        tmpFunction_signature = line.strip()
                        for key in self.EXCLUDE_KEYWORDS:
                            if key == tmpFunction_signature.split('(')[0].split()[-1]:
                                checkExclude = True
                                break

                        if checkExclude:
                            checkExclude = False
                            continue

                        checkMethod=True
                        checkOpenPath=False
                        checkClosePath=False
                        firstCheck=True
                        tmpline_number = line_number
                        
                    
                    if checkMethod:
                        if line.find("(")!=-1:                        
                            checkOpenPath = True

                        if line.find(")")!=-1:                        
                            checkClosePath = True

                        if line.strip().find("{")!=-1 or line.find(");")!=-1:                        
                            if (checkOpenPath and checkClosePath) and self.method_pattern.search(tmpFunction_signature + ' ' +line.strip()):                                        
                                function_signature = tmpFunction_signature + line.strip().split('{')[0].strip()
                                function_obj = FunctionInfo(file.name,className,function_signature, tmpline_number, None)
                                stack.append(function_obj)
                                checkMethod=False
                                continue                                    

                            else:
                                checkMethod=False
                                tmpFunction_signature = ""
                                
                        if line.strip().endswith(";"):
                            checkMethod=False
                            tmpFunction_signature = ""
                            continue
                        else:
                            if firstCheck:
                                firstCheck=False
                            else:
                                tmpFunction_signature += ' ' + line.strip()                        
                    
                    # Count opening braces `{` in the line                    
                    opening_braces = line.count('{')
                    for _ in range(opening_braces):
                        if in_class_scope and  self.method_pattern.search(line):
                            continue  # メソッドの `{` はすでに処理済み
                        dummy_stack.append('{')

                    # Count closing braces `}` in the line
                    closing_braces = line.count('}')
                    for _ in range(closing_braces):
                        if dummy_stack:
                            dummy_stack.pop()
                        elif stack:
                            function_obj = stack.pop()
                            function_obj.end_line = line_number
                            self.functions.append(function_obj)
                        else:
                            in_class_scope = False  # クラススコープ終了
        
    def get_functions(self):
        return self.functions

    def get_parent_relations(self):
        return self.parent_stack


def analyze_java_files_in_directory(directory_path,targetName):
        
    analyzer = JavaFileAnalyzer()
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                analyzer.analyze_file(file_path,0,None)

    output_dir = crrDir + "\\output\\list\\" + targetName    
    os.mkdir(output_dir)

    output_file = output_dir +  "\\output.csv"
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['fileName','class', 'function', 'startNum','endNum','fileNameFull']) 
        for function in analyzer.get_functions():
          writer.writerow([function.FileName,function.className, function.function_name, function.start_line, function.end_line,function.ClassNameFull])        

    output_file = output_dir +  "\\parents.csv"
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['parent_path','child_path','parent_folder','child_folder']) 
        for function in analyzer.get_parent_relations():
          writer.writerow([function[0],function[1],function[2],function[3]])        

    return analyzer.get_functions()
    
def call(directory_path, baseURL):
    try:
        targetName = directory_path.replace(baseURL, "").replace("\\", "_")
        functions = analyze_java_files_in_directory(directory_path, targetName)
        for func in functions:
            print(func)
        return directory_path
    except Exception as e:
        print(f"Error processing {directory_path}: {e}")
        return None

def runParalell(directory_path):

    # for entry in os.scandir(directory_path):
    #     if entry.is_dir(): 
    #         folder_path = entry.path
    #         if folder_path != "C:\emd-web-struts2.5\emd-web-struts2.5\src\jp\co\komatsu\emdw\common":
    #             continue
    #         call(folder_path, baseURL)                

        # for future in concurrent.futures.as_completed(futures):
        #     try:
        #         result = future.result()
        #     except Exception as e:
        #         print(f"Error processing folder: {e}")    



    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(directory_path):
            if entry.is_dir(): 
                for entry2 in os.scandir(entry.path):
                    if entry2.is_dir(): 
                        folder_path = entry2.path
                        futures.append(executor.submit(call, folder_path, baseURL))  # 非同期タスクを送信                folder_path = entry.path
              
        # 結果を取得
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # 結果を取得し、エラーを処理
            except Exception as e:
                print(f"Error processing folder: {e}")   

if __name__ == "__main__":

    tmpOutput_dir = crrDir + "\\output\\list\\"
    if os.path.isdir(tmpOutput_dir):
        shutil.rmtree(tmpOutput_dir)
    if not(os.path.isdir(tmpOutput_dir)):    
        os.mkdir(tmpOutput_dir)

    #run('N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\business\\service\\impl',"N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\")
    runParalell(input("パスを選択してください:"))
    #runParalell("N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\jp\\co\\komatsu\\emdw\\")
