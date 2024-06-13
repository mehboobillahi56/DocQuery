import pandas as pd
import requests
import json
from random import randrange, choice
import datetime 
import pprint

database_Sim = "txt from db "

userprompt = """
Show me all the vehicles that drove by on the 1st april from 1am to 4am, give me their times
"""

promptrule = """
Make sure you follow the rules stated in the system prompt before answering.
Your output must follow the JSON format given in the system prompt.
"""


finalprompt = f'''
{database_Sim}
with the information from the markdown table above, answer the following question:

{userprompt}
{promptrule}

'''


url = "http://localhost:11434/api/chat"
data = {
    "model": "PDF-sum",
    "temperature": 0.2,
    "messages": [
        {"role": "user", "content": finalprompt,},
    ],
    "stream": False
}



print("User: ", finalprompt)
response = requests.post(url, json=data)
content = res = json.loads(response.text)



print("CyLLM:")
print(content["message"]["content"].replace("<|eot_id|>", ""))


print("-"*60)