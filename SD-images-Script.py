import json
import requests
import io
import base64
import os
import argparse
import inquirer
from PIL import Image, PngImagePlugin

def main():
    global payload    
    global allSamples
    global allModels
    global path
    global url
    global fileLocation
    global useSelectModels
    global useSelectSamplers
    global selectModelList
    global selectSamplerList
    global models
    global samplers
    fileLocation = './txt2img/'
    payload = {}    
    allSamples = False
    allModels = False
    useSelectSamplers = False
    useSelectModels = False
    path = ''
    url = "http://127.0.0.1:7860"
    selectModelList = []
    selectSamplerList = []
    models = getAllModels()
    print('All Model Names Retrieved')
    samplers = getSamplerList()
    print('All Sampler Names Retrieved')
    handleArgs()   
    # Check for txt2Iimg Dir.  Create it doesn't exist
    
    run()
def checkForDirs():
    dir = "txt2img"
    if not os.path.exists(dir):
        os.makedirs(dir)
        print("\"txt2img\" directory created")
    else:
        print("\"txt2img\" directory found")
    dir = "data"
    if not os.path.exists(dir):
        os.makedirs(dir)
        print("\"data\" directory created")
    else:
        print("\"data\" directory found")

def getCurrentModel():
    resp = requests.get(f'{url}/sdapi/v1/options')
    r = resp.json()
    return r["sd_model_checkpoint"]

def getAllModels():
    models = []
    resp = requests.get(f'{url}/sdapi/v1/sd-models')
    r = resp.json()
    for m in r:        
        modSplit = m["title"].split('.') 
        modSplitlen = len(modSplit)
        if(len(modSplit) >2):
            outString = ''
            for i in range(len(modSplit) - 1):
                outString += modSplit[i]
            # print(outString)
        else:
            outString = modSplit[0]        
        models.append({'fullName': m["title"], 'shortName': outString})
    
    return  models
            
def getSamplerList():
    samplers = []
    resp = requests.get(f'{url}/sdapi/v1/samplers')
    r = resp.json()   
    for i in r:        
        samplers.append(i["name"])
    return samplers
def getImageAttribObject(path): 
    imgBytes = None     
    
    print('pathToOpen: ' + path)          
    with open(path, 'rb') as f:
        imgBytes = f.read()

    base64_string = base64.b64encode(imgBytes).decode('utf-8')

    png_payload = {
                    "image": "data:image/png;base64," + base64_string
                }
    resp = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload).json()
   
    params = resp["items"]["parameters"]  

    propertiesObj = {}
    # Positive and Negative prompts
    infoArr = params.split('\n')
    attribArr = infoArr[2].split(',')

    propertiesObj["prompt"] = infoArr[0]
    negPromptLen = len(infoArr[1])
    propertiesObj["negative_prompt"] = infoArr[1][17:negPromptLen]

    # Parse the attributes from response
    for s in attribArr:  
        key = s.split(':')[0].strip().lower().replace(' ', '_')
        value = s.split(':')[1].strip()
        if(value.isnumeric() == True):        
            value = int(value)
        if(key == 'sampler'):
            propertiesObj["sampler_name"] = value
        if(key == 'size'):
            sizeList = value.split('x')
            propertiesObj['width'] = int(sizeList[0])
            propertiesObj['height'] = int(sizeList[1])
        else: 
            
            propertiesObj[key] = value    
    with open('./data/propertiesObj.json', 'w') as writefile:
        writefile.write(json.dumps(propertiesObj))        
    return propertiesObj
def processImages(respJSON):
    global fileLocation

    for resp in respJSON:
        print('Resp: ' + resp["name"])
        for i in resp['image']['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))                        
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            image.save(f'{fileLocation}{resp["name"]}', pnginfo=pnginfo) 
def prepareModelName(model):
    modelSplit = model.split('.')    
    splitIdx = len(modelSplit) - 1
    modelSplit.pop(splitIdx)
    finalString = ''
    for s in modelSplit:
        finalString += f'{s}-'
    return finalString

def cycleSamplers(modelName = None):
    global payload
    global allSamples
    global samplers
    global selectSamplerList
    global url
    useSamplersList = []
    getModel = requests.get(url=f'{url}/sdapi/v1/options').json()
    print('MODEL: ' + getModel["sd_model_checkpoint"])
    
    imageNamePrefix = ''
    if (modelName != None):
        imageNamePrefix += f'{modelName}-' 
    else:
        imageNamePrefix += prepareModelName(getModel["sd_model_checkpoint"])

    if(allSamples == True):    
        useSamplersList = samplers
    elif(useSelectSamplers == True):
        useSamplersList = selectSamplerList
    else:
        print('No curated sampler used')
        useSamplersList.append(payload["sampler_name"])

    print(f'Cycling through {len(useSamplersList)} samplers')
    counter = 0
    for s in useSamplersList:
        imageName = f'{counter}-{imageNamePrefix}{s}-output.png'
        print('Processing: ' + s)
        payload["sampler_name"] = s
        try:
            r = call_server_txt2img()               
            processImages([{"name": imageName, "image": r}])    
        except:
            print(f'Error in calling API for Image: {imageName}')
        counter += 1
def call_server_txt2img():
    global url
    global payload
    with open('./data/payload.json', 'w') as f:
        f.write(json.dumps(payload))
    req = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload).json()
    return req
