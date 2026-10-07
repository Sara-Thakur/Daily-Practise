import json
import os
import random
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Menu inventory persistent across sessions
MENU = {
    "pizza": 5,
    "burger": 10,
    "pasta": 2,
    "salad": 8,
}


class RestaurantState(TypedDict):
  messages: Annotated[list, add_messages]
  dish_name: str
  required_quantity: int
  available_quantity: str
  status: str
  order_retry_attempts: int
  cook_retry_attempts: int
  serve_retry_attempts: int
  final_result: str


def input_extractor_node(state: RestaurantState):
  messages = state["messages"]
  last_msg = messages[-1]

  # If the last message is from the AI (retry prompt), ask user for new input directly
  if isinstance(last_msg, AIMessage):
    print(f"\n[Agent Prompt]: {last_msg.content}")
    latest_message = input("Your new response: ")
  else:
    latest_message = last_msg.content

  system_prompt = (
      "You are a restaurant order intake AI. "
      "Analyze the user's input. If it is NOT related to ordering food, "
      'reply with JSON format: {"is_food": false}. '
      "If it IS related to ordering food, extract the dish name and required"
      " quantity. "
      'Reply with JSON format: {"is_food": true, "dish": "<dish_name>",'
      ' "quantity": <int>}.'
  )

  try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": latest_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content.strip()

    if content.startswith("```json"):
      content = content.replace("```json", "").replace("```", "").strip()
    elif content.startswith("```"):
      content = content.replace("```", "").strip()

    data = json.loads(content)

    if not data.get("is_food", True):
      ai_msg = AIMessage(
          content="I only take orders, I do not answer to general purpose."
      )
      return {
          "messages": [ai_msg],
          "status": "unrelated",
          "final_result": "Rejected - Unrelated Input",
      }

    dish = data.get("dish", "").lower()
    qty = int(data.get("quantity", 1))
    return {
        "dish_name": dish,
        "required_quantity": qty,
        "status": "extracted",
    }

  except Exception as e:
    print(f"\n[DEBUG] Extractor Error: {e}")
    return {
        "messages": [
            AIMessage(
                content=(
                    "Could you please specify the dish name and quantity"
                    " clearly?"
                )
            )
        ],
        "status": "unrelated",
    }

def order_confirm_node(state: RestaurantState):
  dish = state.get("dish_name", "").lower()
  req_qty = state.get("required_quantity", 0)
  attempts = state.get("order_retry_attempts", 3)

  # Check if dish is not in menu OR quantity is 0 or less
  if dish not in MENU or req_qty <= 0:
    avail_qty = "0"
    status = "unavailable"

    if req_qty <= 0:
      msg_text = (
          f"Quantity must be at least 1. You requested {req_qty} {dish}(s). "
          f"({attempts - 1} retry attempt(s) left)"
      )
    else:
      msg_text = (
          f"Sorry, '{dish}' is not available on our menu. Available quantity:"
          f" 0. ({attempts - 1} retry attempt(s) left)"
      )

    msg = AIMessage(content=msg_text)
    return {
        "available_quantity": avail_qty,
        "status": status,
        "order_retry_attempts": attempts - 1,
        "messages": [msg],
    }

  stock = MENU[dish]
  avail_qty = str(stock)

  if stock >= req_qty:
    status = "confirmed"
    MENU[dish] -= req_qty  # Deduct from menu stock
    msg = AIMessage(
        content=(
            f"Order confirmed! {req_qty} {dish}(s) placed. Remaining stock:"
            f" {MENU[dish]}. Sending to kitchen."
        )
    )
    return {
        "available_quantity": str(MENU[dish]),
        "status": status,
        "messages": [msg],
    }
  elif stock > 0:
    status = "partial"
    msg = AIMessage(
        content=(
            f"Partial availability: We only have {stock} {dish}(s) in stock"
            f" (requested {req_qty}). Would you like to accept {stock} or change"
            f" your order? ({attempts - 1} retry attempt(s) left)"
        )
    )
    return {
        "available_quantity": avail_qty,
        "status": status,
        "order_retry_attempts": attempts - 1,
        "messages": [msg],
    }

def cook_node(state: RestaurantState):
  attempts = state.get("cook_retry_attempts", 2)
  dish = state.get("dish_name")

  # 60% success chance, 40% failure chance
  success = random.random() < 0.60

  if success:
    msg = AIMessage(
        content=f"The kitchen has successfully prepared your {dish}!"
    )
    return {"status": "ready", "messages": [msg]}
  else:
    if attempts > 1:
      msg = AIMessage(
          content=(
              f"Kitchen encountered an issue cooking your {dish}. Retrying..."
              f" ({attempts - 1} cook attempt(s) left)"
          )
      )
      return {
          "status": "cooking_failed",
          "cook_retry_attempts": attempts - 1,
          "messages": [msg],
      }
    else:
      msg = AIMessage(
          content=(
              "We sincerely apologize, but we are unable to prepare your order"
              " due to unexpected kitchen issues."
          )
      )
      return {
          "status": "failed",
          "cook_retry_attempts": 0,
          "final_result": "Failed at Kitchen",
          "messages": [msg],
      }


