import os 
# from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq


load_dotenv()
QDRANT_URL= os.getenv("QDRANT_URL")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

client=QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)
print("Connected to Qdrant Cloud!")
# my_project_id=os.getenv("GROQ_PROJECT_ID")

# create qdrant collection
COLLECTION_NAME="knowledge"
EMBEDDING_SIZE=384 

# delete collection if already exists
if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection {COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)

# create collection
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,#algorithm for similarity
    )
)
print(f"Collection {COLLECTION_NAME} created successfully!")
print(f"Vector size: {EMBEDDING_SIZE}")
print("Distance: COSINE")


#open knowledge.txt -> make array of the given text lines ->
with open("knowledge.txt","r",encoding="utf-8") as f:
    documents=[
        line.strip() 
        for line in f
        if line.strip()
    ]
print(f"Loaded{len(documents)}documents")


#creating embedding
print("loading embedding model")
model=SentenceTransformer("all-MiniLM-L6-v2")
print("embedding model ready!")
embeddings=model.encode(documents)

print(f"Generated{len(embeddings)}embeddings")
print(f"Embedding size:{len(embeddings[0])}")

#create quadrant points
points=[]
for i,embedding in enumerate(embeddings):
    point=PointStruct(
        id=i+1,
        vector=embedding.tolist(),
        payload={
            "text":documents[i]
        }
    )
    points.append(point)
# print(f"Created{len(points)}points") }

#upload to qdrant
client.upsert(  #upload+insert
    collection_name=COLLECTION_NAME,
    points=points
)

#search qdrant

def search(query,top_k=3):#topk degines how muvh results for thr queru uou want
    query_vector=model.encode(query).tolist()
    results=client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return results

query="How many vacations days do i get?"
results=search(query,top_k=3)
print("\nSearch Results")

for result in results:
    print(f"Score:{result.score:.3f}")
    print(result.payload['text'])
    print()


#connect to groq
# if not my_api_key :
#     raise ValueError("API Key Kaha h bhai")
groq_client = Groq(api_key=GROQ_API_KEY)
# role="system"

def ask_llm(question,context):
    prompt = f"""Answer the question '{question}' only using the information provided in the context below. Do not hallucinate.
    If the answer is not present in the context, say: "I don't know based on the provided info."
    
    Context:
    {context}
    """
    model="groq/compound-mini"
    message={
    "role":"user",
    "content":prompt
    }
    messages=[message]
    response=groq_client.chat.completions.create(model=model,messages=messages)
    return response.choices[0].message.content

# complete rag pipeline
# client=Groq(api_key=my_api_key)

question="How many vacations do i get"
results=search(question,top_k=3)

#extract text from search results
context="\n".join(
    result.payload["text"]
    for result in results
)

answer=ask_llm(question,context)
print("\nAnswer")
print(answer)
# role="user"