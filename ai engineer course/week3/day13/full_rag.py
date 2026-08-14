# s=input("dfsa")
# print(s)
import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

import numpy as np
from sentence_transformers import SentenceTransformer

knowledge_base=[
    "Employees receive 24 days of paid leave per year.",
"The company supports a work from home policy.",
"Employees are entitled to a monthly stipend of 3000.",
"Office hours are from 9 AM to 6 PM.",
"Health insurance coverage starts after 3 months.",
"Performance reviews are conducted biannually."
]

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key :
    raise ValueError("API Key Kaha h bhai")

client=Groq(api_key=my_api_key)

groqmodel="llama-3.3-70b-versatile"
model=SentenceTransformer("all-MiniLM-L6-v2")#384

def cosine_similarity(a,b):  #how difft are the vectors
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

def retrieve(q):
    score=[]
    for i,document in enumerate(doc_embedding):
        score.append((cosine_similarity(q,document),knowledge_base[i]))
    score.sort(reverse=True)
    return score[0]


def askllm(query,context):

    sys_prompt=f"""answer in one line only.Answer only based on this context {context} acc to the question asked in {query}. Do not hallucinate."""
    system_message={
        "role":"system",
        "content":sys_prompt
    }
    message={
    "role":"user",
    "content":query
    }
    messages=[system_message,message]
    response=client.chat.completions.create(model=groqmodel,messages=messages)
    answer=response.choices[0].message.content
    return answer

doc_embedding=model.encode(knowledge_base)

print(doc_embedding.shape)

query="how much vacation is allowed for employee"
q=model.encode(query)

s,context=retrieve(q)
print(s)
print(context)
print(askllm(query,context))