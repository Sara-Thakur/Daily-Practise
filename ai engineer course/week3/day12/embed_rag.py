import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a,b):  #how difft are the vectors
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

model=SentenceTransformer("all-MiniLM-L6-v2")#384
text="MACHINE LEARNING IS NOTE"

t1="old"
t2="new"
# t1="there is a jam ,so i was late"
# t2="It was much traffic, so i am late"
v1=model.encode(t1)
v2=model.encode(t2)

print(cosine_similarity(v1,v2))
# load_dotenv()=
# model=SentenceTransformer("all-MiniLM-L6-v2")#384
# text="MACHINE LEARNING IS NOTE"
# embedding= model.encode(text)
print(v1.shape)
# print(v1)