def serve_node(state: RestaurantState):
  attempts = state.get("serve_retry_attempts", 2)
  dish = state.get("dish_name")

  success = random.random() < 0.80

  if success:
    msg = AIMessage(
        content=(
            f"Your order of {dish} has been successfully served! Enjoy your"
            " meal."
        )
    )
    return {
        "status": "complete",
        "final_result": "Completed Successfully",
        "messages": [msg],
    }
  else:
    if attempts > 1:
      msg = AIMessage(
          content=(
              "There was a minor delay in serving your order. Retrying delivery"
              f" now... ({attempts - 1} serve attempt(s) left)"
          )
      )
      return {
          "status": "serving_failed",
          "serve_retry_attempts": attempts - 1,
          "messages": [msg],
      }
    else:
      msg = AIMessage(
          content=(
              "We apologize, but we encountered repeated delivery issues and"
              " could not serve your order."
          )
      )
      return {
          "status": "failed",
          "serve_retry_attempts": 0,
          "final_result": "Failed at Serving",
          "messages": [msg],
      }


def apology_node(state: RestaurantState):
  msg = AIMessage(
      content=(
          "We are sorry, but after multiple attempts we could not process your"
          " order. Order session ended."
      )
  )
  return {"status": "failed", "final_result": "Max Retries Exceeded", "messages": [msg]}


def route_after_extraction(state: RestaurantState):
  if state.get("status") == "unrelated":
    return END
  return "order_confirm"


def route_after_confirmation(state: RestaurantState):
  status = state.get("status")
  attempts = state.get("order_retry_attempts", 0)

  if status == "confirmed":
    return "cook"
  elif status in ["partial", "unavailable"]:
    if attempts <= 0:
      return "apology"
    return "input_extractor"
  return END


def route_after_cook(state: RestaurantState):
  status = state.get("status")
  if status == "ready":
    return "serve"
  elif status == "cooking_failed":
    return "cook"
  return "apology"


def route_after_serve(state: RestaurantState):
  status = state.get("status")
  if status == "complete":
    return END
  elif status == "serving_failed":
    return "serve"
  return "apology"


workflow = StateGraph(RestaurantState)

workflow.add_node("input_extractor", input_extractor_node)
workflow.add_node("order_confirm", order_confirm_node)
workflow.add_node("cook", cook_node)
workflow.add_node("serve", serve_node)
workflow.add_node("apology", apology_node)

workflow.add_edge(START, "input_extractor")

workflow.add_conditional_edges(
    "input_extractor",
    route_after_extraction,
    {"order_confirm": "order_confirm", END: END},
)

workflow.add_conditional_edges(
    "order_confirm",
    route_after_confirmation,
    {
        "cook": "cook",
        "input_extractor": "input_extractor",
        "apology": "apology",
        END: END,
    },
)

workflow.add_conditional_edges(
    "cook",
    route_after_cook,
    {"serve": "serve", "cook": "cook", "apology": "apology"},
)

workflow.add_conditional_edges(
    "serve",
    route_after_serve,
    {"serve": "serve", "apology": "apology", END: END},
)

workflow.add_edge("apology", END)

app = workflow.compile()

if __name__ == "__main__":
  print("=" * 50)
  print("  WELCOME TO THE LANGGRAPH RESTAURANT AGENT")
  print("=" * 50)

  while True:
    print(f"\n[Current Menu Inventory]: {MENU}")
    user_input = input(
        "\nPlace your order (or type 'exit' / 'quit' to stop):\nYou: "
    )

    if user_input.strip().lower() in ["exit", "quit"]:
      print("Thank you for visiting! Goodbye.")
      break

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "order_retry_attempts": 3,
        "cook_retry_attempts": 2,
        "serve_retry_attempts": 2,
    }

    print("\n--- Processing Order ---")

    for event in app.stream(initial_state, {"recursion_limit": 15}):
      for node_name, node_state in event.items():
        print(f"\n[Node Executed: {node_name}]")
        if "status" in node_state:
          print(f"  Status: {node_state['status']}")
        if "messages" in node_state and node_state["messages"]:
          print(f"  Agent: {node_state['messages'][-1].content}")

    print("\n----------------------------------------")