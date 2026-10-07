import os
import json
import ast
import operator

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env")


# ============================================================
# CLIENTS
# ============================================================

groq_client = Groq(api_key=GROQ_API_KEY)

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ============================================================
# GROQ MODEL
# ============================================================

MODEL = "openai/gpt-oss-120b"


# ============================================================
# TOOL 1: WEB SEARCH
# ============================================================

def web_search(query: str) -> str:

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = response.get("results", [])

    if not results:
        return "No useful search results found."

    output = []

    for result in results:

        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        output.append(
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content: {content}"
        )

    return "\n\n---\n\n".join(output)


# ============================================================
# TOOL 2: CALCULATOR
# ============================================================

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node):

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):

        if type(node.op) not in allowed_operators:
            raise ValueError("Operator not allowed.")

        left = safe_eval(node.left)
        right = safe_eval(node.right)

        return allowed_operators[type(node.op)](
            left,
            right
        )

    if isinstance(node, ast.UnaryOp):

        if type(node.op) not in allowed_operators:
            raise ValueError("Operator not allowed.")

        operand = safe_eval(node.operand)

        return allowed_operators[type(node.op)](
            operand
        )

    raise ValueError("Invalid mathematical expression.")


def calculate(expression: str) -> str:

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = safe_eval(tree.body)

        return str(result)

    except ZeroDivisionError:

        return "Error: Division by zero."

    except Exception as e:

        return f"Calculation error: {e}"


# ============================================================
# TOOLS OBJECT
# ============================================================

tools = [

    {
        "type": "function",
        "function": {

            "name": "web_search",

            "description": (
                "Search the internet using Tavily. "
                "Use this when the user needs current, "
                "recent, factual, news, research, or "
                "other web-based information."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "query": {
                        "type": "string",
                        "description": "The query to search on the web."
                    }

                },

                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {

            "name": "calculate",

            "description": (
                "Calculate mathematical expressions "
                "such as 2*2, 100/5, or (10+5)*2."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression."
                    }

                },

                "required": ["expression"]
            }
        }
    }

]


# ============================================================
# AVAILABLE FUNCTIONS
# ============================================================

available_functions = {
    "web_search": web_search,
    "calculate": calculate
}


# ============================================================
# AGENT FUNCTION
# ============================================================

def agent(query: str):

    messages = [

        {
            "role": "system",
            "content": (
                "You are a helpful AI agent.\n\n"

                "You have access to two tools:\n"
                "- web_search: search the internet\n"
                "- calculate: perform mathematical calculations\n\n"

                "Use calculate for mathematical calculations.\n"
                "Use web_search when internet information is needed.\n"
                "If no tool is required, answer directly.\n\n"

                "After using a tool, use the tool result "
                "to provide the final answer to the user."
            )
        },

        {
            "role": "user",
            "content": query
        }

    ]


    # --------------------------------------------------------
    # FIRST GROQ CALL
    # --------------------------------------------------------

    response = groq_client.chat.completions.create(

        model=MODEL,

        messages=messages,

        tools=tools,

        tool_choice="auto"

    )

    assistant_message = response.choices[0].message


    # --------------------------------------------------------
    # NO TOOL REQUIRED
    # --------------------------------------------------------

    if not assistant_message.tool_calls:

        return assistant_message.content


    # --------------------------------------------------------
    # ADD TOOL CALL TO MESSAGE HISTORY
    # --------------------------------------------------------

    messages.append(assistant_message)


    # --------------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------------

    for tool_call in assistant_message.tool_calls:

        function_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        function = available_functions.get(
            function_name
        )

        if function is None:

            result = f"Unknown tool: {function_name}"

        else:

            try:

                result = function(**arguments)

            except Exception as e:

                result = f"Tool error: {e}"


        # ----------------------------------------------------
        # ADD TOOL RESULT
        # ----------------------------------------------------

        messages.append(
            {
                "role": "tool",

                "tool_call_id": tool_call.id,

                "name": function_name,

                "content": str(result)
            }
        )


    # --------------------------------------------------------
    # SECOND GROQ CALL
    # --------------------------------------------------------

    final_response = groq_client.chat.completions.create(

        model=MODEL,

        messages=messages,

        tools=tools,

        tool_choice="auto"

    )

    return final_response.choices[0].message.content


# ============================================================
# USER INPUT + OUTPUT
# ============================================================

print("=" * 60)
print("             AI TOOL-CALLING AGENT")
print("=" * 60)
print("Available tools: Web Search + Calculator")
print("Type 'exit' to stop.")
print()


while True:

    query = input("You: ").strip()

    if query.lower() == "exit":
        print("Agent: Goodbye!")
        break

    if not query:
        print("Agent: Please enter a query.")
        continue

    try:

        answer = agent(query)

        print("\nAgent:")
        print(answer)
        print()

    except Exception as e:

        print("\nAgent Error:")
        print(e)
        print()