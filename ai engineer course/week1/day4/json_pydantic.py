import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
# my_project_id=os.getenv("GROQ_PROJECT_ID")

if not my_api_key :
    raise ValueError("API Key Kaha h bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"

#to specify structure of answer 
from pydantic import BaseModel
class Ticket(BaseModel):
    name:str
    email:str
    issue:str

schema=Ticket.model_json_schema()
response_format={
    "type":"json_object"
}
system_prompt=f""""
Extraxt the personal info from the ticket strictly based on the schema and give a json output {schema} 
"""
message_system={
    "role":"system",
    "content":system_prompt
}

text="hello, my name is khushi khushi@gmail.com.I have purchased an iphone recently which is not working" #any text can be written by the person commenting or giving product review
prompt=f"""" This is a customer ticket.Please extract the answer from this.{text} 
""" #we insert a variable in prompt string ,therefore we write f """
message={
    "role":role,
    "content":prompt
}
messages=[message_system,message]
response=client.chat.completions.create(model=model,messages=messages,response_format=response_format  )
# print(response)
print("###################")
answer=response.choices[0].message.content
print(answer)

import json
raw_json=answer
data_files=json.loads(raw_json)
ticket=Ticket(**data_files)
print(ticket.email)
print(ticket.name)
print(ticket.issue)