def cycleModels():
    # TODO: Update OPtions payload to switch around the Models
    global payload
    global useSelectModels
    global allSamples
    global allModels    
    global models
    useModels = []
    print(f'CuratedModels [allSamples: {allSamples}] [allModels: {allModels}] [useSelectModels: {useSelectModels}]')
    if (allModels == True):
        print('Cycling Throug All Models')
        useModels = models
    elif(allModels == False and useSelectModels == True):
        print('Cycling through curated models')
        useModels = selectModelList
    print(f'Using total of models {len(useModels)} used')       
    print('Use Models: ')
    print(useModels)
    for m in useModels:
        print(f'Shifting Model to {m["fullName"]}')
        optionsPayload = {"sd_model_checkpoint": m["fullName"]}
        print(json.dumps(optionsPayload))
        status = requests.post(url=f'{url}/sdapi/v1/options', json=optionsPayload)
        print(status.json())
        cycleSamplers()
            
            
def printImageInfo(image):
    print(image)
    quit()

def handleArgs():  
    global payload
    global allSamples
    allSamples = False
    global allModels
    allModels = False
    global useSelectModels     
    global useSelectSamplers
    
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to PNG file with Stable Diffusion data")
    parser.add_argument("-ma", "--modelsall", help="Use All Models", action="store_true")
    parser.add_argument("-sa", "--samplersall", help="Use All Samplers", action="store_true")
    parser.add_argument("-ss", "--samplerselect", help="Use Only Selected Samplers", action="store_true")
    parser.add_argument("-ms", "--modelsselect", help="Use Only Selected Models", action="store_true")
    args = parser.parse_args()
    # -m allModels -s allSamplers arg1 = path to png
    print("Using Path: ", args.path)
    try:
        payload = getImageAttribObject(args.path) 
        with open('./data/payload.json', 'w') as f:
            f.write(json.dumps(payload))  
    except ConnectionRefusedError:
        print('Unable to contact SD Server.  Have you started it?')
        quit()
    print('Initial Payload Created')
    if args.modelsall:
        allModels = True
        print("Use All Models")
    if args.samplersall:
        allSamples = True
        print("Use All Samplers")
    if args.samplerselect:
        allSamples = False
        useSelectSamplers = True
        print("Use Curated Samplers")
        selectSamplersToUse()
    if args.modelsselect:
        allModels = False
        useSelectModels = True
        selectModelsToUse()
        print("Use Curated Models")
def selectSamplersToUse():
    global selectSamplerList
    global samplers

    questions = [inquirer.Checkbox('selectedSamplers',
        message="Select Samplers to Use",
        choices=samplers)]
    answers = inquirer.prompt(questions)
    for s in answers['selectedSamplers']:
        selectSamplerList.append(s)
    print('Using the following samplers: ')
    print(selectSamplerList)
def selectModelsToUse():
    global selectModelList
    global models
    modelShortNameList = []
    for m in models:
        modelShortNameList.append(m["shortName"])

    questions = [inquirer.Checkbox('selectedModels',
        message="Select Models to Use",
        choices=modelShortNameList
        )]
    answers = inquirer.prompt(questions)
    for ans in answers["selectedModels"]:
        idx = next((i for i, item in enumerate(models) if item["shortName"] == ans), None)
        if (idx != None):
            selectModelList.append(models[idx])    
    print(selectModelList)
    
def run():
    global allSamples
    global allModels
    global useSelectModels
    print(f'Commence Run [allSamples: {allSamples}] [allModels: {allModels}] [useSelectModels: {useSelectModels}]')
    if (allSamples == True and allModels == False and useSelectModels == False):
        print('Samplers Only')
        cycleSamplers()
    else:
        print('Sampler and Models')
        cycleModels()


if(__name__ == "__main__"):
    main()
    




