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
prompt="i love flowers.help me make a company brandname"
msg_system={
    "role":"system",
    "content":"You are my boss"
}
message={
    "role":role,
    "content":prompt
}
messages=[msg_system,message]
response=client.chat.completions.create(model=model,messages=messages,temperature=0.7)
# print(response)
print("###################")
answer=response.choices[0].message.content
print(answer)
