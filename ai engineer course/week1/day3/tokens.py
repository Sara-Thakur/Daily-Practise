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

#3 prompt
prompt1="hi!"
prompt2="explain whats trending in hiring tech roles!"
prompt3="write a 10 words pick up line"
prompts=[prompt1,prompt2,prompt3]

for prompt in prompts:
    message={
        "role":role,
        "content":prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model,messages=messages,max_tokens=50)
    
    usage=response.usage
    print(f"Prompt:{prompt} -->your tokens:{usage.prompt_tokens} total_tokens:{usage.total_tokens} completion_tokens: {usage.completion_tokens} Finish Reason:{response.choices[0].finish_reason}")
    # prompt=prompt.usage

# prompt="i love flowers.help me make a company brandname"

# message={
#     "role":role,
#     "content":prompt
# }
# messages=[message]
# response=client.chat.completions.create(model=model,messages=messages)
# # print(response)
# print("###################")
# answer=response.choices[0].message.content
# print(answer)
