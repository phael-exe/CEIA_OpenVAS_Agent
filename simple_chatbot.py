import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

#Added a test to verify if the OpenAI API key is loaded correctly.
"""if api_key:
    print("OpenAI API key loaded successfully.")
else:
    print("Error: OpenAI API key is not loaded.")"""
    
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    max_completion_tokens=None,
    streaming=True,
    timeout=None,
    api_key=api_key,
    )


class State(TypedDict):
    
    messages: Annotated[list, add_messages]
    
graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_edge("chatbot", END)


