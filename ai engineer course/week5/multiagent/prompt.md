i want to make a multiagent system 
and one single agent system 

in which there is a director/manager LLM
which decides which tool to use and two tools and LLMs , first tool is websearch(using Tavily)and second tool is Calculator( python), 
we are using Groq for our LLM , 

all api keys are stored in .env file (import os, dotenv, Groq)
there will be Maximum attempts of 5

then we will convert this to a multiagent system without langraph

In the multiagent there will be three askllm function
first for director LLM which only  will decide which tool to be used babsed on query
second will be only Websearch llm which uses tavily  search tool the query on web and fetch results
third will be Python Calculator only which solves arithmetic and mathematics part

role of each askllm will be given by a system prompt
Manaer llm will also have a notes file whwere it will store the response outputs of tool LLMs

finally we will have token usage also,
in the end we will compare both the systems and see which uses more tokens

for test prepare a little complex query which involves both tools usage(may be more than once)
if you have any doubt just ask me