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
#baseURL = "C:\\New_EQP-Care(Web)\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\"
baseURL = "N:\\New_EQP-Care(Web)\\emd-web-struts2.5\\src\\"

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
    method_partial_pattern = re.compile(
        rf'\b(public|protected|private|static|final|\s)*\s*'  # 修飾子
        rf'(static|final|\s)?\s*'                              # static や final
        rf'(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+'       # 戻り値の型
        rf'(?!{exclude_pattern})\w+\s*'                        # メソッド名。ただし除外キーワードは含めない
        rf'\(.*'                                               # 引数リストの始まり（改行考慮）
    )
    #method_pattern = re.compile(r'\b(public|protected|private|static|final|\s)*\s*(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*\)\s*(throws\s+\w+(\s*,\s*\w+)*)?\s*\{')
    method_pattern = re.compile(
        rf'\b(public|protected|private|static|final|\s)*\s*'  # 修飾子
        rf'(static|final|\s)?\s*'                              # static や final
        rf'(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+'       # 戻り値の型
        rf'(?!{exclude_pattern})\w+\s*'                        # メソッド名。ただし除外キーワードは含めない
        rf'\(.*\)\s*'                                          # 引数リスト
        rf'(throws\s+\w+(\s*,\s*\w+)*)?\s*\{{'                 # throws と本体の開始
    )
    #method_pattern = re.compile(r'\b(public|protected|private|static|final|\s)\s+(static|final|\s)?\s*(\w+(\[\])?|\w+<(\?|(\w+(\s*,\s*\w+)*))>)\s+\w+\s*\(.*\)\s*(throws\s+\w+(\s*,\s*\w+)*)?\s*\{')
    sb_append_pattern = re.compile(r'sb\.append\s*\(.*?[{}].*?\)')
    comment_pattern = re.compile(r'^\s*//')
    
    def __init__(self):
        self.functions = []

    def analyze_file(self, file_path):
        stack = []
        dummy_stack = []
        in_class_scope = False
        in_comment_scope = False
        checkMethod = False
        tmpline_number = 0
        tmpFunction_signature = ""

        with open(file_path, 'r', encoding='utf-8') as file:

            for line_number, line in enumerate(file, 1):
               
                # Class or Interface Detection
                if not (in_class_scope) and self.class_pattern.search(line):
                    in_class_scope = True
                    className = line.strip().split('{')[0].strip()
                    continue                    

                if not(in_comment_scope) and line.strip().startswith("/*") and not(line.strip().endswith("*/")):
                    in_comment_scope = True

                if in_comment_scope and line.strip().endswith("*/"):
                    in_comment_scope = False

                if not(in_comment_scope):
                    # Skip Comment
                    if self.comment_pattern.search(line):
                        continue

                    # skip if "{}" is included in sb.append
                    if self.sb_append_pattern.search(line):
                        continue

                    # Function Detection using `{` split to get function signature
                    if in_class_scope and self.method_pattern.search(line) and not(checkMethod):
                        
                        checkExclude = False
                        function_signature = line.strip().split('{')[0].strip()
                        for key in self.EXCLUDE_KEYWORDS:
                            if key == function_signature.split('(')[0].split()[-1]:
                                checkExclude = True
                                break

                        if checkExclude:
                            continue

                        function_obj = FunctionInfo(file.name,className,function_signature, line_number, None)
                        stack.append(function_obj)

                    elif in_class_scope and self.method_partial_pattern.search(line)  and not(checkMethod):
                        checkMethod=True
                        tmpFunction_signature = line.strip()
                        tmpline_number = line_number
                        continue

                    if checkMethod:
                        if line.strip().endswith("{"):                        
                            function_signature = tmpFunction_signature + line.strip().split('{')[0].strip()
                            function_obj = FunctionInfo(file.name,className,function_signature, tmpline_number, None)
                            stack.append(function_obj)
                            checkMethod=False
                            continue
                        elif line.strip().endswith(";"):
                            checkMethod=False
                            continue
                        else:
                            tmpFunction_signature += line.strip()                        
                    
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

def analyze_java_files_in_directory(directory_path,targetName):
    analyzer = JavaFileAnalyzer()
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                analyzer.analyze_file(file_path)

    output_dir = crrDir + "\\output\\list\\" + targetName    
    os.mkdir(output_dir)

    output_file = output_dir +  "\\output.csv"
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['fileName','class', 'function', 'startNum','endNum','fileNameFull']) 
        for function in analyzer.get_functions():
          writer.writerow([function.FileName,function.className, function.function_name, function.start_line, function.end_line,function.ClassNameFull])
        

    return analyzer.get_functions()
    
def call(directory_path,baseURL):

    targetName=directory_path.replace(baseURL,"").replace("\\","_") 
    
    functions = analyze_java_files_in_directory(directory_path,targetName)
    for func in functions:
        print(func)
    return directory_path

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



    with ProcessPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(directory_path):
            if entry.is_dir(): 
                folder_path = entry.path
                futures.append(executor.submit(call,folder_path, baseURL))                

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
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
