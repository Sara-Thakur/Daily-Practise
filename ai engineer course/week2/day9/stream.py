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
prompt="Explain me how to give a self introduction to a recruiter if you are a btech cse student in only 200 words"
message={
    "role":role,
    "content":prompt
}
messages=[message]
# response=client.chat.completions.create(model=model,messages=messages)
stream=client.chat.completions.create(model=model,messages=messages,stream=True)
# print(response)
# print("###################")
# answer=response.choices[0].message.content
# print(answer)

for chunk in stream:
    content=chunk.choices[0].delta.content
    if content:
        print(content,end="",flush=True)
