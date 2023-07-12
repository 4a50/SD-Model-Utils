import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def Main():
    savedFile = None
    with open('./JSON/saved.json', 'rb') as f:
        savedFile = json.load(f)
    rootURL = savedFile["root_url"]
    fetchedModels = {"root_url": savedFile["root_url"], "site_name": "CivitAi", "models": [] }
    counter = 0
    for model in savedFile["models"]:        
        URL = f'{rootURL}{model["url"]}'        
        page = requests.get(URL)    
        soup = BeautifulSoup(page.content, "html.parser")
        # print(soup.prettify())
        downloadPath = soup.find('a', class_='mantine-zj7kjy')
        print(f'\nCurrent Status of CivitAi Model: {model["name"]}')
        print('-------------------------------')
        print('Index Number: ' + str(counter))        
        if (downloadPath == None):
            nsfw = soup.find('div', class_= 'mantine-ljqvxq')
           
            print(nsfw.text)
            continue        
        href = downloadPath.get('href')
        # pattern = re.compile('Download \(')
        # print(len(soup.find_all('div', string=pattern)))
        dlSoupText = soup.find('div', class_='mantine-11zngbh')
        #                                    'mantine-11zngbh'
        dlSize = getDLSizeFromButton(dlSoupText.text) if (dlSoupText != None) else 'No Data'         
        tableDataValues = soup.find_all('td', class_='mantine-1avyp1d')
        dateUploaded = tableDataValues[2].text if len(tableDataValues) > 1 else 'No Data'
        print(f'Download Link: {str(rootURL) + str(href)}')
        print(f'Download Size: {dlSize}')    
        print(f'Uploaded: {dateUploaded}\n\n')
        fetchedModels["models"].append({
            "name": model["name"],
            "url": model["url"],
            "last_uploaded": dateUploaded,
            "download_size": dlSize,
            "download_link": str(rootURL) + str(href) if dateUploaded != 'No Data' else '**Login Required**',
            "login": False if dateUploaded != 'No Data' else True
        })
        counter += 1
    

def checkUpdateRequired():
    # with open('./JSON/lastUpdated.json', 'r') as f:
    #     lastUpdated = json.load(f)
    with open('./JSON/lastUpdated.json', 'rb') as f:
        savedFile = json.load(f)

    dateSaved = datetime.strptime('Mar 16, 2023', "%b %d, %Y")
    print(dateSaved)
        

def getDLSizeFromButton(text):
    try:
        leftIdx = text.index('(') + 1
        rightIdx = text.index(')')
        return text[leftIdx:rightIdx]

    except:
        print('Parens not found')
def get_URL_List():
    with open('./JSON/saved.json', 'r') as f:
         fileJSON = json.load(f)
    
    return []


Main()
# checkUpdateRequired()

# print(str(allTable))
# print(allTable[2].text)
# print(len(allTable))
