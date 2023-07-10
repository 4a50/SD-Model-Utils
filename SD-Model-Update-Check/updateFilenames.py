from __future__ import print_function, unicode_literals
from fileInfo import getFileInfo
import inquirer
from pprint import pprint
from PyInquirer import prompt, Separator
from examples import custom_style_1
import json
import os

# Get all the file names in the dir.

path_saved = "./JSON/saved.json"
listFileNames = None
listYN = ["No", "Yes", "Quit"]
print("JSON File Exists Here: " + str(os.path.exists(path_saved)))
def getKVP_savedJSON():
    with open(path_saved, 'rb') as f:
        jsonList = json.load(f)    
    jsonKVP = {"dict":{}}
    idx = 0
    for el in jsonList["models"]:
        print(el["filename"])
        if(el["filename"] == None or el["filename"] == "" ):             
            jsonKVP["dict"][str(idx)] = el
        else:
             jsonKVP["dict"][el["filename"]] = el
        idx = idx + 1
    jsonKVP["keys"] = list(jsonKVP["dict"].keys())
    return jsonKVP   
def getFilename_dir():     
    listFileNames = []
    [listFileNames.append(x["fileName"]) for x in getFileInfo()]
    listFileNames.sort()
    listFileNames.insert(0, "None")
    print(f"Files Count: {len(listFileNames)}" )
    return listFileNames

def referenceCode():
    listFileNames = []
    jsonList = {}
    for i in jsonList["models"]:    
        modelName = i["name"]
        
        questions = [inquirer.List('choice',
                                        message=f"Select filename for ** {modelName} **",
                                        choices=listFileNames)]
        answers = inquirer.prompt(questions)
        
        idxvalue = listFileNames.index(answers["choice"])    
        print(f"index: {idxvalue}")
        
        i.update({"filename": answers["choice"]})    
        if (answers["choice"] != "None"): listFileNames.remove(answers["choice"])
        os.system('cls' if os.name == 'nt' else 'clear')
    print(jsonList)
    if (len(listFileNames) > 0): 
        print(f"There are {len(listFileNames)} files remaining")
        [print(x) for x in listFileNames]

    with open(path_saved, 'w', encoding='utf-16') as f:
            json.dump(jsonList, f)

def UpdateJSONEntry(modelObj):
    q = [
                {
                    'type': 'list',
                    'name': 'chooseFile',
                    'message': f'Select Filname from list to update:',
                    'choices': listFileNames
                }
            ]          
    a = prompt.prompt(q, style=custom_style_1)
    ansValue = a['chooseFile']
    print(f'\n**UPDATED** {modelObj["name"]}\'s filename to --> {ansValue} <--\n')
    modelObj["filename"] = ansValue
    return modelObj

     
# Iterate through all of the files, determine if there is an entry for it, of not off to create a new entry by scraping the URL or manually
def Main():
    jsonList = getKVP_savedJSON()
    global listFileNames
    global listYN
    listFileNames = getFilename_dir()
    

    for i in listFileNames:

        # if a key exists
        if i in jsonList["keys"]:
            print('\n\n**********************')
            for k in jsonList['dict'][i].keys():
                value = jsonList['dict'][i][k]
                print(f'{k}: {value}')
            print('**********************\n')
            objName = jsonList['dict'][i]["name"]
            q = [
                {
                    'type': 'list',
                    'name': 'modelEntry',
                    'message': f'Filename {i} matches for model --> {objName} <--.  Do you want to update?',
                    'choices': listYN
                }
            ]                    
            a = prompt.prompt(q, style=custom_style_1)  
            if a["modelEntry"] == 'Yes':                                
                jsonList['dict'][i] = UpdateJSONEntry(jsonList['dict'][i])
            elif a["modelEntry"] == 'Quit':                
                quit()
            else:
                continue
        else:            
            question = [
                {
                    'type': 'confirm',
                    'message': f'{i} does not exist in the file.  Do you want to add a new entry?',
                    'name': 'addNew',
                    'default': True,
                }                
            ]
            answers = prompt.prompt(question, style=custom_style_1)
            if answers['addNew']:
                print(addNewEntry(i))
            else:
                print(f'**NO ENTRY ADDED** --> {i}')
            
def addNewEntry(fileName):
    global listYN
    q = [
                {
                    'type': 'input',
                    'name': 'ModelName',
                    'message': 'Enter Model Name'                    
                },
                {
                    'type': 'input',
                    'name': 'ModelUrl',
                    'message': 'Enter URL'                    
                },
                {
                    'type': 'input',
                    'name': 'ModelName',
                    'message': 'Enter Model Name'                    
                },

            ]                    
    a = prompt.prompt(q, style=custom_style_1)  
    return {
        "name": a['ModelName'],
        "url": a['ModelUrl'],
        "last_uploaded": "",
        "download_size": "",
        "download_link": "",
        "login": False,
        "filename": fileName
        }
        
if __name__ == "__main__":
    Main()


    