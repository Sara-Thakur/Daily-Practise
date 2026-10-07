import os
import json
import re
import math
import time
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# ---------------------------------------------------------------------------
# 1. Initialization & Configuration
# ---------------------------------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Please set GROQ_API_KEY and TAVILY_API_KEY in your .env file.")

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Active Groq model ID suitable for JSON and reasoning
MODEL_NAME = "openai/gpt-oss-120b"
MAX_ATTEMPTS = 5
NOTES_FILE = "manager_notes.txt"


# ---------------------------------------------------------------------------
# 2. Token & Latency Tracker
# ---------------------------------------------------------------------------
class PerformanceTracker:
    def __init__(self, name: str):
        self.name = name
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.api_calls = 0
        self.total_api_time = 0.0

    def add_usage(self, usage, duration: float):
        if usage:
            self.prompt_tokens += getattr(usage, "prompt_tokens", 0)
            self.completion_tokens += getattr(usage, "completion_tokens", 0)
            self.total_tokens += getattr(usage, "total_tokens", 0)
        self.api_calls += 1
        self.total_api_time += duration

    def print_summary(self, wall_clock_time: float):
        print(f"\n================ {self.name} Performance Summary ================")
        print(f"Total System Runtime  : {wall_clock_time:.2f} seconds")
        print(f"Total API Calls       : {self.api_calls}")
        print(f"Total API Latency     : {self.total_api_time:.2f} seconds")
        if self.api_calls > 0:
            print(f"Avg Time per API Call : {self.total_api_time / self.api_calls:.2f} seconds")
        print(f"Prompt (Input) Tokens : {self.prompt_tokens}")
        print(f"Completion Tokens     : {self.completion_tokens}")
        print(f"Total Tokens Used     : {self.total_tokens}")
        print("=====================================================================\n")


