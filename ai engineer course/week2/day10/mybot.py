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


def askllm(sys_prompt,user_prompt):
    message_system={
        "role":"system",
        "content":sys_prompt
    }
    message_user={
        "role":"user",
        "content":user_prompt
    }
    messages=[message_system,message_user]
    streami=client.chat.completions.create(model=model,messages=messages,stream=True)
    # print(streami)
    print("-------------------------------------------")
    for chunk in streami:
        content=chunk.choices[0].delta.content
        if content:
            print(content,end="",flush=True)

def fetch_detail(data):
    sys_prompt=f"""You are my personal honest detail chatbot .when a request comes from user keep in mind that the user is an HR and answer respectfully ,, they will ask question in second person and you should answer in first person.
    you have all information about me in {data}  
    answerv the user based on what they ask in under 50 words with emoji's in chat in front,, 
    also if the given info absent,just do not invent information on your own 
    ,,youu should be honest and answerable .Understand the similar words yourself like, fullname name from the data and question.
    """
    user_prompt="""What is your name?"""
    askllm(sys_prompt,user_prompt)

details_folder=Path("details")
file_path = details_folder / "me.json"
import json

# Open the file using its literal filename
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print(data)

fetch_detail(data)
