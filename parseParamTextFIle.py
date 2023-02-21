import json
import requests
import io
import base64
from io import BytesIO
from PIL import Image, PngImagePlugin
import sys
print('ARGS: ' + str(sys.argv))



def getImageAttribObject():
    url = "http://127.0.0.1:7860"
    with open('./data/sample.png', 'rb') as f:
        imgBytes = f.read()
    base64_string = base64.b64encode(imgBytes).decode('utf-8')

    png_payload = {
                    "image": "data:image/png;base64," + base64_string
                }
    resp = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload).json()
    with open('./data/sample.json', 'w') as writefile:
        writefile.write(json.dumps(resp))
        jsonDump = json.dumps(resp)
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
        # print(f'Key: {key} Value: {value}')
        if(key == 'size'):
            sizeList = value.split('x')
            propertiesObj['width'] = int(sizeList[0])
            propertiesObj['height'] = int(sizeList[1])
        else: 
            propertiesObj[key] = value
    with open('./data/sampleParamsJSON.json', 'w') as f:    
        json.dump(propertiesObj, f)