# ---------------------------------------------------------------------------
# 3. Base Tools (Tavily Web Search & Python Calculator)
# ---------------------------------------------------------------------------
def tool_web_search(query: str) -> str:
    """Performs web search using Tavily API and returns context snippets."""
    try:
        response = tavily_client.search(query=query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "No web search results found."
        
        snippets = []
        for idx, res in enumerate(results, 1):
            snippets.append(f"[{idx}] {res.get('title')}: {res.get('content')}")
        return "\n".join(snippets)
    except Exception as e:
        return f"Web Search Error: {str(e)}"


def tool_calculator(expression: str) -> str:
    """Evaluates mathematical expressions safely using Python."""
    allowed_globals = {
        "__builtins__": None,
        "math": math,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
    }
    try:
        clean_expr = expression.strip().strip("`").replace("python", "").strip()
        result = eval(clean_expr, allowed_globals, {})
        return str(result)
    except Exception as e:
        return f"Calculator Execution Error: {str(e)}"


def parse_json_response(text: str) -> dict:
    """Helper to extract JSON objects from model outputs safely."""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except Exception:
        return {}


# ===========================================================================
# SYSTEM 1: SINGLE-AGENT SYSTEM
# ===========================================================================
SINGLE_AGENT_SYSTEM_PROMPT = """You are an Autonomous AI Agent equipped with two tools:
1. 'web_search': Search current facts or data on the internet. Input: search query string.
2. 'calculator': Evaluate mathematical expressions in Python syntax. Input: python expression string (e.g. '38.9 * 10**6 / 2.14').

Respond strictly in valid JSON format matching this exact schema:
{
    "thought": "Step-by-step reasoning on what to do next",
    "action": "web_search" | "calculator" | "FINAL_ANSWER",
    "input": "Query string for web_search OR expression string for calculator OR final answer text"
}
Do NOT include markdown syntax like ```json in your response.
"""

def run_single_agent_system(user_query: str) -> str:
    print("\n--------------------------------------------------")
    print("         RUNNING SINGLE-AGENT SYSTEM             ")
    print("--------------------------------------------------")
    
    tracker = PerformanceTracker("Single-Agent System")
    system_start_time = time.time()

    messages = [
        {"role": "system", "content": SINGLE_AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"User Query: {user_query}"}
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n[Single-Agent Iteration {attempt}/{MAX_ATTEMPTS}] Calling Groq LLM...")
        
        api_start = time.time()
        try:
            response = groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            api_duration = time.time() - api_start
            tracker.add_usage(response.usage, api_duration)
            print(f"--> API Call Time: {api_duration:.2f}s")
        except Exception as e:
            api_duration = time.time() - api_start
            print(f"API Error on attempt {attempt} ({api_duration:.2f}s): {e}")
            messages.append({
                "role": "user",
                "content": "Your previous output failed JSON validation. Please output ONLY valid JSON matching the schema."
            })
            continue

        output_text = response.choices[0].message.content
        parsed = parse_json_response(output_text)
        
        thought = parsed.get("thought", "")
        action = parsed.get("action", "")
        action_input = parsed.get("input", "")
        
        print(f"Thought: {thought}")
        print(f"Action : {action}")
        print(f"Input  : {action_input}")

        if action == "FINAL_ANSWER":
            wall_clock = time.time() - system_start_time
            tracker.print_summary(wall_clock)
            return action_input

        # Tool execution branch
        if action == "web_search":
            observation = tool_web_search(action_input)
        elif action == "calculator":
            observation = tool_calculator(action_input)
        else:
            observation = f"Invalid action specified: '{action}'. Choose 'web_search', 'calculator', or 'FINAL_ANSWER'."

        print(f"Observation: {observation[:200]}...")
        
        # Safely serialize observation string to prevent JSON corruption
        safe_observation = json.dumps(str(observation))

        messages.append({"role": "assistant", "content": output_text})
        messages.append({
            "role": "user", 
            "content": f"Tool Output (Observation):\n{safe_observation}\n\nDecide the next action. Respond STRICTLY in valid JSON."
        })

    wall_clock = time.time() - system_start_time
    tracker.print_summary(wall_clock)
    return "Reached maximum attempts (5) without producing a final answer."


# ===========================================================================
# SYSTEM 2: MULTI-AGENT SYSTEM (NO LANGRAPH)
# ===========================================================================

DIRECTOR_SYSTEM_PROMPT = """You are the Director/Manager LLM coordinating a team to answer complex user requests.
You do NOT execute web searches or mathematical calculations directly. Instead, you delegate tasks to two worker agents:
1. 'WebSearch_Agent': Fetches factual data from the internet.
2. 'Calculator_Agent': Computes exact mathematical expressions using Python.

You have access to a 'Notes' section containing all previous worker outputs.

Respond strictly in JSON format with NO markdown wrapping:
{
    "thought": "Analyze user query against current Notes state to decide next step",
    "next_agent": "WebSearch_Agent" | "Calculator_Agent" | "FINAL_ANSWER",
    "task_instruction": "Specific directive for the selected worker agent (leave empty if FINAL_ANSWER)",
    "final_response": "The complete final answer to the user query (only fill when next_agent is FINAL_ANSWER)"
}
"""

WEBSEARCH_AGENT_SYSTEM_PROMPT = """You are the specialized WebSearch Agent.
Your job is to analyze instructions, format search queries, and synthesize raw web data into concise factual text.

CRITICAL INSTRUCTIONS:
- Do NOT generate native function/tool calls or JSON like {"name": "web.run"}.
- Return ONLY plain text responses.
- When summarizing search results, summarize key facts directly.
"""

CALCULATOR_AGENT_SYSTEM_PROMPT = """You are the specialized Python Calculator Agent.
Your job is to take mathematical instructions and format valid Python math expressions or present calculated results.

CRITICAL INSTRUCTIONS:
- Do NOT generate native function or tool call JSON syntax.
- Return ONLY plain text or executable single-line Python math expressions when requested.
"""

# --- Notes File Management ---
def reset_notes_file():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        f.write("=== DIRECTOR MANAGER NOTES ===\n")

def read_notes_file() -> str:
    if not os.path.exists(NOTES_FILE):
        return ""
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return f.read()

def append_to_notes_file(agent_name: str, task: str, response: str):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n--- Output from {agent_name} ---\n")
        f.write(f"Task Assigned: {task}\n")
        f.write(f"Agent Output : {response}\n")


# --- The Three askllm Functions with Call Timing ---
def ask_director_llm(user_query: str, tracker: PerformanceTracker) -> dict:
    notes_content = read_notes_file()
    prompt = f"Original User Query: {user_query}\n\nCurrent Notes File:\n{notes_content}"
    
    api_start = time.time()
    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    api_duration = time.time() - api_start
    tracker.add_usage(response.usage, api_duration)
    print(f"--> Director API Latency: {api_duration:.2f}s")
    
    return parse_json_response(response.choices[0].message.content)


def ask_websearch_llm(task_instruction: str, tracker: PerformanceTracker) -> str:
    # 1. Query generation call
    agent_prompt = (
        f"Task Directive: {task_instruction}\n\n"
        "Provide ONLY a single line containing the best search query string to find this information. "
        "Do NOT output JSON or function calls."
    )
    api_start1 = time.time()
    res = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": WEBSEARCH_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": agent_prompt}
        ],
        temperature=0.1
    )
    dur1 = time.time() - api_start1
    tracker.add_usage(res.usage, dur1)
    print(f"--> WebSearch Agent Query Gen API Latency: {dur1:.2f}s")
    
    query_str = res.choices[0].message.content.strip().replace('"', '')

    # 2. Tool execution
    search_data = tool_web_search(query_str)

    # 3. Synthesis call
    synthesis_prompt = (
        f"Task Directive: {task_instruction}\n"
        f"Raw Search Results:\n{search_data}\n\n"
        "Summarize the exact facts needed to answer the directive in plain text. Do NOT make tool calls."
    )
    api_start2 = time.time()
    synth_res = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": WEBSEARCH_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": synthesis_prompt}
        ],
        temperature=0.1
    )
    dur2 = time.time() - api_start2
    tracker.add_usage(synth_res.usage, dur2)
    print(f"--> WebSearch Agent Synthesis API Latency: {dur2:.2f}s")
    
    return synth_res.choices[0].message.content


