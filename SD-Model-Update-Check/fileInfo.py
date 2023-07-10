
import json
import os

from datetime import datetime


from urllib.parse import urlparse
def convertPath(pathName, osType):   

    print(f'{osType}, {os.name}')
    
    if osType == 'nt' and  str(os.name) == 'posix':
        print('converting')
        convertPath = pathName.replace('\\', '/')
        driveLetter = convertPath[convertPath.index(':') - 1]
        startIdx = convertPath.index(':') + 1        
        endIdx = len(convertPath)
        locationPath = convertPath[startIdx:endIdx]
        return f'/mnt/{driveLetter}{locationPath}'
        
    


def getFileInfo():
    with open("settings.json", "r") as f:
        settings = json.load(f)  
    rootPath = convertPath(settings["filePath"], settings['os'])
    print(rootPath)
    
    dirSD = os.path.join(rootPath, "Stable-diffusion")
    dirLora = rootPath + "\\Lora"
    print(f"SD  Path: {dirSD}")
    print(f"LORA Path: {dirSD}")    

    if(os.path.exists(dirSD)): print("SD directory cofirmed")
    else: print('SD directory DNE')
    if(os.path.exists(dirLora)): print("Lora directory cofirmed")
    else: print('Lora directory DNE')

    modelList = []
    for i in os.listdir(dirSD):
        file_path = os.path.join(dirSD, i)
        timestamp = os.path.getmtime(file_path)        
        rawDate = datetime.fromtimestamp(timestamp)
        last_modified = rawDate.strftime("%B %d, %Y")
        modelList.append({"fileName": i, "modified": last_modified })
    # for q in modelList:
        # print(q)
    return modelList

