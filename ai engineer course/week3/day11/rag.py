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

# step1 Knowledge Base
knowledge_base={
    "age":"The age of khushi is 25 years",
    "education":"Khushi is a btech cse student "
}

# step 2 retrieval
def retrieve_info(question):
    question=question.lower() #lowercase convert
    if "age" in question:
        return knowledge_base["age"]
    elif "education" in question:
        return knowledge_base["education"]
    else:
        return None


def askllm(question):
    context=retrieve_info(question)

    sys_prompt=f"""answer in one line only.Answer only based on this context {context}. Do not hallucinate."""
    system_message={
        "role":"system",
        "content":sys_prompt
    }
    message={
    "role":"user",
    "content":question
    }
    messages=[system_message,message]
    response=client.chat.completions.create(model=model,messages=messages)
    answer=response.choices[0].message.content
    return answer


question="do you know my age."
print(askllm(question))

