import json
import requests
import io
import base64
import sys
import argparse
from PIL import Image, PngImagePlugin

def main():
    global payload    
    global allSamples
    global allModels
    global path
    global url
    global fileLocation
    fileLocation = './txt2img/'
    payload = {}    
    allSamples = False
    allModels = False
    path = ''
    url = "http://127.0.0.1:7860"
    samplers = []
    models = []    

    handleArgs()   
    run()
   
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
            
def getSampleList():
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

def call_server_all_Samplers(modelName = None):
    global payload
    global allSamples
    global url
    getModel = requests.get(url=f'{url}/sdapi/v1/options').json()
    print('MODEL: ' + getModel["sd_model_checkpoint"])
    
    imageNamePrefix = ''
    if (modelName != None):
        imageNamePrefix += f'{modelName}-' 
    else:
        imageNamePrefix += prepareModelName(getModel["sd_model_checkpoint"])

    if(allSamples == True):
        sampleList = getSampleList()
        print(f'Cycling through {len(sampleList)} samplers')
        counter = 0
        for s in sampleList:
            imageName = f'{counter}-{imageNamePrefix}{s}-output.png'
            print('Processing: ' + s)
            payload["sampler_name"] = s
            r = call_server_txt2img()               
            processImages([{"name": imageName, "image": r}])    
            counter += 1
    else:
        print(payload.keys())
        print('Single Sampler used: ' + payload["sampler_name"])
        imageName = f'{imageNamePrefix}{payload["sampler_name"]}-output.png'
        r = call_server_txt2img() 
        processImages(processImages([{"name": imageName, "image": r}]))
def call_server_txt2img():
    global url
    global payload
    with open('./data/payload.json', 'w') as f:
        f.write(json.dumps(payload))
    return requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload).json()
def call_server_all_Models():
    # TODO: Update OPtions payload to switch around the Models
    global payload
    global allSamples
    global allModels    
    models = getAllModels()
    imagesToProcess = []
    if (allModels == True):
        print(f'Using total of models {len(models)} used')
        payload["override_settings_restore_afterwards"] = False
        overrideSetting ={}
        overrideSetting["sd_model_checkpoint"] = models[0]

        for m in models:
            print(f'Shifting Model to {m["fullName"]}')
            optionsPayload = {"sd_model_checkpoint": m["fullName"]}
            print(json.dumps(optionsPayload))
            status = requests.post(url=f'{url}/sdapi/v1/options', json=optionsPayload)
            print(status.json())
            call_server_all_Samplers()
            
            
def printImageInfo(image):
    print(image)
    quit()

def handleArgs():  
    global payload
    global allSamples
    allSamples = False
    global allModels
    allModels = False     
    
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to PNG file with Stable Diffusion data")
    parser.add_argument("-m", "--models", help="Use All Models", action="store_true")
    parser.add_argument("-s", "--samplers", help="Use All Samplers", action="store_true")
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
    if args.models:
        allModels = True
        print("Use All Models")
    if args.samplers:
        allSamples = True
        print("Use All Samplers")
    
def run():
    global allSamples
    global allModels
    if (allSamples == True and allModels == False):
        call_server_all_Samplers()
    else:
        call_server_all_Models()


if(__name__ == "__main__"):
    main()
    




