import json
import requests
import io
import base64
import os
import argparse
import inquirer
from datetime import datetime, date, time, timezone
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
    global useEventLog
    useEventLog = True
    fileLocation = './txt2img/'
    payload = {}
    allSamples = False
    allModels = False
    useSelectSamplers = False
    useSelectModels = False
    path = ''
    url = "http://127.0.0.1:3032"
    selectModelList = []
    selectSamplerList = []
    models = getAllModels()    
    print('All Model Names Retrieved')
    print('All Sampler Names Retrieved')
    samplers = getSamplerList()
    handleArgs()
    initLogFile()    
    # Check for txt2Iimg Dir.  Create it doesn't exist

    run()
def initLogFile():    
    newFile = False
    exist = os.path.exists('./data/log.csv')
    print(f'logfile exist: {exist}')
    if not os.path.exists('./data/log.csv'):
        newFile = True
    with open('./data/log.csv', 'a') as logFile:
        if(newFile == True):
            logFile.write('dateTime, event, message\n') 
        
def printOut(evnt, txt):    
    dt = datetime.now()    
    print(txt)
    if(useEventLog == True):
        with open('./data/log.csv', 'a') as logFile:
            logFile.write(f'{dt.strftime("%Y-%m-%d|%H:%M:%S")}, {evnt}, {txt}\n')
        
def checkForDirs():
    dir = "txt2img"
    if not os.path.exists(dir):
        os.makedirs(dir)
        printOut('DIRCHECK', "\"txt2img\" directory created")
    else:
        printOut('DIRCHECK', "\"txt2img\" directory found")
    dir = "data"
    if not os.path.exists(dir):
        os.makedirs(dir)
        printOut('DIRCHECK', "\"data\" directory created")
    else:
        printOut('DIRCHECK', "\"data\" directory found")


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
        if (len(modSplit) > 2):
            outString = ''
            for i in range(len(modSplit) - 1):
                outString += modSplit[i]
            # print(outString)
        else:
            outString = modSplit[0]
        models.append({'fullName': m["title"], 'shortName': outString})

    return models


def getSamplerList():
    samplers = []
    resp = requests.get(f'{url}/sdapi/v1/samplers')
    r = resp.json()
    for i in r:
        samplers.append(i["name"])
    return samplers


def getImageAttribObject(path):
    imgBytes = None

    printOut('STATUS', 'pathToOpen: ' + path)
    with open(path, 'rb') as f:
        imgBytes = f.read()

    base64_string = base64.b64encode(imgBytes).decode('utf-8')

    png_payload = {
        "image": "data:image/png;base64," + base64_string
    }
    resp = requests.post(
        url=f'{url}/sdapi/v1/png-info', json=png_payload).json()

    params = resp["items"]["parameters"]

    propertiesObj = {}
    # Positive and Negative prompts
    infoArr = params.split('\n')
    [print(f'\n{x}\n') for x in infoArr]
    print(f'infoArrLen: {len(infoArr)}')
    if len(infoArr) < 3: attribArr = infoArr[1].split(',')
    else: attribArr = infoArr[2].split(',')
    

    propertiesObj["prompt"] = infoArr[0]
    negPromptLen = len(infoArr[1])
    propertiesObj["negative_prompt"] = infoArr[1][17:negPromptLen]

    # Parse the attributes from response
    for s in attribArr:
        key = s.split(':')[0].strip().lower().replace(' ', '_')
        value = s.split(':')[1].strip()
        if (value.isnumeric() == True):
            value = int(value)
        if (key == 'sampler'):
            propertiesObj["sampler_name"] = value
        if (key == 'size'):
            sizeList = value.split('x')
            propertiesObj['width'] = int(sizeList[0])
            propertiesObj['height'] = int(sizeList[1])
        if (key == 'seed'):
            propertiesObj['seed'] = -1
        else:

            propertiesObj[key] = value
    with open('./data/propertiesObj.json', 'w') as writefile:
        writefile.write(json.dumps(propertiesObj))
    return propertiesObj


