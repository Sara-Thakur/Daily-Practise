import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    response = client.models.list()
    print("Available Models on your Groq Account:")
    for model in response.data:
        print(f" -> {model.id}")
except Exception as e:
    print(f"Error fetching models: {e}")