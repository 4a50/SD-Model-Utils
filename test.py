import inquirer
questions = [
  inquirer.Checkbox('models',
                    message="What are you interested in?",
                    choices=['Computers', 'Books', 'Science', 'Nature', 'Fantasy', 'History'],
                    ),
]
answers = inquirer.prompt(questions)
print (answers)
dictObj = [
    {"name": "Computers"},
    {"name": "Books"}
]
finalList = []
masterList = ['Computers', 'Books']
for ml in answers['models']: 
    print('ml: ' + ml)   
    a = next((i for i, item in enumerate(dictObj) if item["name"] == ml), None)
    if (a != None):
        finalList.append(a)
print(finalList)
print(dictObj[1])