import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
# my_project_id=os.getenv("GROQ_PROJECT_ID")

if not my_api_key :
    raise ValueError("API Key Kaha h bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

JD="""
We are hiring a backend python dveloper.

requirements:
-Strong Python
- FastAPI or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

RESUME="""
Name: Samantha Sharma

Experience:
3 years as a software developer

Skills:
Python, FastAPI, MySQL, Docker, REST APIs, Git

Projects:
Built a food delivery backend using FastAPI and MySQL.

Deployed applications using Docker.

"""
def ask_llm(system_prompt,user_prompt):
    system_msg={
        "role":"system",
        "content":system_prompt
    }
    user_msg={
        "role":"user",
        "content":user_prompt
    
    }
    messages=[system_msg,user_msg]
    response=client.chat.completions.create(model=model,messages=messages)
    answer=response.choices[0].message.content
    return answer

def step1 (RESUME):#resume extraction
    print("STEP-1")
    system_prompt="""
    you are a professional HR assistant. 
    Extract the following field(skills,experience,projects) from the resume and return only the skills no other information. do not invent any skills from your side"""
    user_prompt=f"""
    Extract the skills from the {RESUME}"""
    return ask_llm(system_prompt,user_prompt)
    
def step2 ():#job description extract
    print("STEP-2")

    system_prompt="""
    you are a professional HR assistant. 
    Extract the skills from the job description and return only the skills ,no other information. 
    do not invent any skills from your side"""
    user_prompt=f"""
    Extract the skills from the {JD}"""
    return ask_llm(system_prompt,user_prompt)

def step3(candidate,jd):#match
    print("STEP-3")
    
    system_prompt="""
    you are a professional HR assistant.
    compare the skills for candidate and skills require according to skills and produce a final score out of 100
    also produce a short verdict whether the student is a good fit or not."""

    user_prompt=f"""Compare the job description: {jd} and resume of candidiate: {candidate}"""
    return ask_llm(system_prompt,user_prompt)

candidate=step1(RESUME)
print(candidate)
sleep(2)
jd=step2()
print(jd)
sleep(2)
score=step3(candidate,jd)
print(score)