def processImages(respJSON):
    global fileLocation
    for resp in respJSON:
        printOut('STATUS', 'Resp: ' + resp["name"])
        for i in resp['image']['images']:
            image = Image.open(io.BytesIO(
                base64.b64decode(i.split(",", 1)[0])))
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(
                url=f'{url}/sdapi/v1/png-info', json=png_payload)
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


def cycleSamplers(modelName=None):
    global payload
    global allSamples
    global samplers
    global selectSamplerList
    global url
    useSamplersList = []
    getModel = requests.get(url=f'{url}/sdapi/v1/options').json()
    printOut('STATUS', 'MODEL: ' + getModel["sd_model_checkpoint"])

    imageNamePrefix = ''
    if (modelName != None):
        imageNamePrefix += f'{modelName}-'
    else:
        imageNamePrefix += prepareModelName(getModel["sd_model_checkpoint"])

    if (allSamples == True):
        useSamplersList = samplers
    elif (useSelectSamplers == True):
        useSamplersList = selectSamplerList
    else:
        printOut('STATUS', 'No curated sampler used')
        useSamplersList.append(payload["sampler_name"])

    printOut('STATUS', f'Cycling through {len(useSamplersList)} samplers')
    counter = 0
    printOut('TIMESTAMP', '>>> Start Sampler Iteration')
    stopwatchStart = datetime.now()
    for s in useSamplersList:
        printOut('VAR', f's: {s}')
        imageName = f'{counter}-{imageNamePrefix}{s}-output.png'
        printOut('STATUS', 'Processing: ' + s)
        payload["sampler_name"] = s
        try:
            r = call_server_txt2img()
            processImages([{"name": imageName, "image": r}])
        except KeyboardInterrupt:
            printOut('ERROR','Keyboard Interrupt')
            quit()
        except:
            printOut('ERROR', f'Error in calling API for Image: {imageName}')
        counter += 1
    printOut('TIMESTAMP', '<<< Completed Sampler Iteration')
    stopwatchStop = datetime.now()
    timedelta = stopwatchStop - stopwatchStart
    printOut("TIMESTAMP", "{} hours, {} minutes, {} seconds".format(timedelta.seconds//3600, (timedelta.seconds//60)%60, timedelta.seconds%60))

def call_server_txt2img():
    global url
    global payload
    with open('./data/payload.json', 'w') as f:
        f.write(json.dumps(payload))
    req = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload).json()
    return req


def checkIfModelInImageExists():
    curModel = payload["model"]
    idx = next((i for i, item in enumerate(models)
               if item["fullName"].startswith(curModel)), None)
    if (idx != None):
        return idx
    return -1


def checkImageModelMatchesCurrentModel():
    resp = requests.get(f'{url}/sdapi/v1/options').json()
    curModel = payload["model"]
    if (resp["sd_model_checkpoint"].startswith(curModel)):
        printOut('STATUS', 'Image model is loaded.')
        return True
    printOut('STATUS', 'Image model is NOT loaded')
    return False


def cycleModels():
    # TODO: Update OPtions payload to switch around the Models
    global payload
    global useSelectModels
    global allSamples
    global allModels
    global models
    useModels = []
    idx = -1
    printOut('STATUS', 
        f'CuratedModels [allSamples: {allSamples}] [allModels: {allModels}] [useSelectModels: {useSelectModels}]')
    if (allModels == True):
        printOut('STATUS', 'Cycling Throug All Models')
        useModels = models
    elif (allModels == False and useSelectModels == True):
        printOut('STATUS', 'Cycling through curated models')
        useModels = selectModelList
    else:
        printOut('STATUS', 'Using model in image')
        idx = checkIfModelInImageExists()
        if (idx != -1):
            printOut('STATUS', 'Image Model Exists')
            useModels.append(models[idx])
        else:
            printOut('ERROR', 'Image Model is not installed/availible. Install as required')
            quit()
    
    
    printOut('STATUS', f'Using total of models {len(useModels)} used')
    modelStringList = []
    for mls in useModels:
        modelStringList.append(mls["shortName"])
    printOut('STATUS', f'Use Models: {json.dumps(modelStringList)}')
    
    printOut('STATUS', useModels)
    lenUseModels = len(useModels)
    printOut('TIMESTAMP', '>>> Start Model Iteration')
    stopwatchStart = datetime.now()
    for m in useModels:
        if(lenUseModels > 1 or checkImageModelMatchesCurrentModel() == False):                              
            printOut('STATUS', f'Shifting Model to {m["fullName"]}')
            optionsPayload = {"sd_model_checkpoint": m["fullName"]}
            printOut('STATUS', json.dumps(optionsPayload))
            status = requests.post(
                url=f'{url}/sdapi/v1/options', json=optionsPayload)
            printOut('STATUS', status.json())
        else:
            printOut('STATUS', 'Image Model is Currently Loaded')
        cycleSamplers()
    printOut('TIMESTAMP', '<<< Completed Model Iteration')
    stopwatchStop = datetime.now()
    timedelta = stopwatchStop - stopwatchStart
    printOut("TIMESTAMP", "{} hours, {} minutes, {} seconds".format(timedelta.seconds//3600, (timedelta.seconds//60)%60, timedelta.seconds%60))



def printImageInfo(image):
    printOut('INFO', image)
    quit()


def handleArgs():
    global payload
    global allSamples
    allSamples = False
    global allModels
    allModels = False
    global useSelectModels
    global useSelectSamplers
    global useEventLog

    parser = argparse.ArgumentParser()
    parser.description = 'Cycles a supplied image through all/selected Models and Samplers'
    parser.epilog = 'No options provided will create an image using data from image'
    parser.add_argument(
        "path", help="Path to PNG file with Stable Diffusion data")
    parser.add_argument("-ma", "--modelsall",
                        help="Use All Models", action="store_true")
    parser.add_argument("-sa", "--samplersall",
                        help="Use All Samplers", action="store_true")
    parser.add_argument("-ss", "--samplerselect",
                        help="Use Only Selected Samplers", action="store_true")
    parser.add_argument("-ms", "--modelsselect",
                        help="Use Only Selected Models", action="store_true")
    parser.add_argument("-nl", "--noeventlog", 
                        help="Do not log events to file", action="store_true")
    args = parser.parse_args()
    if args.noeventlog:
        useEventLog = False
    # -m allModels -s allSamplers arg1 = path to png    
    try:
        payload = getImageAttribObject(args.path)
        payload["restore_faces"] = True
        with open('./data/payload.json', 'w') as f:
            f.write(json.dumps(payload))
    except ConnectionRefusedError:
        printOut('ERROR','Unable to contact SD Server.  Have you started it?')
        quit()
    printOut('STATUS', 'Initial Payload Created')
    if args.modelsall:
        allModels = True
        printOut('STATUS', "Use All Models")
    if args.samplersall:
        allSamples = True
        printOut('STATUS', "Use All Samplers")
    if args.samplerselect:
        allSamples = False
        useSelectSamplers = True
        printOut('STATUS', "Use Curated Samplers")
        selectSamplersToUse()
    if args.modelsselect:
        allModels = False
        useSelectModels = True
        selectModelsToUse()
        printOut('STATUS', "Use Curated Models")
    


def selectSamplersToUse():
    global selectSamplerList
    global samplers

    questions = [inquirer.Checkbox('selectedSamplers',
                                   message="Select Samplers to Use",
                                   choices=samplers)]
    answers = inquirer.prompt(questions)
    for s in answers['selectedSamplers']:
        selectSamplerList.append(s)
    printOut('STATUS', 'Using the following samplers: ')
    printOut('STATUS', selectSamplerList)


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
        idx = next((i for i, item in enumerate(models)
                   if item["shortName"] == ans), None)
        if (idx != None):
            selectModelList.append(models[idx])
    printOut('STATUS', selectModelList)


def run():
    global allSamples
    global allModels
    global useSelectModels
    printOut('STATUS', 
        f'Commence Run [allSamples: {allSamples}] [allModels: {allModels}] [useSelectModels: {useSelectModels}]'
        )
    cycleModels()

if (__name__ == "__main__"):
    main()
