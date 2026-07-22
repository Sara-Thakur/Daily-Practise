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

def llm_ans(prompt):
    message={
        "role":"user",
        "content":prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model,messages=messages,max_tokens=50)
    answer=response.choices[0].message.content
    return answer

bad_prompt="""
This is a user complaint:
My laptop not working
classify it"""

good_prompt="""
#ROLE
You are a support assistant at mobile/software compay
#TASK
You have to classify the issue in a category
#CONSTRAINT
Classify the issue in only one of the three categories: technical, return ,billing.
#OUTPUT FORMAT
Give only one word answer. The one word should be one of the categories given in contraints.

This is a user complaint:
My laptop is very costly
 """
# print(llm_ans(bad_prompt))
print(llm_ans(good_prompt))