def ask_calculator_llm(task_instruction: str, tracker: PerformanceTracker) -> str:
    # 1. Math extraction call
    prompt = (
        f"Instruction: {task_instruction}\n\n"
        "Extract and return ONLY a valid executable Python math expression (e.g., abs(13960000 - 2161000)**0.5). "
        "Do NOT include explanation, markdown formatting, JSON, or tool calls."
    )
    api_start1 = time.time()
    res = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": CALCULATOR_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    dur1 = time.time() - api_start1
    tracker.add_usage(res.usage, dur1)
    print(f"--> Calculator Agent Expr API Latency: {dur1:.2f}s")

    math_expr = res.choices[0].message.content.strip().strip("`").replace("python", "").strip()

    # 2. Python Tool execution
    calc_result = tool_calculator(math_expr)

    # 3. Output formatting call
    format_prompt = (
        f"Mathematical Directive: {task_instruction}\n"
        f"Python Expression Evaluated: {math_expr}\n"
        f"Raw Calculated Result: {calc_result}\n\n"
        "Provide a clear, plain text summary of this computation result."
    )
    api_start2 = time.time()
    fmt_res = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": CALCULATOR_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": format_prompt}
        ],
        temperature=0.1
    )
    dur2 = time.time() - api_start2
    tracker.add_usage(fmt_res.usage, dur2)
    print(f"--> Calculator Agent Formatting API Latency: {dur2:.2f}s")

    return fmt_res.choices[0].message.content


# --- Multi-Agent Orchestrator ---
def run_multi_agent_system(user_query: str) -> str:
    print("\n--------------------------------------------------")
    print("          RUNNING MULTI-AGENT SYSTEM             ")
    print("--------------------------------------------------")
    
    tracker = PerformanceTracker("Multi-Agent System")
    system_start_time = time.time()
    reset_notes_file()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n[Multi-Agent Step {attempt}/{MAX_ATTEMPTS}] Director LLM Evaluating...")
        
        director_decisions = ask_director_llm(user_query, tracker)
        
        thought = director_decisions.get("thought", "")
        next_agent = director_decisions.get("next_agent", "")
        task_instruction = director_decisions.get("task_instruction", "")
        
        print(f"Director Thought   : {thought}")
        print(f"Delegating To      : {next_agent}")
        print(f"Task Directive     : {task_instruction}")

        if next_agent == "FINAL_ANSWER":
            final_ans = director_decisions.get("final_response", "")
            wall_clock = time.time() - system_start_time
            tracker.print_summary(wall_clock)
            return final_ans

        if next_agent == "WebSearch_Agent":
            print(">>> Invoking WebSearch Agent...")
            worker_output = ask_websearch_llm(task_instruction, tracker)
            append_to_notes_file("WebSearch_Agent", task_instruction, worker_output)
            print(f"WebSearch Result Saved to Notes: {worker_output[:150]}...")

        elif next_agent == "Calculator_Agent":
            print(">>> Invoking Calculator Agent...")
            worker_output = ask_calculator_llm(task_instruction, tracker)
            append_to_notes_file("Calculator_Agent", task_instruction, worker_output)
            print(f"Calculator Result Saved to Notes: {worker_output[:150]}...")

        else:
            err_msg = f"Unknown agent '{next_agent}' requested by Director."
            append_to_notes_file("System_Error", task_instruction, err_msg)

    wall_clock = time.time() - system_start_time
    tracker.print_summary(wall_clock)
    return "Multi-Agent System reached maximum attempts (5) without finishing."


# ---------------------------------------------------------------------------
# 4. Main Benchmark Test Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    TEST_QUERY = (
        "Find the current estimated population of Tokyo and Paris. "
        "Calculate what percentage Tokyo's population is of Paris's population. "
        "Then, compute the square root of the absolute difference between their two populations."
    )

    print("==========================================================")
    print("               AGENT SYSTEM BENCHMARK BENCH               ")
    print("==========================================================")
    print(f"TEST QUERY:\n{TEST_QUERY}\n")

    # Run System 1
    res_single = run_single_agent_system(TEST_QUERY)

    # Run System 2
    res_multi = run_multi_agent_system(TEST_QUERY)

    # Final Summary Comparison
    print("\n==========================================================")
    print("                    FINAL ANSWERS                         ")
    print("==========================================================")
    print(f"\n[Single-Agent Output]:\n{res_single}\n")
    print(f"\n[Multi-Agent Output]:\n{res_multi}\n")