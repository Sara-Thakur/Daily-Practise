import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from time import sleep
import re

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
# my_project_id=os.getenv("GROQ_PROJECT_ID")

if not my_api_key :
    raise ValueError("API Key Kaha h bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

#tools
def get_product_price(product):
    if product=='iPhone 17':
        return 1000
    elif product=="iPhone 15":
        return 500
    else:
        return 0

def calculator(expression):
    try:
        return eval(expression)
    except:
        return "Invalid Expression"

tools={
    "get_product_price":get_product_price,
    "calculator":calculator
}
system_prompt="""
You are a shopping assistant.

You have these tools:
get_product_price(product)
calculator(expression)

Imp:
Call tools exactly like these examples:
action: get_product_price("iPhone 17")
action: calculator("500-1000")

never write:action: get_product_price(product="iPhone 17")
never write:action: calculator(expression="5000-1000")

follow these rules:
1. decide what  you need to do next.
2. Call only one tool at a time.
3. after writing an action, STOP immediately.
4. Never guess or invent a tool result
5. wait until you receive an observation.
6. then decide your next action.
7. when the task is complete, give the final answer.

format:
thought:what  you need to do
action: tool_name(argument)

when finished:

Final answer: your answer
"""
def run_agent(question):
    messages=[
        {
            "role":"system",
            "content":system_prompt
        },
        {
            "role":"user",
            "content":question
        
        }
    ]
    for step in range(5):
        print("\n----------------")
        print(f"STEP,{step+1}")
        print("----------------")
        response=client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        answer=response.choices[0].message.content
        print(answer)

        #agent finished
        if "Final answer:" in answer:
            break
        
        #find the action
        match=re.search(
            r"action:\s*(\w+)\((.*?)\)",
            answer,re.IGNORECASE)

        if match:
            tool_name=match.group(1)
            tool_input=match.group(2)
            tool_input=tool_input.strip()
            tool_input=tool_input.strip('"')

            #run the tool
            if tool_name in tools:
                tool=tools[tool_name]
                tool_result=tool(tool_input)

            else:
                tool_result="Tool not found"

            print(
                "Tool result: ",
                tool_result
            )
            #add llm response to memory
            messages.append({
                "role":"assistant",
                "content":answer
            })

            #give tool result back to llm
            messages.append({
                "role":"user",
                "content":"Tool result: "+str(tool_result)
            })
            sleep(5)

role="user"
prompt="I have 5000 rupees. What is the price of an iPhone 17? and how much money will I have left"
run_agent(prompt)
# message={
#     "role":role,
#     "content":prompt
# }
# messages=[message]
# print(response)
# print("###################")
# print(answer)